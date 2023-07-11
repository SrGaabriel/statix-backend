import base64


def get_player_id(name, nation, born):
    if name is None or nation is None or born is None:
        return None

    # Encode each unique value to base64
    encoded_name = base64.urlsafe_b64encode(name.encode()).decode().rstrip("=")
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
