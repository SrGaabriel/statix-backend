import base64


def get_player_id(name, nation, born):
    if name is None or nation is None or born is None:
        return None

    # Encode each unique value to base64
    encoded_name = base64.urlsafe_b64encode(name.lower().encode()).decode().rstrip("=")
    encoded_nationality = base64.urlsafe_b64encode(nation.encode()).decode().rstrip("=")
    encoded_birth_year = (
        base64.urlsafe_b64encode(born.to_bytes((born.bit_length() + 7) // 8, "big"))
        .decode()
        .rstrip("=")
    )

    # Concatenate the encoded values
    numerical_id = f"{encoded_nationality}-{encoded_name}-{encoded_birth_year}"

    return numerical_id


def decode_player_id(numerical_id):
    encoded_nationality, encoded_name, encoded_birth_year = numerical_id.split("-")

    name = base64.urlsafe_b64decode(encoded_name + "==").decode()
    nationality = base64.urlsafe_b64decode(encoded_nationality + "==").decode()
    birth_year = base64.urlsafe_b64decode(encoded_birth_year + "==").decode()

    return name, nationality, birth_year


def encode_league(league):
    if league == "ENG-Premier League":
        return "premier_league"
    if league == "FRA-Ligue 1":
        return "ligue_1"
    if league == "GER-Bundesliga":
        return "bundesliga"
    if league == "ITA-Serie A":
        return "serie_a"
    if league == "ESP-La Liga":
        return "la_liga"
    if league == "BRA-Brasileirao":
        return "brasileirao"
    if league == "Top 5 European Leagues":
        return "top_5"
    raise ValueError(f"Unknown league: {league}")

# decodes league
def decode_league(league: str):
    if league == "premier_league":
        return "ENG-Premier League"
    if league == "ligue_1":
        return "FRA-Ligue 1"
    if league == "bundesliga":
        return "GER-Bundesliga"
    if league == "serie_a":
        return "ITA-Serie A"
    if league == "la_liga":
        return "ESP-La Liga"
    if league == "brasileirao":
        return "BRA-Brasileirao"
    if league == "top_5":
        return "Top 5 European Leagues"
    raise ValueError(f"Unknown league: {league}")

def format_player_age(age) -> int:
    if isinstance(age, str) and len(age) > 2:
        return int(age[:2])
    elif isinstance(age, int):
        return age
    else:
        return int(age)