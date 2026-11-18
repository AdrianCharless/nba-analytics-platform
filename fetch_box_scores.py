from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import json
from pathlib import Path
from nba_api.stats.endpoints import leaguegamelog

PROJECT_ROOT = Path(__file__).resolve().parent
RAW_DIR = PROJECT_ROOT / "data" / "bronze"

def fetch_box_scores(game_date=None):
    if game_date is None:
        game_date = datetime.now(ZoneInfo("America/New_York")).date() - timedelta(days=1)
    

    api_date = game_date.strftime("%m/%d/%Y")
    file_date = game_date.strftime("%Y-%m-%d")

    log = leaguegamelog.LeagueGameLog(
        season="2026-27",
        player_or_team_abbreviation="P",
        date_from_nullable=api_date,
        date_to_nullable=api_date,
        )

    raw = log.get_dict() 

    # create filename for freshly ingested games
    filename = RAW_DIR / f"box_scores_{file_date}.json"
    # make directory if its not already created
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    with open(filename, "w") as f:
        json.dump(raw, f)
    
    print("Saved", filename)
    return filename


if __name__ == "__main__":
    fetch_box_scores()