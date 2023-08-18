import os
from pathlib import Path
from datetime import date
import pandas as pd
import soccerdata as sd
import numpy as np
from unidecode import unidecode

from infos import PlayerInfos
import playernames as pn
from config import TEAMNAME_REPLACEMENTS, PLAYERNAME_REPLACEMENTS
from utils import get_player_id


class DataframeLoader:
    def __init__(
            self,
            data_dir,
            player_infos: PlayerInfos,
            playing_time_threshold: int = 360
        ):
        self.player_infos = player_infos
        self.playing_time_threshold = playing_time_threshold
        self.fbref = sd.FBref(
            leagues=["Big 5 European Leagues Combined", "BRA-Brasileirao"],
            seasons=["23-24",],
            data_dir=data_dir
        )

    def create_stats_dataframe(
        self, type: str, is_standard: bool = False, is_keeper=False
    ) -> pd.DataFrame:
        renamed = (
            self.fbref.read_player_season_stats(stat_type=type)
            .rename(index=lambda x: TEAMNAME_REPLACEMENTS.get(x, x), level="team")
            .rename(index=lambda x: unidecode(x), level="player")
        )
        renamed.to_excel(f"desired\\auto\\{type}.xlsx")
        without_duplicates = self.remove_duplicates(renamed, is_standard, is_keeper)
        without_duplicates.to_excel(f"desired\\{type}.xlsx")
        return without_duplicates.sort_index()

    player_ids = {}
    playing_times = {}
    duplicated_indexes = []
    duplicated_goalkeeper_indexes = []

    def drop_player(self, index: tuple, is_keeper: bool):
        self.duplicated_indexes.append(index)
        if is_keeper:
            self.duplicated_goalkeeper_indexes.append(index)

    def remove_duplicates(self, dataframe: pd.DataFrame, is_standard=False, is_keeper=False):
        global overrides
        players_registry = {}
        for index, row in dataframe.iterrows():
            if not is_standard:
                overwritten_position = overrides.get(
                    (index[3].lower(), index[1], index[2]), None
                )

                if overwritten_position is not None:
                    row["pos"] = overwritten_position
                    dataframe.loc[index, 'pos'] = overwritten_position
                continue

            name = index[3]
            nation = row["nation"].item()
            born = row["born"].item()
            if name is None or pd.isna(nation) or pd.isna(born):
                self.drop_player(index, is_keeper)
                continue
            birthyear = int(born)

            id = get_player_id(name, nation, birthyear)
            if id is None:
                self.drop_player(index, is_keeper)
                continue

            playing_time = float(row[("Playing Time", "Min")])
            if playing_time is None:
                self.drop_player(index, is_keeper)
                continue
            elif playing_time < self.playing_time_threshold:
                self.drop_player(index, is_keeper)
                continue

            if id not in players_registry:
                self.playing_times[id] = playing_time
                players_registry[id] = index
                continue
            other_playing_time = self.playing_times[id]
            if playing_time > other_playing_time:
                self.drop_player(players_registry[id], is_keeper)
                players_registry[id] = index
                self.playing_times[id] = playing_time
                continue
            self.drop_player(index, is_keeper)

        filtered = (
            dataframe.drop(self.duplicated_indexes)
            if not is_keeper
            else dataframe.drop(self.duplicated_goalkeeper_indexes)
        )
        self.__rename_indexes__(filtered)
        if is_standard:
            nations = set()
            for premier_league_player in self.player_infos.premier_league_players:
                nations.add(premier_league_player["nationality"])

            overrides = self.player_infos.generate_mappings(dataframe, filtered)

            for index, row in filtered.iterrows():
                lower_name = index[3].lower()
                season = index[1]
                club = index[2]
                key_id = (lower_name, season, club)

                overwritten_position = overrides.get(key_id, None)
                if overwritten_position is not None:
                    row["pos"] = overwritten_position
                    filtered.loc[index, 'pos'] = overwritten_position
                self.player_ids[
                    get_player_id(
                        index[3], row["nation"].item(), row["born"].item()
                    )
                ] = (index, row)

        return filtered
    
    def __rename_indexes__(self, dataframe: pd.DataFrame):
        dataframe.index = dataframe.index.map(lambda x: self.__rename_index__(x))
    
    def __rename_index__(self, index: tuple):
        key_id = (index[3].lower(), index[1], index[2])
        overwritten_name = pn.PLAYERNAME_REPLACEMENTS.get(key_id, None)
        if overwritten_name is not None:
            return (index[0], index[1], index[2], unidecode(overwritten_name))
        return index

    def remove_plus_signal(self, dataframe: pd.DataFrame, column):
        pass

    def create_grouped_column(self, dataframe: pd.DataFrame, group: str, column, new_column_name: str):
        dataframe[column] = dataframe[column].fillna(0)
        dataframe[column] = pd.to_numeric(dataframe[column])

        if isinstance(column, tuple):
            dataframe[new_column_name] = dataframe[[column]] / dataframe.groupby(level=group)[[column]].sum() * 100
        elif isinstance(column, str):
            dataframe[new_column_name] = dataframe[column] / dataframe.groupby(level=group)[column].sum() * 100
        else:
            raise TypeError("Column must be a tuple or a string")

    def create_proportional_column(
        self, dataframe: pd.DataFrame, name: str, numerator: tuple, denominator: tuple
    ):
        dataframe[numerator] = pd.to_numeric(dataframe[numerator])
        dataframe[denominator] = pd.to_numeric(dataframe[denominator])
        dataframe[name] = dataframe[numerator] / dataframe[denominator]
        dataframe.replace([np.inf, -np.inf], np.nan, inplace=True)

    def get_player_by_id(self, id: str):
        return self.player_ids.get(id, None)

    def create_per_90s_column(
        self, dataframe: pd.DataFrame, name: str, column: tuple, ninetiesColumn="90s"
    ):
        self.create_proportional_column(dataframe, f"{name}/90", column, ninetiesColumn)

    def clear(self):
        self.duplicated_indexes = []
        self.duplicated_goalkeeper_indexes = []
        self.playing_times = {}
