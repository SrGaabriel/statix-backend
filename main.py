import soccerdata as sd
import pandas as pd
from flask import Flask, jsonify, request, abort
from flask_cors import CORS
from flask_caching import Cache
from unidecode import unidecode
import re
import numpy as np
from datetime import date
import os
from pathlib import Path

from stats import Stats
from utils import get_player_id, decode_league, encode_league, format_player_age
from infos import PlayerInfos
from loader import DataframeLoader

date = date.today()
formatted_date = date.strftime("%Y-%m-%d")

BASE_DIR = Path(os.environ.get("SOCCERDATA_DIR", Path.home() / "soccerdata"))
DATA_DIR = Path(BASE_DIR, "data")
FBREF_DATA_DIR = Path(DATA_DIR, "FBref")
POSITIONS_DATA_DIR = Path(DATA_DIR, "positions")

TODAY_FBREF_DATA_DIR = Path(FBREF_DATA_DIR, formatted_date)
TODAY_POSITIONS_DATA_DIR = Path(POSITIONS_DATA_DIR, formatted_date)

player_infos = PlayerInfos(
    data_dir=TODAY_POSITIONS_DATA_DIR, cache=True, store_cache=True
)
player_infos.load_all_players()

elo = sd.ClubElo()
loader = DataframeLoader(data_dir=TODAY_FBREF_DATA_DIR, player_infos=player_infos)

standard = loader.create_stats_dataframe("standard", is_standard=True)
shooting = loader.create_stats_dataframe("shooting")

loader.remove_plus_signal(shooting, ("Expected", "np:G-xG"))

passing = loader.create_stats_dataframe("passing")

loader.create_proportional_column(
    passing, "Pass Directness %", ("Total", "PrgDist"), ("Total", "Att")
)
loader.create_per_90s_column(passing, "Passes Completed", ("Total", "Cmp"))
loader.remove_plus_signal(passing, "A-xAG")

passing_types = loader.create_stats_dataframe("passing_types")

loader.create_per_90s_column(passing_types, "Sw", ("Pass Types", "Sw"))
loader.create_per_90s_column(passing_types, "Crosses", ("Pass Types", "Crs"))

goal_shot_creation = loader.create_stats_dataframe("goal_shot_creation")
defense = loader.create_stats_dataframe("defense")

loader.create_grouped_column(defense, "team", ('Tackles', 'Tkl'), 'Team Tackles')
loader.create_grouped_column(defense, "team", "Tkl+Int", 'Team Def Actions')
loader.create_per_90s_column(defense, "Challenges", ("Challenges", "Att"))
defense.to_excel("defense.xlsx")

possession = loader.create_stats_dataframe("possession")

loader.create_per_90s_column(possession, "Touches", ("Touches", "Live"))
loader.create_per_90s_column(possession, "Take-ons", ("Take-Ons", "Att"))
loader.create_per_90s_column(possession, "Successful Take-Ons", ("Take-Ons", "Succ"))
loader.create_per_90s_column(possession, "Carries", ("Carries", "Carries"))
loader.create_per_90s_column(
    possession, "Carries Progressiveness", ("Carries", "PrgDist")
)

misc = loader.create_stats_dataframe("misc")

loader.create_per_90s_column(misc, "Aerial Duels Won", ("Aerial Duels", "Won"))
loader.create_per_90s_column(misc, "Fouls", ("Performance", "Fls"))

keeper = loader.create_stats_dataframe(
    "keeper",
    is_keeper=True,
)

loader.create_per_90s_column(
    keeper, "SoTA", ("Performance", "SoTA"), ("Playing Time", "90s")
)

keeper_advanced = loader.create_stats_dataframe("keeper_adv", is_keeper=True)

loader.create_per_90s_column(keeper_advanced, "GA", ("Goals", "GA"))
loader.create_per_90s_column(keeper_advanced, "FK", ("Goals", "FK"))
loader.create_per_90s_column(keeper_advanced, "CK", ("Goals", "CK"))
loader.create_per_90s_column(keeper_advanced, "OG", ("Goals", "OG"))

loader.clear()

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
        player_info = player_infos.get_player_info_or_empty(id)

        player_data = {
            "id": id,
            "name": name,
            "club": index[2],
            "club_elo": get_club_elo(index[2]),
            "nationality": row["nation"].item(),
            "position": row["pos"].item()[:2],
            "base_id": player_info["base_id"],
            "has_image": player_info["has_image"],
        }
        players.append(player_data)
    return players


playerLevel = standard.index.get_level_values(3)

app = Flask(__name__)
app.json.sort_keys = False
cache = Cache(config={"CACHE_TYPE": "SimpleCache", "DEBUG": True})
CORS(app, resources={r"/*": {"origins": "*"}}, methods=["GET", "POST"])

cache.init_app(app)


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
    index_row_data = loader.get_player_by_id(id)
    if index_row_data is None:
        abort(404)

    player_info = player_infos.get_player_info_or_empty(id)
    (player_index, player_row) = index_row_data
    player_object = {
        "id": id,
        "name": player_index[3],
        "club": player_index[2],
        "league": encode_league(player_index[0]),
        "nationality": player_row["nation"].item(),
        "position": player_row["pos"].item()[:2],
        "age": format_player_age(player_row["age"].item()),
        "born": int(player_row["born"].item()),
        "base_id": player_info["base_id"],
        "has_image": player_info["has_image"],
    }

    return jsonify({"player": player_object})


def get_position_abbreviation(name: str):
    if name == "goalkeeper":
        return "GK"
    if name == "defender":
        return "DF"
    if name == "centreback":
        return "CB"
    if name == "fullback":
        return "FB"
    if name == "midfielder":
        return "MF"
    if name == "forward":
        return "FW"
    if name == "winger":
        return "W"
    if name == "striker":
        return "ST"
    return "XX"


@app.route("/players/<id>/data", methods=["GET"])
def get_player_positional_data(id):
    index_row_data = loader.get_player_by_id(id)
    if index_row_data is None:
        abort(404)

    (player_index, player_row) = index_row_data
    position = request.args.get("position", type=str)
    if position is None:
        position = get_position_abbreviation(player_row["pos"].item()[:2])
    else:
        position = get_position_abbreviation(position)
    league = decode_league(
        request.args.get("league", default=player_index[0], type=str)
    )

    return jsonify(stats.get_player_data(player_index, league, position))


@app.route("/players/<id>/profile", methods=["GET"])
def get_player_profile_data(id):
    index_row_data = loader.get_player_by_id(id)
    if index_row_data is None:
        abort(404)

    (player_index, player_row) = index_row_data
    position = request.args.get("position", type=str)
    if position is None:
        position = player_row["pos"].item()[:2]
    else:
        position = get_position_abbreviation(position)
    league = decode_league(
        request.args.get("league", default=player_index[0], type=str)
    )
    ratingType = request.args.get("type", default="dynamic", type=str)

    return jsonify(stats.create_radar_data(player_index, league, position, ratingType))


@app.route("/players/<id>/similar", methods=["GET"])
def get_similar_players(id):
    index_row_data = loader.get_player_by_id(id)
    if index_row_data is None:
        abort(404)

    (player_index, player_row) = index_row_data
    position = request.args.get("position", type=str)
    if position is None:
        position = get_position_abbreviation(player_row["pos"].item()[:2])
    else:
        position = get_position_abbreviation(position)
    league = decode_league(
        request.args.get("league", default=player_index[0], type=str)
    )

    return jsonify(stats.find_similar_players(player_index, league, position))


@app.route("/players/<id>/<type>/<stat>", methods=["GET"])
def get_player_statistic_ranking(id, type, stat):
    index_row_data = loader.get_player_by_id(id)
    if index_row_data is None:
        abort(404)

    (player_index, player_row) = index_row_data
    position = request.args.get("position", type=str)
    if position is None:
        position = player_row["pos"].item()[:2]
    else:
        position = get_position_abbreviation(position)
    league = decode_league(
        request.args.get("league", default=player_index[0], type=str)
    )

    return jsonify(
        stats.get_player_statistic_rank(player_index, league, position, type, stat)
    )


if __name__ == "__main__":
    app.run()
