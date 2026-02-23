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
FALLBACK_ICON = "https://api.mozambiquehe.re/assets/icons/bangalore.png"
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
    - A dictionary containing the raw API response for the given player.
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


def transform_profile(raw: dict, stamp: str) -> dict:
    """
    Trims a raw /bridge API response down to exactly the fields used by the
    frontend. See retriever/README.md for the output schema.
    """
    global_data = raw.get("global", {})
    legends_all = raw.get("legends", {}).get("all", {})

    total_kills = 0
    top_legend_name = "Bangalore" # set bangalore as default top legend in case no legends come back
    top_legend_kills = 0
    top_legend_icon = FALLBACK_ICON

    for legend_name, legend_data in legends_all.items():
        kills = 0
        for stat in (legend_data.get("data") or []):
            if stat.get("key") == "kills" and isinstance(stat.get("value"), (int, float)):
                kills = int(stat["value"])
                break
        total_kills += kills
        if kills > top_legend_kills:
            top_legend_kills = kills
            top_legend_name = legend_name
            top_legend_icon = (legend_data.get("ImgAssets") or {}).get("icon") or FALLBACK_ICON

    rank = global_data.get("rank") or {}
    arena = global_data.get("arena") or {}

    global_rank_int = rank.get("ALStopIntGlobal")
    if global_rank_int is None:
        global_rank_int = "—"

    return {
        "playerName": global_data.get("name") or "Unknown",
        "level": global_data.get("level") or 0,
        "totalKills": total_kills,
        "topLegend": {
            "name": top_legend_name,
            "kills": top_legend_kills,
            "icon": top_legend_icon,
        },
        "rank": {
            "name": rank.get("rankName") or "Unranked",
            "division": rank.get("rankDiv") or 0,
            "score": rank.get("rankScore") or 0,
            "image": rank.get("rankImg") or "",
            "globalRankInt": global_rank_int,
        },
        "arenaRank": {
            "name": arena.get("rankName") or "Unranked",
            "division": arena.get("rankDiv") or 0,
            "image": arena.get("rankImg") or "",
        },
        "collectedAtUtc": stamp,
    }


def save_json(path: Path, obj: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, sort_keys=False), encoding="utf-8")


def main():
    api_key = os.environ.get("APEX_API_KEY")
    uids_str = os.environ.get("APEX_UIDS")

    if not api_key or not uids_str:
        raise SystemExit("Set env vars APEX_API_KEY and APEX_UIDS (comma-separated UIDs).")

    uids = [uid.strip() for uid in uids_str.split(",") if uid.strip()]

    if not uids:
        raise SystemExit("APEX_UIDS must contain at least one UID.")

    profiles = []
    stamp = utc_stamp()

    for i, user_id in enumerate(uids):
        print(f"Fetching data for {user_id}...")
        if i > 0:
            time.sleep(RATE_LIMIT_DELAY)

        raw = fetch_user_by_uid(api_key, user_id)
        profiles.append(transform_profile(raw, stamp))

    if not os.environ.get("CI"):
        save_json(SNAPSHOTS_DIR / f"all_profiles_{stamp}.json", profiles)
    save_json(DATA_DIR / "latest_profiles.json", profiles)

    print(f"Done. Saved {len(profiles)} profiles.")


if __name__ == "__main__":
    main()
