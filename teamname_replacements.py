from pathlib import Path
import json, os
import logging

BASE_DIR = Path(os.environ.get("SOCCERDATA_DIR", Path.home() / "soccerdata"))
CONFIG_DIR = Path(BASE_DIR, "config")

TEAMNAME_REPLACEMENTS = {}
_f_custom_teamnname_replacements = CONFIG_DIR / "teamname_replacements.json"
if _f_custom_teamnname_replacements.is_file():
    with open(_f_custom_teamnname_replacements, encoding='utf8') as json_file:
        for team, to_replace_list in json.load(json_file).items():
            for to_replace in to_replace_list:
                TEAMNAME_REPLACEMENTS[to_replace] = team