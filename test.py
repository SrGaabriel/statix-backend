import soccerdata
import time
import pandas as pd
import os
from pathlib import Path
from datetime import date

date = date.today()
formatted_date = date.strftime("%Y-%m-%d")

BASE_DIR = Path(os.environ.get("SOCCERDATA_DIR", Path.home() / "soccerdata"))
DATA_DIR = Path(BASE_DIR, "data")
FBREF_DATA_DIR = Path(DATA_DIR, "FBref")

TODAY_FBREF_DATA_DIR = Path(FBREF_DATA_DIR, formatted_date)

fbref = soccerdata.FBref(
    leagues=["Big 5 European Leagues Combined"],
    seasons=["22-23"],
    data_dir=TODAY_FBREF_DATA_DIR
)
defense = fbref.read_player_season_stats(stat_type='defense').head(100)

def create_grouped_column(dataframe: pd.DataFrame, group: str, column, new_column_name: str):
    dataframe[column] = dataframe[column].fillna(0)
    dataframe[column] = pd.to_numeric(dataframe[column])
    if isinstance(column, tuple):
        dataframe[new_column_name] = dataframe[[column]] / dataframe.groupby(level=group)[[column]].sum() * 100
    elif isinstance(column, str):
        dataframe[new_column_name] = dataframe[column] / dataframe.groupby(level=group)[column].sum() * 100
    else:
        raise TypeError("Column must be a tuple or a string")

create_grouped_column(defense, "team", "Err", "Team Errors")
create_grouped_column(defense, "team", ('Tackles', 'Tkl'), "Team Tackles")
print(defense)
defense.to_excel("test.xlsx")