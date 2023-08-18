import os
import requests
from unidecode import unidecode
import json
import pandas as pd
from utils import get_player_id
from playernames import PLAYERNAME_REPLACEMENTS


class PlayerInfos:
    def __init__(self, data_dir, cache: bool, playing_time_threshold: int, store_cache: bool):
        self.data_dir = data_dir
        self.association_map = {}
        self.cache = cache
        self.playing_time_threshold = playing_time_threshold
        self.store_cahe = store_cache
        self.premier_league_players = []

    def load_players(self, season: str, league_id: int):
        cached_file = f"{self.data_dir}/{league_id}-{season}.json"
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
        if self.cache:
            if os.path.exists(cached_file):
                with open(cached_file, "r") as f:
                    self.premier_league_players = json.loads(f.read())
                return

        response = requests.get(
            f"https://www.footballcritic.com/json/competition-player-stats.php?uid={league_id}"
        )
        data = response.json()[0]
        for player in data:
            minutes = int(player["17"])
            if self.playing_time_threshold > minutes:
                continue

            name = unidecode(player["2"].strip())
            club = self.translate_club(player["5"])
            translated_name = unidecode(
                PLAYERNAME_REPLACEMENTS.get((name.lower(), season, club), name)
            ).lower()

            self.premier_league_players.append(
                {
                    "name": translated_name,
                    "club": self.translate_club(player["5"]),
                    "position": player["86"],
                    "season": season,
                    "base_id": int(player["14"]),
                    "has_image": not 'no_player' in player["4"],
                    "nationality": player["3"]
                }
            )
        if self.store_cahe:
            with open(cached_file, "w") as f:
                f.write(json.dumps(self.premier_league_players))

    def load_all_players(self):
        self.load_players("2324", 68731)  # Premier League 2324
        self.load_players("2324", 68733)  # La Liga 2324
        # self.load_players("2324", 68734)  # Serie A 2324
        self.load_players("2324", 68727)  # Ligue 1 2324
        # self.load_players("2324", 68723)  # Bundesliga 2324
        self.load_players("2324", 68014)  # Brasileirão 23

    def translate_position(self, position: str):
        if position == "Goalkeeper":
            return "GK"
        elif position == "Defender":
            return "CB"
        elif position == "Full back":
            return "FB"
        elif position == "Defensive midfielder":
            return "MF"
        elif position == "Midfielder":
            return "MF"
        elif position == "Attacking midfielder":
            return "MF, FW"
        elif position == "Winger":
            return "W"
        elif position == "Striker":
            return "ST"
        else:
            raise ValueError(f"Unknown position: {position}")

    club_translations = {
        "Notts Forest": "Nottingham Forest",
        "Leeds Utd": "Leeds United",
        "Man Utd": "Manchester United",
        "Man City": "Manchester City",
        "Newcastle": "Newcastle United",
        "Paranaense": "Athletico Paranaense",
        "Bragantino": "RB Bragantino",
        "América": "América-MG",
        "Cuiabá EC": "Cuiabá",
        "Mineiro": "Atlético-MG",
        "Dortmund": "Borussia Dortmund",
        "Bayern": "Bayern Munich",
        "Schalke": "Schalke 04",
        "Mainz": "Mainz 05",
        "Hertha": "Hertha BSC",
        "M'gladbach": "Borussia M'Gladbach",
        "Frankfurt": "Eintracht Frankfurt",
        "W. Bremen": "Werder Bremen",
        "Clermont": "Clermont Foot",
        "PSG": "Paris SG",
        "Rennais": "Rennes",
        "Verona": "Hellas Verona",
        "Valladolid": "Real Valladolid",
        "Atletico Madrid": "Atlético Madrid",
        "Celta": "Celta Vigo",
        "Athletic": "Athletic Club",
    }

    def translate_club(self, club: str):
        return self.club_translations.get(club, club)

    def generate_mappings(self, dataframe: pd.DataFrame, filtered: pd.DataFrame):
        entire_dataframe_players = {}
        for player_index, player_row in dataframe.iterrows():
            name = player_index[3]
            club = player_index[2]
            season = player_index[1]
            position = player_row["pos"].item()
            if pd.isna(position):
                continue
            entire_dataframe_players[name.lower(), season, club] = player_row
        filtered_database_players = {}
        for player_index, player_row in filtered.iterrows():
            name = player_index[3]
            club = player_index[2]
            season = player_index[1]
            position = player_row["pos"].item()
            filtered_database_players[name.lower(), season, club] = player_row

        overwritten_positions = {}
        unknown = 0
        discarded = 0
        for pl_player in self.premier_league_players:
            name = pl_player["name"]
            club = pl_player["club"]
            position = pl_player["position"]
            season = pl_player["season"]
            id = name, season, club

            equivalent_dataframe_player_row = filtered_database_players.get(id, None)

            if equivalent_dataframe_player_row is None:
                if id in entire_dataframe_players:
                    discarded += 1
                else:
                    unknown += 1
                    print(f"Unknown player {unidecode(name)} {id}")
                continue

            equivalent_dataframe_player_position = equivalent_dataframe_player_row[
                "pos"
            ].item()

            translated_position = self.translate_position(position)
            if equivalent_dataframe_player_position != translated_position:
                overwritten_positions[id] = translated_position

            nationality = equivalent_dataframe_player_row["nation"].item()
            birthyear = int(equivalent_dataframe_player_row["born"].item())
            player_id = get_player_id(name, nation=nationality, born=birthyear)
            self.association_map[player_id] = pl_player

        print(
            f"Overwritten the position of {len(overwritten_positions)} players."
        )
        print(
            f"Loaded {len(self.association_map)} players, lost {unknown} players and discarded {discarded} players."
        )
        return overwritten_positions

    def get_player_info(self, player_id: str):
        return self.association_map.get(player_id, None)

    def get_player_info_or_empty(self, player_id: str):
        info = self.association_map.get(player_id, None)
        if info is None:
            return {
                "base_id": 4194304,
                "has_image": False
            }
        return info