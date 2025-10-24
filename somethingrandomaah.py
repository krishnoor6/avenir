import pandas as pd
import ast
import re

csv_path = "C:/Users/HP/Downloads/avenir-main/avenir-main/backend/ingredients.csv"

# Load CSV
df = pd.read_csv(csv_path)

def safe_parse_list(x):
    # Convert to string first
    s = str(x).strip()

    # Fix potential newline / weird spaces
    s = re.sub(r'\s+', '', s)

    # Match pattern like [0,0,1,0,0]
    match = re.fullmatch(r'\[(\d,)*\d\]', s)
    if match:
        return [int(i) for i in s.strip("[]").split(",")]

    # If something unexpected, return zeros
    return [0,0,0,0,0]

df['[obesity,heart,diabetes,cancer,gut]'] = df['[obesity,heart,diabetes,cancer,gut]'].apply(safe_parse_list)

print(df.head())
