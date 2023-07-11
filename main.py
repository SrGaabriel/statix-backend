import soccerdata as sd
import pandas as pd
from flask import Flask, jsonify, request, abort
from flask_cors import CORS
from unidecode import unidecode
import re, base64
import numpy as np

from teamname_replacements import TEAMNAME_REPLACEMENTS
from stats import Stats
from utils import get_player_id, decode_player_id

fbref = sd.FBref(
    leagues=["Big 5 European Leagues Combined", "BRA-Brasileirao"],
    seasons=["22-23", "2023"],
)
elo = sd.ClubElo()


playing_time = {}
player_ids = {}


def create_stats_dataframe(
    type: str, isStandard: bool = False, isKeeper=False
) -> pd.DataFrame:
    renamed = fbref.read_player_season_stats(stat_type=type).rename(
        index=lambda x: TEAMNAME_REPLACEMENTS.get(x, x), level="team"
    )
    without_duplicates = remove_duplicates(renamed, isStandard, isKeeper)
    return without_duplicates


playing_times = {}
duplicated_indexes = []
duplicated_goalkeeper_indexes = []


def remove_duplicates(dataframe, isStandard=False, isKeeper=False):
    for index, row in dataframe.iterrows():
        if index[0] == "BRA-Brasileirao" and index[1] == "2223":
            duplicated_indexes.append(index)
            continue
        if not isStandard:
            continue

        name = index[3]
        nation = row["nation"].item()
        born = row["born"].item()
        position = row["pos"].item()
        isGoalkeeper = position == "GK"
        if name is None or nation is None or born is None:
            duplicated_indexes.append(index)
            if isGoalkeeper:
                duplicated_goalkeeper_indexes.append(index)
            continue
        born = int(born)

        id = get_player_id(name, nation, born)
        if id is None:
            duplicated_indexes.append(index)
            if isGoalkeeper:
                duplicated_goalkeeper_indexes.append(index)
            continue

        playing_time = row[("Playing Time", "MP")]
        if playing_time is None:
            duplicated_indexes.append(index)
            if isGoalkeeper:
                duplicated_goalkeeper_indexes.append(index)
            continue

        if id not in player_ids:
            playing_times[id] = playing_time
            player_ids[id] = (index, row)
            continue
        other_playing_time = playing_times[id]
        if playing_time > other_playing_time:
            duplicated_indexes.append(player_ids[id][0])
            if isGoalkeeper:
                duplicated_goalkeeper_indexes.append(index)
            player_ids[id] = (index, row)
            playing_times[id] = playing_time
            continue
        duplicated_indexes.append(index)
        if isGoalkeeper:
            duplicated_goalkeeper_indexes.append(index)

    if isKeeper:
        return dataframe.drop(duplicated_goalkeeper_indexes)
    else:
        return dataframe.drop(duplicated_indexes)


def remove_plus_signal(dataframe: pd.DataFrame, column):
    dataframe[column] = dataframe[column].str.replace("+", "")
    dataframe[column] = dataframe[column].astype(float)


def create_proportional_column(
    dataframe: pd.DataFrame, name: str, numerator: tuple, denominator: tuple
):
    dataframe[numerator] = pd.to_numeric(dataframe[numerator])
    dataframe[denominator] = pd.to_numeric(dataframe[denominator])
    dataframe[name] = dataframe[numerator] / dataframe[denominator]
    dataframe.replace([np.inf, -np.inf], np.nan, inplace=True)


def create_per_90s_column(
    dataframe: pd.DataFrame, name: str, column: tuple, ninetiesColumn="90s"
):
    create_proportional_column(dataframe, f"{name}/90", column, ninetiesColumn)


standard = create_stats_dataframe("standard", isStandard=True)
shooting = create_stats_dataframe("shooting")

remove_plus_signal(shooting, ("Expected", "np:G-xG"))

passing = create_stats_dataframe("passing")

create_proportional_column(
    passing, "Pass Directness %", ("Total", "PrgDist"), ("Total", "Att")
)
create_per_90s_column(passing, "Passes Completed", ("Total", "Cmp"))
remove_plus_signal(passing, "A-xAG")

passing_types = create_stats_dataframe("passing_types")
goal_shot_creation = create_stats_dataframe("goal_shot_creation")
defense = create_stats_dataframe("defense")

create_per_90s_column(defense, "Challenges", ("Challenges", "Att"))

possession = create_stats_dataframe("possession")

create_per_90s_column(possession, "Touches", ("Touches", "Live"))
create_per_90s_column(possession, "Take-ons", ("Take-Ons", "Att"))
create_per_90s_column(possession, "Successful Take-Ons", ("Take-Ons", "Succ"))
create_per_90s_column(possession, "Carries", ("Carries", "Carries"))
create_per_90s_column(possession, "Carries Progressiveness", ("Carries", "PrgDist"))

misc = create_stats_dataframe("misc")

create_per_90s_column(misc, "Aerial Duels Won", ("Aerial Duels", "Won"))
create_per_90s_column(misc, "Fouls", ("Performance", "Fls"))

keeper = create_stats_dataframe("keeper", isKeeper=True)

create_per_90s_column(
    keeper, "SoTA", ("Performance", "SoTA"), ninetiesColumn=("Playing Time", "90s")
)

keeper_advanced = create_stats_dataframe("keeper_adv", isKeeper=True)

create_per_90s_column(keeper_advanced, "GA", ("Goals", "GA"))
create_per_90s_column(keeper_advanced, "FK", ("Goals", "FK"))
create_per_90s_column(keeper_advanced, "CK", ("Goals", "CK"))
create_per_90s_column(keeper_advanced, "OG", ("Goals", "OG"))

del playing_times

stats = Stats(
    standard,
    shooting,
    passing,
    passing_types,
    goal_shot_creation,
    defense,
    possession,
    misc,
    keeper,
    keeper_advanced,
)

clubs_elo = {}

elo = elo.read_by_date().head(300)
for index, row in elo.iterrows():
    clubs_elo[index] = row["elo"]


def get_club_elo(club):
    if club in clubs_elo:
        return clubs_elo[club]
    return 1650.0


def create_regex_pattern(word):
    pattern = r"(?i)(?<=\b)\S*" + re.escape(unidecode(word)) + r"\S*(?=\b)"
    return pattern


def compile_dataframe_players(dataframe):
    # Create a list to store player details
    players = []

    # Iterate over the filtered DataFrame
    for index, row in dataframe.iterrows():
        name = index[3]
        nationality = row["nation"].item()
        id = get_player_id(name, nationality, int(row["born"].item()))
        if id is None:
            continue

        player_data = {
            "id": id,
            "name": name,
            "club": index[2],
            "club_elo": get_club_elo(index[2]),
            "nationality": nationality,
            "position": row["pos"].item()[:2],
        }
        players.append(player_data)
    return players


playerLevel = standard.index.get_level_values(3)

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}}, methods=["GET", "POST"])


@app.route("/players", methods=["GET"])
def get_players():
    currentSearchTerm = request.args.get("search", default="", type=str)

    if currentSearchTerm == "":
        return jsonify(compile_dataframe_players(standard))

    if len(currentSearchTerm) < 4:
        return jsonify([])

    playerIndex = playerLevel.str.contains(
        create_regex_pattern(currentSearchTerm), regex=True
    )
    newDataFrame = standard.loc[playerIndex]
    if len(newDataFrame) == 0:
        return jsonify([])

    return jsonify(compile_dataframe_players(newDataFrame))


@app.route("/players/<id>", methods=["GET"])
def get_player(id):
    (player_index, player_row) = player_ids.get(id)
    if player_index is None or player_row is None:
        abort(404)

    player_object = {
        "id": id,
        "name": player_index[3],
        "club": player_index[2],
        "nationality": player_row["nation"].item(),
        "position": player_row["pos"].item()[:2],
        "age": player_row["age"].item()[:2],
        "born": int(player_row["born"].item()),
    }

    return jsonify({"player": player_object})


def get_position_abbreviation(name: str):
    if name == "goalkeeper":
        return "GK"
    if name == "defender":
        return "DF"
    if name == "midfielder":
        return "MF"
    if name == "forward":
        return "FW"
    return "XX"


@app.route("/players/<id>/<position>/<stat>", methods=["GET"])
def get_player_positional_data(id, position, stat):
    (player_index, player_row) = player_ids.get(id)
    if player_index is None or player_row is None:
        abort(404)

    return jsonify(
        stats.get_player_data(player_index, get_position_abbreviation(position), stat)
    )


@app.route("/players/<id>/<position>/<type>/<stat>", methods=["GET"])
def get_player_statistic_ranking(id, position, type, stat):
    (player_index, player_row) = player_ids.get(id)
    if player_index is None or player_row is None:
        abort(404)

    return jsonify(
        stats.get_player_statistic_rank(
            player_index, get_position_abbreviation(position), type, stat
        )
    )


if __name__ == "__main__":
    app.run()
