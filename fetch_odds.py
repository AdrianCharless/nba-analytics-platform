import os, requests, json
from dotenv import load_dotenv
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
RAW_DIR = PROJECT_ROOT / "data" / "bronze"
load_dotenv(PROJECT_ROOT / ".env")
BASE_URL = "https://api.sportsgameodds.com/v2/events"


def fetch_odds():
    odds_api_key = os.getenv("SPORTSGAMEODDS_API_KEY")
    if not odds_api_key:
        raise ValueError("SPORTSGAMEODDS_API_KEY not found. Check your .env file.")

    
    params = {
        "apiKey": odds_api_key,
        "leagueID": "NBA",
        "oddsAvailable": "true",
        "started": "false",
        "limit": 50,
        "oddIDs": "points-PLAYER_ID-game-ou-over,assists-PLAYER_ID-game-ou-over",
        "includeOpposingOdds": "true"
        }

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
    filename = RAW_DIR / f"games_{fetched_at}.json"
    # make directory if its not already created
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    with open(filename, "w") as f:
        json.dump(all_games, f)

    print("Saved", filename)
    return filename

if __name__ == "__main__":
    fetch_odds()