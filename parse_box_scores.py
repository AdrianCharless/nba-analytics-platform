import json
import pandas as pd
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
RAW_DIR = PROJECT_ROOT / "data" / "bronze"
OUT_DIR = PROJECT_ROOT / "data" / "silver"

def parse_box_scores():
    raw_files = sorted(RAW_DIR.glob("box_scores_*.json"))
    processed = 0
    for path in raw_files:
        name = path.name
        stamp = name.removeprefix("box_scores_").removesuffix(".json")
        out_path = OUT_DIR / f"box_scores_{stamp}.parquet"

        if out_path.exists():
            continue
        print("Processing", path)
        

        with open(path) as f:
            games = json.load(f)
        rs = games["resultSets"][0]
        df = pd.DataFrame(rs["rowSet"], columns=rs["headers"])
        if df.empty:
            print("No games in", path, "- skipping")
            continue
        columns = {
            "GAME_ID": "game_id",
            "GAME_DATE": "game_date",
            "MATCHUP": "matchup",
            "PLAYER_ID": "player_id",
            "PLAYER_NAME": "player_name",
            "TEAM_ABBREVIATION": "team",
            "MIN": "minutes",
            "PTS": "points",
            "AST": "assists",
            "REB": "rebounds",
            "FG3M": "threes_made",
            "FG3A": "threes_attempted",
            "FGM": "fgm",
            "FGA": "fga",
            "FTM": "ftm",
            "FTA": "fta",
            "TOV": "turnovers",
            "STL": "steals",
            "BLK": "blocks",
        }
        df = df[list(columns.keys())].rename(columns=columns)
        df["is_home"] = df["matchup"].str.contains("vs.", regex=False)
        df["opponent"] = df["matchup"].str.split(" ").str[-1]
        df = df.drop(columns=["matchup"])
        df["game_date"] = pd.to_datetime(df["game_date"]).dt.date
        df["game_id"] = df["game_id"].astype(str)
        df["minutes"] = df["minutes"].astype(float)

        OUT_DIR.mkdir(parents=True, exist_ok=True)
        df.to_parquet(out_path, index=False)

        print("Saved", out_path, "-", len(df), "rows")
        processed += 1
    return processed

if __name__ == "__main__":
    count = parse_box_scores()
    print("Done -", count, "files processed")