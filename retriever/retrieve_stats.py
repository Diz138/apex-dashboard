import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv() 

API_BASE = "https://api.mozambiquehe.re"
PLATFORM = "X1"  # Xbox
# Rate limit: 2 requests per second = minimum 0.5s between requests
# Using 0.6s to be safe
RATE_LIMIT_DELAY = 0.6
DATA_DIR = Path("retriever/data")
SNAPSHOTS_DIR = DATA_DIR / "snapshots"

def utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def fetch_user_by_uid(api_key: str, uid: str) -> dict:
    """
    Calls the /bridge endpoint for profile/stats data by UID.
    Does not support match history (no history param).

    Arguments: 
    - api_key: Your API key for authentication.
    - uid: The player's Apex Legends Status user ID to fetch data for.

    Returns:
    - A dictionary containing the user's profile and stats data as returned by the API.
    """

    params = {
        "auth": api_key,
        "uid": uid,
        "platform": PLATFORM,
    }

    url = f"{API_BASE}/bridge"
    r = requests.get(url, params=params, timeout=20)
    if r.status_code != 200:
        raise RuntimeError(f"HTTP {r.status_code}: {r.text[:300]}")
    return r.json()


def save_json(path: Path, obj: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, sort_keys=False), encoding="utf-8")


def main():
    api_key = os.environ.get("APEX_API_KEY")
    uids_str = os.environ.get("APEX_UIDS")
    
    if not api_key or not uids_str:
        raise SystemExit("Set env vars APEX_API_KEY and APEX_UIDS (comma-separated UIDs).")
    
    # Parse comma-separated UIDs
    uids = [uid.strip() for uid in uids_str.split(",") if uid.strip()]
    
    if not uids:
        raise SystemExit("APEX_UIDS must contain at least one UID.")

    # Collect all player data
    all_profiles = {}
    stamp = utc_stamp()
    
    for i, user_id in enumerate(uids):
        print(f"Fetching data for {user_id}...")
        if i > 0:
            time.sleep(RATE_LIMIT_DELAY)

        profile = fetch_user_by_uid(api_key, user_id)
        profile["_collected_at_utc"] = stamp
        all_profiles[user_id] = profile

    save_json(SNAPSHOTS_DIR / f"all_profiles_{stamp}.json", all_profiles)
    save_json(DATA_DIR / "latest_profiles.json", all_profiles)

    print("Done.")

if __name__ == "__main__":
    main()
