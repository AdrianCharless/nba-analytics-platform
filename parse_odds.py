# This file will read the nested JSON and flatten it into rows. 
import json, os, glob
from datetime import datetime, timezone
import pandas as pd

raw_files = sorted(glob.glob("data/bronze/games_*.json"))

for path in raw_files:
    name = os.path.basename(path)
    stamp = name.removeprefix("games_").removesuffix(".json")
    out_path = f"data/silver/props_{stamp}.parquet"

    if os.path.exists(out_path):
        continue
    print("Processing", path)

    fetched_at = datetime.strptime(stamp, "%Y-%m-%dT%H-%M-%SZ").replace(tzinfo=timezone.utc)

    

    with open(path) as f:
        games = json.load(f)

    rows = []

    for game in games:
        game_id = game["eventID"]
        game_start = game["status"]["startsAt"]
        for odd_id, prop in game["odds"].items():
            player_id = prop["playerID"]
            stat = prop["statID"]
            side = prop["sideID"]
            fair_line = float(prop.get("fairOverUnder")) if prop.get("fairOverUnder") is not None else None
            fair_odds = int(prop.get("fairOdds")) if prop.get("fairOdds") is not None else None
            books = prop.get("byBookmaker", {})
            if books:
                for sportsbook, bookmaker in books.items():
                    if not bookmaker.get("available"):
                        continue
                    line = float(bookmaker["overUnder"])
                    odds = int(bookmaker["odds"])
                    book_updated_at = bookmaker["lastUpdatedAt"]
                    rows.append({
                        "event_id": game_id,
                        "game_starts_at": game_start,
                        "player_id": player_id,
                        "stat": stat,
                        "side": side,
                        "fair_line": fair_line,
                        "fair_odds_american": fair_odds,
                        "sportsbook": sportsbook,
                        "line": line,
                        "odds_american": odds,
                        "book_updated_at": book_updated_at,
                        "fetched_at": fetched_at,
                    })
            else:
                raw_line = prop.get("bookOverUnder")
                raw_odds = prop.get("bookOdds")
                if raw_line is None or raw_odds is None:
                    continue
                rows.append({
                                    "event_id": game_id,
                                    "game_starts_at": game_start,
                                    "player_id": player_id,
                                    "stat": stat,
                                    "side": side,
                                    "fair_line": fair_line,
                                    "fair_odds_american": fair_odds,
                                    "sportsbook": "consensus",
                                    "line": float(raw_line),
                                    "odds_american": int(raw_odds),
                                    "book_updated_at": None,
                                    "fetched_at": fetched_at,
                                })
    if not rows:
        print("No rows in", path, "- skipping")
        continue
    df = pd.DataFrame(rows)

    df["game_starts_at"] = pd.to_datetime(df["game_starts_at"], utc=True)
    df["book_updated_at"] = pd.to_datetime(df["book_updated_at"], utc=True)

    os.makedirs("data/silver", exist_ok=True)
    df.to_parquet(out_path, index=False)

    print("Saved", out_path, "-", len(df), "rows")