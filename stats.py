import pandas as pd

from utils import get_player_id;
import numpy as np
import time

class Stats:
    attribute_map = {}

    def __init__(
        self,
        standard: pd.DataFrame,
        shooting: pd.DataFrame,
        passing: pd.DataFrame,
        passing_types: pd.DataFrame,
        goal_shot_creation: pd.DataFrame,
        defense: pd.DataFrame,
        possession: pd.DataFrame,
        misc: pd.DataFrame,
        keeper: pd.DataFrame,
        keeper_advanced: pd.DataFrame,
    ):
        self.standard = standard
        self.shooting = shooting
        self.passing = passing
        self.passing_types = passing_types
        self.goal_shot_creation = goal_shot_creation
        self.defense = defense
        self.possession = possession
        self.misc = misc
        self.keeper = keeper
        self.keeper_advanced = keeper_advanced
        self.forwards_radar_shooting_data = [
            "shooting_clinicality",
            "shooting_chances",
            "shooting_tendency",
            "shooting_threat"
        ]
        self.forwards_radar_playmaking_data = [
            "goal_creating_tendency",
            "shot_creating_tendency",
            "goal_creating_passes",
            "goal_creating_dribbles",
            "expected_assists"
        ]
        self.forwards_radar_possession_data = [
            "taking_on_tendency",
            "taking_on_ability",
            "taking_on_consistency",
            "carrying_tendency",
            "carrying_progressiveness",
            "penalty_area_carries",
            "final_third_carries"
        ]
        self.forwards_radar_passing_data = [
            "directness",
            "key_passes",
            "through_balls",
            "final_third_passes",
            "crossing_tendency",
            "long_range_passes",
        ]
        self.forwards_radar_defending_data = ["defensive_actions", "aerial_reliability"]
        # ------------------------
        self.midfielders_radar_shooting_data = ["shooting_clinicality", "shooting_tendency", "shooting_threat"]
        self.midfielders_radar_playmaking_data = [
            "shot_creating_actions",
            "shot_creating_tendency",
            "shot_creating_passes",
            "shot_creating_dribbles",
            "expected_assisted_shots"
        ]
        self.midfielders_radar_possession_data = [
            "taking_on_tendency",
            "taking_on_ability",
            "carrying_tendency",
            "progressive_carries",
            "carrying_progressiveness",
            "final_third_carries",
            "penalty_area_carries",
            "defensive_third_touches",
            "attacking_third_touches",
        ]
        self.midfielders_radar_passing_data = [
            "directness",
            "key_passes",
            "progressive_passes",
            "final_third_passes",
            "long_range_passes",
        ]
        self.midfielders_radar_defending_data = [
            "challenging_tendency",
            "defensive_actions",
            "recoveries",
            "aerial_reliability",
            "interceptions",
            "defensive_third_tackles",
            "mid_third_tackles",
            "attacking_third_tackles",
        ]
        # ------------------------
        self.defenders_radar_playmaking_data = [
            "shot_creating_defensive_actions",
        ]
        self.defenders_radar_possession_data = [
            "taking_on_tendency",
            "taking_on_ability",
            "carrying_tendency",
            "carrying_progressiveness",
            "touches_per_90",
            "mid_third_touches",
        ]
        self.defenders_radar_passing_data = [
            "passes_per_90",
            "medium_range_passes",
            "medium_range_pass_accuracy",
            "long_range_passes",
            "long_range_pass_accuracy",
            "through_balls",
            "switching_tendency",
            "directness",
            "progressive_passes"
        ]
        self.defenders_radar_defending_data = [
            "challenging_tendency",
            "challenging_consistency",
            "defensive_actions",
            "defensive_third_tackles",
            "mid_third_tackles",
            "recoveries",
            "aerial_prowess",
            "aerial_reliability",
            "clearances",
            "shots_blocked",
            "passes_blocked",
            "interceptions",
        ]
        # ------------------------
        self.overall_goalkeeping_radar_data = [
            "penalty_saving",
            "clean_sheet_consistency",
        ]
        self.shot_stopping_radar_data = [
            "shot_stopping_total",
            "shot_stopping_per_90",
            "shot_quality_faced",
            "shots_against_per_90",
        ]
        self.distribution_radar_data = [
            "total_passes",
            "passing_distance",
            "short_range_passes",
            "short_range_pass_accuracy",
            "medium_range_passes",
            "medium_range_pass_accuracy",
            "long_range_passes",
            "long_range_pass_accuracy",
            "launching_consistency",
            "goalkicks_distance",
        ]
        self.sweeping_radar_data = [
            "crosses_stopped",
            "crosses_stopping_tendency",
            "sweeping_actions",
            "sweeping_tendency",
            "sweeping_distance",
            "carrying_total_distance",
            "carrying_tendency",
            "defensive_third_touches",
            "mid_third_touches"
        ]
        # ------------------------
        self.shooting_attributes = {
            "shooting_tendency": (self.shooting, ("Standard", "Sh/90"), False),
            "shooting_threat": (self.shooting, ("Standard", "G/Sh"), False),
            "shooting_chances": (self.shooting, ("Expected", "npxG/Sh"), False),
            "shooting_consistency": (self.shooting, ("Standard", "SoT%"), False),
            "shooting_clinicality": (self.shooting, ("Expected", "np:G-xG"), False),
            "shooting_distance": (self.shooting, ("Standard", "Dist"), False)
        }
        self.playmaking_attributes = {
            "shot_creating_actions": (self.goal_shot_creation, ("SCA", "SCA"), False),
            "shot_creating_tendency": (self.goal_shot_creation, ("SCA", "SCA90"), False),
            "shot_creating_passes": (self.goal_shot_creation, ("SCA Types", "PassLive"), False),
            "shot_creating_setpieces": (self.goal_shot_creation, ("SCA Types", "PassDead"), False),
            "shot_creating_dribbles": (self.goal_shot_creation, ("SCA Types", "TO"), False),
            "shot_creating_defensive_actions": (self.goal_shot_creation, ("SCA Types", "Def"), False),
            "goal_creating_actions": (self.goal_shot_creation, ("GCA", "GCA"), False),
            "goal_creating_tendency": (self.goal_shot_creation, ("GCA", "GCA90"), False),
            "goal_creating_passes": (self.goal_shot_creation, ("GCA Types", "PassLive"), False),
            "goal_creating_setpieces": (self.goal_shot_creation, ("GCA Types", "PassDead"), False),
            "goal_creating_dribbles": (self.goal_shot_creation, ("GCA Types", "TO"), False),
            "goal_creating_defensive_actions": (self.goal_shot_creation, ("GCA Types", "Def"), False),
            "expected_assists": (self.passing, "xAG", False),
            "expected_assisted_shots": (self.passing, "xA", False),
            "forwards_clinicality": (self.passing, "A-xAG", False)
        }
        self.possession_attributes = {
            "taking_on_tendency": (self.possession, "Take-ons/90", False),
            "taking_on_ability": (self.possession, "Successful Take-Ons/90", False),
            "taking_on_consistency": (self.possession, ("Take-Ons", "Succ%"), False),
            "carrying_tendency": (self.possession, "Carries/90", False),
            "progressive_carries": (self.possession, ("Carries", "PrgC"), False),
            "carrying_progressiveness": (self.possession, "Carries Progressiveness/90", False),
            "final_third_carries": (self.possession, ("Carries", "1/3"), False),
            "penalty_area_carries": (self.possession, ("Carries", "CPA"), False),
            "carrying_total_distance": (self.possession, ("Carries", "TotDist"), False),
            "touches_per_90": (self.possession, "Touches/90", False),
            "received_passes": (self.possession, ("Receiving", "Rec"), False),
            "received_progressive_passes": (self.possession, ("Receiving", "PrgR"), False),
            "possession_trustworthiness": (self.possession, ("Carries", "Dis"), True),
            "defensive_third_touches": (self.possession, ("Touches", "Def 3rd"), False),
            "mid_third_touches": (self.possession, ("Touches", "Mid 3rd"), False),
            "attacking_third_touches": (self.possession, ("Touches", "Att 3rd"), False)
        }
        self.passing_attributes = {
            "directness": (self.passing, "Pass Directness %", False),
            "passes_per_90": (self.passing, "Passes Completed/90", False),
            "accuracy": (self.passing, ("Total", "Cmp%"), False),
            "key_passes": (self.passing, "KP", False),
            "progressive_passes": (self.passing, "PrgP", False),
            "final_third_passes": (self.passing, "1/3", False),
            "through_balls": (self.passing_types, ("Pass Types", "TB"), False),
            "switching_tendency": (self.passing_types, "Sw/90", False),
            "crossing_tendency": (self.passing_types, "Crosses/90", False),
            "short_range_passes": (self.passing, ("Short", "Cmp"), False),
            "short_range_pass_accuracy": (self.passing, ("Short", "Cmp%"), False),
            "medium_range_passes": (self.passing, ("Medium", "Cmp"), False),
            "medium_range_pass_accuracy": (self.passing, ("Medium", "Cmp%"), False),
            "long_range_passes": (self.passing, ("Long", "Cmp"), False),
            "long_range_pass_accuracy": (self.passing, ("Long", "Cmp%"), False),
        }
        self.defending_attributes = {
            "challenging_tendency": (self.defense, "Challenges/90", False),
            "challenging_consistency": (self.defense, ("Challenges", "Tkl%"), False),
            "defensive_actions": (self.defense, "Tkl+Int", False),
            "defensive_third_tackles": (self.defense, ("Tackles", "Def 3rd"), False),
            "mid_third_tackles": (self.defense, ("Tackles", "Mid 3rd"), False),
            "attacking_third_tackles": (self.defense, ("Tackles", "Att 3rd"), False),
            "teams_tackling_contribution": (self.defense, 'Team Tackles', False),
            "teams_defensive_contribution": (self.defense, 'Team Tackles', False),
            "recoveries": (self.misc, ("Performance", "Recov"), False),
            "aerial_reliability": (self.misc, "Aerial Duels Won/90", False),
            "aerial_prowess": (self.misc, ("Aerial Duels", "Won%"), False),
            "clearances": (self.defense, "Clr", False),
            "shots_blocked": (self.defense, ("Blocks", "Sh"), False),
            "passes_blocked": (self.defense, ("Blocks", "Pass"), False),
            "interceptions": (self.defense, "Int", False),
            "yellow_cards": (self.misc, ("Performance", "CrdY"), False),
            "fouling_tendency": (self.misc, "Fouls/90", False)
        }
        self.overall_goalkeeping_attributes = {
            "goals_against_per_90": (self.keeper_advanced, "GA/90", True),
            "penalty_saving": (self.keeper, ("Penalty Kicks", "Save%"), False),
            "freekick_saving": (self.keeper_advanced, "FK/90", True),
            "corners_saving": (self.keeper_advanced, "CK/90", True),
            "clean_sheet_consistency": (self.keeper, ("Performance", "CS%"), False)
        }
        self.shot_stopping_attributes = {
            "shot_stopping_total": (self.keeper_advanced, ("Expected", "PSxG+/-"), False),
            "shot_stopping_per_90": (self.keeper_advanced, ("Expected", "/90"), False),
            "shot_quality_faced": (self.keeper_advanced, ("Expected", "PSxG/SoT"), False),
            "shots_against": (self.keeper, ("Performance", "SoTA"), False),
            "shots_against_per_90": (self.keeper, "SoTA/90", False),
        }
        self.distribution_attributes = {
            "total_passes": (self.keeper_advanced, ("Passes", "Att"), False),
            "passing_distance": (self.keeper_advanced, ("Passes", "AvgLen"), False),
            "short_range_passes": (self.passing, ("Short", "Cmp"), False),
            "short_range_pass_accuracy": (self.passing, ("Short", "Cmp%"), False),
            "medium_range_passes": (self.passing, ("Medium", "Cmp"), False),
            "medium_range_pass_accuracy": (self.passing, ("Medium", "Cmp%"), False),
            "long_range_passes": (self.passing, ("Long", "Cmp"), False),
            "long_range_pass_accuracy": (self.passing, ("Long", "Cmp%"), False),
            "expected_assists": (self.passing, "xA", False),
            "launching_consistency": (self.keeper_advanced, ("Launched", "Cmp%"), False),
            "launching_tendency": (self.keeper_advanced, ("Passes", "Launch%"), False),
            "goalkicks_launching_tendency": (self.keeper_advanced, ("Goal Kicks", "Launch%"), False),
            "goalkicks_distance": (self.keeper_advanced, ("Goal Kicks", "AvgLen"), False)
        }
        self.sweeping_attributes = {
            "crosses_stopped": (self.keeper_advanced, ("Crosses", "Stp"), False),
            "crosses_stopping_tendency": (self.keeper_advanced, ("Crosses", "Stp%"), False),
            "sweeping_actions": (self.keeper_advanced, ("Sweeper", "#OPA"), False),
            "sweeping_tendency": (self.keeper_advanced, ("Sweeper", "#OPA/90"), False),
            "sweeping_distance": (self.keeper_advanced, ("Sweeper", "AvgDist"), False),
            "carrying_total_distance": (self.possession, ("Carries", "TotDist"), False),
            "carrying_tendency": (self.possession, "Carries/90", False),
            "defensive_third_touches": (self.possession, ("Touches", "Def 3rd"), False),
            "mid_third_touches": (self.possession, ("Touches", "Mid 3rd"), False),
        }

    filtered_dataframe_cache = {}
    def filter_dataframe(self, dataframe: pd.DataFrame, player_index: tuple, league: str, position: str) -> pd.DataFrame:
        cached_value = self.filtered_dataframe_cache.get(self.get_dataframe_name(dataframe), None)
        if cached_value is not None:
            return cached_value
        filtered = dataframe
        filtered = self.filter_by_league(filtered, player_index, league)
        filtered = self.filter_by_position(filtered, player_index, position)
        self.filtered_dataframe_cache[self.get_dataframe_name(dataframe), player_index, league, position] = filtered
        return filtered
    
    parent_positions = {
        "FW": ["ST", "W"],
        "DF": ["CB", "FB"]
    }
    def get_parent_position(self, position: str) -> str:
        if position == "ST" or position == "W":
            return "FW"
        elif position == "CB" or position == "FB":
            return "DF"
        else:
            return position

    def filter_by_position(self, dataframe: pd.DataFrame, player_index: tuple, position: str) -> pd.DataFrame:
        filtered = dataframe
        if position != "GK":
            player_position = dataframe.loc[player_index, "pos"]
            if player_position == position:
                filtered = dataframe[dataframe["pos"] == position]
            elif position in self.parent_positions:
                children_positions = self.parent_positions[position]
                filtered = dataframe[(dataframe.index == player_index) | dataframe["pos"].isin(children_positions)]
            elif position in player_position:
                filtered = dataframe[dataframe["pos"].str.contains(position)]
            else:
                filtered = dataframe[(dataframe.index == player_index) | (dataframe['pos'] == position)]
        else:
            filtered = dataframe[dataframe["pos"] == position]
        return filtered

    def filter_by_league(self, dataframe: pd.DataFrame, player_index: tuple, league: str) -> pd.DataFrame:
        if len(player_index) == 3 or league == player_index[0]:
            return dataframe.loc[league, :, :, :]
        elif league == "Top 5 European Leagues":
            return dataframe[(dataframe.index == player_index) | dataframe.index.get_level_values('league').isin(self.top_5_european_leagues)]
        else:
            return dataframe[(dataframe.index == player_index) | (dataframe.index.get_level_values('league') == league)]

    def multiple_filter_dataframe(self, dataframe: pd.DataFrame, indexes: tuple, league: str, position: str) -> pd.DataFrame:
        filtered = self.multiple_filter_by_league(dataframe, indexes, league)
        filtered = self.multiple_filter_by_position(filtered, indexes, position)
        return filtered

    def multiple_filter_by_position(self, dataframe: pd.DataFrame, indexes: tuple, position: str) -> pd.DataFrame:
        filtered = dataframe
        if position != "GK":
            if position in self.parent_positions:
                children_positions = self.parent_positions[position]
                filtered = dataframe[(dataframe.index.isin(indexes)) | dataframe["pos"].isin(children_positions)]
            else:
                filtered = dataframe[(dataframe.index.isin(indexes)) | (dataframe['pos'] == position)]
        else:
            filtered = dataframe[dataframe["pos"] == position]
        return filtered

    def multiple_filter_by_league(self, dataframe: pd.DataFrame, indexes: tuple, league: str) -> pd.DataFrame:
        if league == "Top 5 European Leagues":
            return dataframe[(dataframe.index.isin(indexes)) | dataframe.index.get_level_values('league').isin(self.top_5_european_leagues)]
        else:
            return dataframe[(dataframe.index.isin(indexes)) | (dataframe.index.get_level_values('league') == league)]

    def get_player_data(self, player_index: tuple, league: str, position: str):
        data = {}
        dataframe_cache = {}
        if position == "GK":
            data["overall"] = self.compile_data(self.overall_goalkeeping_attributes, player_index, league, position, dataframe_cache)
            data["shot-stopping"] = self.compile_data(self.shot_stopping_attributes, player_index, league, position, dataframe_cache)
            data["distribution"] = self.compile_data(self.distribution_attributes, player_index, league, position, dataframe_cache)
            data["sweeping"] = self.compile_data(self.sweeping_attributes, player_index, league, position, dataframe_cache)
        else:
            data["shooting"] = self.compile_data(self.shooting_attributes, player_index, league, position, dataframe_cache)
            data["playmaking"] = self.compile_data(self.playmaking_attributes, player_index, league, position, dataframe_cache)
            data["possession"] = self.compile_data(self.possession_attributes, player_index, league, position, dataframe_cache)
            data["passing"] = self.compile_data(self.passing_attributes, player_index, league, position, dataframe_cache)
            data["defending"] = self.compile_data(self.defending_attributes, player_index, league, position, dataframe_cache)
        return data

    def compile_data(self, data_map: dict, player_index: tuple, league: str, position: str, dataframe_cache):
        data = {}
        if league == player_index[0]:
            player_index = player_index[1:]
        for attribute, (dataframe, column, ascending) in data_map.items():
            filtered = dataframe_cache.get(self.get_dataframe_name(dataframe), None)
            if filtered is None:
                filtered = self.filter_dataframe(dataframe, player_index, league, position)
                dataframe_cache[self.get_dataframe_name(dataframe)] = filtered
            data[attribute] = self.get_attribute_and_compare(filtered, player_index, column, ascending=ascending)
        return data

    top_5_european_leagues = ["ESP-La Liga", "ENG-Premier League", "ITA-Serie A", "GER-Bundesliga", "FRA-Ligue 1"]
    def get_player_statistic_rank(self, player_index: tuple, league: str, position: str, stat_type: str, stat: str):
        map = self.get_map_by_stat_type(stat_type)
        dataframe: pd.DataFrame = map[stat][0]
        column: tuple = map[stat][1]
        ascending = map[stat][2]

        if player_index[0] == league:
            player_index = player_index[1:]
        filtered = self.filter_dataframe(dataframe, player_index, league, position)

        filtered_ranking = filtered.copy()
        filtered_ranking[column] = pd.to_numeric(filtered_ranking[column])
        if ascending:
            filtered_ranking = filtered_ranking.nsmallest(3, column, "first")
        else:
            filtered_ranking = filtered_ranking.nlargest(3, column, "first")

        zipped = zip(filtered_ranking.index, filtered_ranking[column])
        data = {
            "total": filtered.shape[0]
        }
        data["ranking"] = []
        is_player_in_ranking = False
        for rank, (index, value) in enumerate(zipped):
            if index == player_index:
                is_player_in_ranking = True
            player_name = index[-1]
            player_nation = filtered_ranking.loc[index, "nation"]
            player_born = int(filtered_ranking.loc[index, "born"])
            
            player_id = get_player_id(player_name, player_nation, player_born)

            player_entry = {
                "id": player_id,
                "name": player_name,
                "nation": player_nation,
                "born": player_born,
                "rank": rank+1,
                "value": float(value)
            }
            data["ranking"].append(player_entry)
        if not is_player_in_ranking:
            filtered_dataframe = filtered.copy()
            filtered_dataframe[column] = pd.to_numeric(filtered_dataframe[column])
            filtered_dataframe["rank"] = filtered_dataframe[column].rank(
                ascending=ascending, method="min", na_option="bottom"
            )
            rank = filtered_dataframe.loc[player_index, "rank"]
            player_name = player_index[-1]
            player_nation = filtered_dataframe.loc[player_index, "nation"]
            player_born = int(filtered_dataframe.loc[player_index, "born"])

            player_id = get_player_id(player_name, player_nation, player_born)

            data["ranking"].append({
                "id": player_id,
                "name": player_name,
                "nation": player_nation,
                "born": player_born,
                "rank": int(rank),
                "value": float(filtered_dataframe.loc[player_index, column])
            })
        return data

    def create_radar_data_for_comparison(self, indexes: list, ids: list, league: str, position: str):
        standard = self.multiple_filter_dataframe(self.standard, indexes, league, position)
        filtered_cache = { "standard": standard }
        data = { "players": {} }
        for (id, player_index) in zip(ids, indexes):
            data["players"][id] = {
                "name": player_index[3],
                "nation": standard.loc[player_index, "nation"],
                "club": player_index[2],
                "values": {}
            }

        parent_position = self.get_parent_position(position)
        if parent_position == "FW":
            self.assemble_radar_comparison_data(indexes, league, position, data, self.shooting_attributes, self.forwards_radar_shooting_data, filtered_cache)
            self.assemble_radar_comparison_data(indexes, league, position, data, self.playmaking_attributes, self.forwards_radar_playmaking_data, filtered_cache)
            self.assemble_radar_comparison_data(indexes, league, position, data, self.possession_attributes, self.forwards_radar_possession_data, filtered_cache)
            self.assemble_radar_comparison_data(indexes, league, position, data, self.passing_attributes, self.forwards_radar_passing_data, filtered_cache)
            self.assemble_radar_comparison_data(indexes, league, position, data, self.defending_attributes, self.forwards_radar_defending_data, filtered_cache)
        elif parent_position == "MF":
            self.assemble_radar_comparison_data(indexes, league, position, data, self.shooting_attributes, self.midfielders_radar_shooting_data, filtered_cache)
            self.assemble_radar_comparison_data(indexes, league, position, data, self.playmaking_attributes, self.midfielders_radar_playmaking_data, filtered_cache)
            self.assemble_radar_comparison_data(indexes, league, position, data, self.possession_attributes, self.midfielders_radar_possession_data, filtered_cache)
            self.assemble_radar_comparison_data(indexes, league, position, data, self.passing_attributes, self.midfielders_radar_passing_data, filtered_cache)
            self.assemble_radar_comparison_data(indexes, league, position, data, self.defending_attributes, self.midfielders_radar_defending_data, filtered_cache)
        elif parent_position == "DF":
            self.assemble_radar_comparison_data(indexes, league, position, data, self.playmaking_attributes, self.defenders_radar_playmaking_data, filtered_cache)
            self.assemble_radar_comparison_data(indexes, league, position, data, self.possession_attributes, self.defenders_radar_possession_data, filtered_cache)
            self.assemble_radar_comparison_data(indexes, league, position, data, self.passing_attributes, self.defenders_radar_passing_data, filtered_cache)
            self.assemble_radar_comparison_data(indexes, league, position, data, self.defending_attributes, self.defenders_radar_defending_data, filtered_cache)
        elif parent_position == "GK":
            self.assemble_radar_comparison_data(indexes, league, position, data, self.overall_goalkeeping_attributes, self.overall_goalkeeping_radar_data, filtered_cache)
            self.assemble_radar_comparison_data(indexes, league, position, data, self.shot_stopping_attributes, self.shot_stopping_radar_data, filtered_cache)
            self.assemble_radar_comparison_data(indexes, league, position, data, self.distribution_attributes, self.distribution_radar_data, filtered_cache)
            self.assemble_radar_comparison_data(indexes, league, position, data, self.sweeping_attributes, self.sweeping_radar_data, filtered_cache)
        return data
    
    def assemble_radar_comparison_data(self, indexes: tuple, league: str, position: str, data, attribute_map, desired_attributes, filtered_cache):
        for attribute_name in desired_attributes:
            (dataframe, column, ascending) = attribute_map[attribute_name]

            cached_value = filtered_cache.get(self.get_dataframe_name(dataframe), None)
            if cached_value is not None:
                filtered = cached_value
            else:
                filtered = self.multiple_filter_dataframe(dataframe, indexes, league, position)
                filtered_cache[self.get_dataframe_name(dataframe)] = filtered

            for index in indexes:
                filtered = filtered.copy()
                player_value = self.get_attribute_and_compare(filtered, index, column, ascending=ascending)
                player_nationality = filtered.loc[index, "nation"]
                player_born = int(filtered.loc[index, "born"])

                player_id = get_player_id(index[3], player_nationality, player_born)
                player_data = data["players"][player_id]["values"]

                player_data[attribute_name] = float(player_value)

    def create_radar_data(self, player_index: tuple, league: str, position: str, rating_type: str):
        data = { "values": [] }
        filtered_cache = {}
        parent_position = self.get_parent_position(position)
        if parent_position == "FW":
            self.assemble_radar_data(player_index, league, position, data, rating_type, self.shooting_attributes, self.forwards_radar_shooting_data, filtered_cache)
            self.assemble_radar_data(player_index, league, position, data, rating_type, self.playmaking_attributes, self.forwards_radar_playmaking_data, filtered_cache)
            self.assemble_radar_data(player_index, league, position, data, rating_type, self.possession_attributes, self.forwards_radar_possession_data, filtered_cache)
            self.assemble_radar_data(player_index, league, position, data, rating_type, self.passing_attributes, self.forwards_radar_passing_data, filtered_cache)
            self.assemble_radar_data(player_index, league, position, data, rating_type, self.defending_attributes, self.forwards_radar_defending_data, filtered_cache)
        elif parent_position == "MF":
            self.assemble_radar_data(player_index, league, position, data, rating_type, self.shooting_attributes, self.midfielders_radar_shooting_data, filtered_cache)
            self.assemble_radar_data(player_index, league, position, data, rating_type, self.playmaking_attributes, self.midfielders_radar_playmaking_data, filtered_cache)
            self.assemble_radar_data(player_index, league, position, data, rating_type, self.possession_attributes, self.midfielders_radar_possession_data, filtered_cache)
            self.assemble_radar_data(player_index, league, position, data, rating_type, self.passing_attributes, self.midfielders_radar_passing_data, filtered_cache)
            self.assemble_radar_data(player_index, league, position, data, rating_type, self.defending_attributes, self.midfielders_radar_defending_data, filtered_cache)
        elif parent_position == "DF":
            self.assemble_radar_data(player_index, league, position, data, rating_type, self.playmaking_attributes, self.defenders_radar_playmaking_data, filtered_cache)
            self.assemble_radar_data(player_index, league, position, data, rating_type, self.possession_attributes, self.defenders_radar_possession_data, filtered_cache)
            self.assemble_radar_data(player_index, league, position, data, rating_type, self.passing_attributes, self.defenders_radar_passing_data, filtered_cache)
            self.assemble_radar_data(player_index, league, position, data, rating_type, self.defending_attributes, self.defenders_radar_defending_data, filtered_cache)
        elif parent_position == "GK":
            self.assemble_radar_data(player_index, league, position, data, rating_type, self.overall_goalkeeping_attributes, self.overall_goalkeeping_radar_data, filtered_cache)
            self.assemble_radar_data(player_index, league, position, data, rating_type, self.shot_stopping_attributes, self.shot_stopping_radar_data, filtered_cache)
            self.assemble_radar_data(player_index, league, position, data, rating_type, self.distribution_attributes, self.distribution_radar_data, filtered_cache)
            self.assemble_radar_data(player_index, league, position, data, rating_type, self.sweeping_attributes, self.sweeping_radar_data, filtered_cache)
        return data

    def assemble_radar_data(self, player_index: tuple, league: str, position: str, data, rating_type: str, attribute_map, desired_attributes, filtered_cache):
        if player_index[0] == league:
            player_index = player_index[1:]
        for attribute_name in desired_attributes:
            (dataframe, column, ascending) = attribute_map[attribute_name]
            player_value = 0

            cached_value = filtered_cache.get(self.get_dataframe_name(dataframe), None)
            if cached_value is not None:
                filtered = cached_value
            else:
                filtered = self.filter_dataframe(dataframe, player_index, league, position)
                filtered_cache[self.get_dataframe_name(dataframe)] = filtered

            if rating_type != "absolute":
                filtered = filtered.copy()
                player_value = self.get_attribute_and_compare(filtered, player_index, column, ascending=ascending)
                data["values"].append({
                    "type": attribute_name,
                    "value": float(player_value)
                })
            else:
                filtered[column] = pd.to_numeric(filtered[column])
                player_value = filtered.loc[player_index, column]
                if np.isnan(np.sum(player_value)):
                    player_value = 0
                best_value = filtered[column].max()
                average_value = filtered[column].mean()
                data["values"].append({
                    "type": attribute_name,
                    "value": float(player_value),
                    "average": float(average_value),
                    "best": float(best_value)
                })

    def get_attribute_and_compare(
        self,
        dataframe: pd.DataFrame,
        index: tuple,
        column,
        ascending=False,
    ) -> float:
        dataframe[column] = pd.to_numeric(dataframe[column])
        dataframe["rank"] = dataframe[column].rank(
            ascending=ascending, method="max", na_option="bottom"
        )
        rank = dataframe.loc[index, "rank"]
        total = dataframe.shape[0]
        return float((total - rank + 1) / total * 100)

    def get_map_by_stat_type(self, stat_type):
        if stat_type == "shooting":
            return self.shooting_attributes
        elif stat_type == "playmaking":
            return self.playmaking_attributes
        elif stat_type == "possession":
            return self.possession_attributes
        elif stat_type == "passing":
            return self.passing_attributes
        elif stat_type == "defending":
            return self.defending_attributes
        elif stat_type == "overall":
            return self.overall_goalkeeping_attributes
        elif stat_type == "shot-stopping":
            return self.shot_stopping_attributes
        elif stat_type == "distribution":
            return self.distribution_attributes
        elif stat_type == "sweeping":
            return self.sweeping_attributes

    def get_dataframe_name(self, dataframe):
        if dataframe is self.standard:
            return "standard"
        if dataframe is self.shooting:
            return "shooting"
        elif dataframe is self.passing:
            return "passing"
        elif dataframe is self.passing_types:
            return "passing_types"
        elif dataframe is self.goal_shot_creation:
            return "goal_shot_creation"
        elif dataframe is self.defense:
            return "defending"
        elif dataframe is self.possession:
            return "possession"
        elif dataframe is self.misc:
            return "misc"
        elif dataframe is self.keeper:
            return "keeper"
        elif dataframe is self.keeper_advanced:
            return "keeper_advanced"