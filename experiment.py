import pandas as pd

# Sample DataFrame with a multiindex
data = {
    'Goals': [10, 5, 7],
    'Assists': [8, 12, 3]
}

index = pd.MultiIndex.from_tuples([('Real Madrid', 'Toni Kroos'), ('Barcelona', 'Lionel Messi'), ('Juventus', 'Toni Kroos')], names=['Team', 'Player'])

df = pd.DataFrame(data, index=index)
print(df)

# Function to rename 'Toni Kroos' under 'Real Madrid' to 'Eder Militao'
def rename_toni_kroos(player_tuple):
    team, player = player_tuple
    if team == 'Real Madrid' and player == 'Toni Kroos':
        return team, 'Eder Militao'
    return player_tuple

# Renaming the multiindex entry
df.index = df.index.map(rename_toni_kroos)
print(df)
