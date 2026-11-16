import os, requests, json
from dotenv import load_dotenv
from datetime import datetime, timezone
load_dotenv()
odds_api_key = os.getenv("SPORTSGAMEODDS_API_KEY")

if not odds_api_key:
    raise ValueError("SPORTSGAMEODDS_API_KEY not found. Check your .env file.")

BASE_URL = "https://api.sportsgameodds.com/v2/events"
params = {
    "apiKey": odds_api_key,
    "leagueID": "NBA",
    "oddsAvailable": "true",
    "started": "false",
    "limit": 50,
    "oddIDs": "points-PLAYER_ID-game-ou-over,assists-PLAYER_ID-game-ou-over",
    "includeOpposingOdds": "true"
    }

# response = requests.get(BASE_URL, params=params, timeout=30)
# response.raise_for_status()

# data = response.json()
# print("Got", len(data["data"]), "results")

all_games = []
cursor = None

while True:
    if cursor:
        params["cursor"] = cursor

    response = requests.get(BASE_URL, params=params, timeout=30)
    response.raise_for_status()
    page = response.json()

    all_games.extend(page["data"])
    cursor = page.get("nextCursor")

    if not page["data"] or not cursor:
        break

print("Total games:", len(all_games))

# change utc datetime to string
fetched_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H-%M-%SZ")
# create filename for freshly ingested games
filename = f"data/bronze/games_{fetched_at}.json"
# make directory if its not already created
os.makedirs("data/bronze", exist_ok=True)

with open(filename, "w") as f:
    json.dump(all_games, f)

print("Saved", filename)