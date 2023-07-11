import pandas as pd

from utils import get_player_id;

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
            "goal_creating_defensive_actions": (self.goal_shot_creation, ("GCA Types", "Def"), False)
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
            "short_range_passes": (self.passing, ("Short", "Cmp"), False),
            "short_range_pass_accuracy": (self.passing, ("Short", "Cmp%"), False),
            "medium_range_passes": (self.passing, ("Medium", "Cmp"), False),
            "medium_range_pass_accuracy": (self.passing, ("Medium", "Cmp%"), False),
            "long_range_passes": (self.passing, ("Long", "Cmp"), False),
            "long_range_pass_accuracy": (self.passing, ("Long", "Cmp%"), False),
            "expected_assists": (self.passing, "xAG", False),
            "expected_assisted_shots": (self.passing, "xA", False),
            "forwards_clinicality": (self.passing, "A-xAG", False)
        }
        self.defending_attributes = {
            "challenging_tendency": (self.defense, "Challenges/90", False),
            "challenging_consistency": (self.defense, ("Challenges", "Tkl%"), False),
            "defensive_actions": (self.defense, "Tkl+Int", False),
            "defensive_third_tackles": (self.defense, ("Tackles", "Def 3rd"), False),
            "mid_third_tackles": (self.defense, ("Tackles", "Mid 3rd"), False),
            "attacking_third_tackles": (self.defense, ("Tackles", "Att 3rd"), False),
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
            "team_defensive_prowess": (self.keeper_advanced, "GA/90", True),
            "penalty_saving": (self.keeper, ("Penalty Kicks", "Save%"), True),
            "freekick_saving": (self.keeper_advanced, "FK/90", True),
            "corners_saving": (self.keeper_advanced, "CK/90", True),
            "clean_sheet_consistency": (self.keeper, ("Performance", "CS%"), False)
        }
        self.shot_stopping_attributes = {
            "shot_stopping_total": (self.keeper_advanced, ("Expected", "PSxG+/-"), False),
            "shot_stopping_per_90": (self.keeper_advanced, ("Expected", "/90"), False),
            "shot_quality_faced": (self.keeper_advanced, ("Expected", "PSxG/SoT"), False),
            "shot_stopping_consistency": (self.keeper_advanced, ("Expected", "PSxG+/-"), False),
            "shots_against": (self.keeper, ("Performance", "SoTA"), False),
            "shots_against_per_90": (self.keeper, "SoTA/90", False),
        }
        self.distribution_attributes = {
            "total_passes": (self.keeper_advanced, ("Passes", "Att"), False),
            "passing_distance": (self.keeper_advanced, ("Passes", "AvgLen"), False),
            "launching_consistency": (self.keeper_advanced, ("Launched", "Cmp%"), False),
            "launching_tendency": (self.keeper_advanced, ("Passes", "Launch%"), False),
            "goalkicks_launching_tendency": (self.keeper_advanced, ("Goal Kicks", "Launch%"), False),
            "goalkicks_distance": (self.keeper_advanced, ("Goal Kicks", "AvgLen"), False)
        }
        self.sweeping_attributes = {
            "crosses_stopping_tendency": (self.keeper_advanced, ("Crosses", "Stp%"), False),
            "sweeping_actions": (self.keeper_advanced, ("Sweeper", "#OPA"), False),
            "sweeping_tendency": (self.keeper_advanced, ("Sweeper", "#OPA/90"), False)
        }


    def get_player_data(self, player_index: tuple, position: str, stat_type: str):
        return self.compile_data(self.getMapByStatType(stat_type), player_index, position)

    def compile_data(self, map: dict, player_index: tuple, position: str):
        data = {}
        for attribute, (dataframe, column, ascending) in map.items():
            data[attribute] = self.get_attribute_and_compare(dataframe, player_index, column, position, ascending=ascending)
        return data

    def get_player_statistic_rank(self, player_index: tuple, position: str, stat_type: str, stat: str):
        map = self.getMapByStatType(stat_type)
        dataframe = map[stat][0]
        column = map[stat][1]
        ascending = map[stat][2]

        filtered = dataframe.loc[player_index[0], :, :, :]
        filtered = filtered[filtered[("pos", "")] == position]
        filtered[column] = pd.to_numeric(filtered[column])
        if ascending:
            filtered = filtered.nsmallest(3, column, "first")
        else:
            filtered = filtered.nlargest(3, column, "first")

        zipped = zip(filtered.index, filtered[column])
        data = {}
        data["ranking"] = []
        for index, value in zipped:
            player_name = index[2]
            player_nation = filtered.loc[index, "nation"]
            player_born = int(filtered.loc[index, "born"])
            
            player_id = get_player_id(player_name, player_nation, player_born)

            player_entry = {
                "id": player_id,
                "name": player_name,
                "nation": player_nation,
                "born": player_born,
                "value": float(value)
            }
            data["ranking"].append(player_entry)
        return data

    def get_attribute_and_compare(
        self,
        dataframe: pd.DataFrame,
        index: tuple,
        column,
        position: str,
        ascending=False,
    ):
        filtered = dataframe.loc[index[0], :, :, :]
        filtered = filtered[filtered[("pos", "")] == position]
        filtered[column] = pd.to_numeric(filtered[column])
        filtered["rank"] = filtered[column].rank(
            ascending=ascending, method="min", na_option="bottom"
        )
        rank = filtered.loc[index[1:], "rank"]

        total = filtered.shape[0]
        return (total - rank + 1) / total * 100
    
    def getMapByStatType(self, stat_type):
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