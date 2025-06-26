import json

with open("firebase_carbon_tracker.json", "r") as f:
    content = f.read()

# Escape newlines and quotes properly for TOML
escaped = json.dumps(content)
print(f'FIREBASE_KEY = {escaped}')
