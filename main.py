from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import ast
import os

app = Flask(__name__)
CORS(app, supports_credentials=True)

# --- Path to CSV ---
csv_path = os.path.join("ingredients.csv")

# --- Load CSV safely ---
try:
    df = pd.read_csv(csv_path, quotechar='"')  # handles commas inside quotes
except Exception as e:
    print("Error loading CSV:", e)
    exit(1)

# --- Utility to safely parse list strings like "[1,0,1,0,0]" ---
def safe_eval(val):
    try:
        parsed = ast.literal_eval(val)
        if isinstance(parsed, list) and len(parsed) == 5:
            return parsed
        else:
            return [0, 0, 0, 0, 0]
    except Exception:
        return [0, 0, 0, 0, 0]

df['[obesity,heart,diabetes,cancer,gut]'] = df['[obesity,heart,diabetes,cancer,gut]'].apply(safe_eval)

# --- Map index to disease names ---
RISK_NAMES = ['obesity', 'heart', 'diabetes', 'cancer', 'gut']

# --- Create dictionary for quick lookup ---
ingredient_dict = {
    row['Ingredient'].lower(): {
        'description': row['Description'],
        'diseases': row['[obesity,heart,diabetes,cancer,gut]']
    }
    for _, row in df.iterrows()
}

@app.route('/')
def home():
    return "Flask backend is running!"

# --- API route to check ingredients ---
@app.route('/check', methods=['POST'])
def check_ingredients():
    data = request.get_json(force=True, silent=True) or {}
    ingredients = data.get('ingredients', [])
    results = []

    for ing in ingredients:
        ing_lower = ing.lower().strip()
        if ing_lower in ingredient_dict:
            info = ingredient_dict[ing_lower]
            risks_text = [name for val, name in zip(info['diseases'], RISK_NAMES) if val]
            # Build a readable sentence
            if risks_text:
                risk_sentence = f"May contribute to {', '.join(risks_text)}."
            else:
                risk_sentence = "No major risks reported."
            results.append({
                'ingredient': ing,
                'found': True,
                'description': info['description'],
                'risks': risk_sentence
            })
        else:
            results.append({
                'ingredient': ing,
                'found': False,
                'description': '',
                'risks': 'Unknown ingredient'
            })

    return jsonify({'results': results})

# --- Run Flask ---
if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)
