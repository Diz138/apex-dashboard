# Apex Legends Data Retriever

Fetches player stats from the [Apex Legends Status API](https://apexlegendsapi.com/) and writes
trimmed JSON files consumed directly by the Astro frontend.

## Usage

```bash
uv run retriever/retrieve_stats.py
```

Requires environment variables `APEX_API_KEY` and `APEX_UIDS` (comma-separated Xbox UIDs).
These are loaded from `.env` locally or from GitHub Actions secrets in CI.

## Output Files

| File | Description |
|------|-------------|
| `retriever/data/latest_profiles.json` | Current player data — read by Astro at build time |
| `retriever/data/snapshots/all_profiles_<TIMESTAMP>.json` | Timestamped archive of each run |

> **Note:** `data/snapshots/` is not checked in to version control. Snapshot files accumulate
> locally but are not committed to the repository.

Both files share the same schema (see below).

## Output Schema

Each file is a JSON **array** of player objects. The array is in fetch order; the frontend sorts
by `totalKills` descending at build time.

```json
[
  {
    "playerName": "string",
    "level": "number",
    "totalKills": "number",
    "topLegend": {
      "name": "string",
      "kills": "number",
      "icon": "string (URL)"
    },
    "rank": {
      "name": "string",
      "division": "number (1–4, or 0 for unranked)",
      "score": "number (RP)",
      "image": "string (URL)",
      "globalRankInt": "number | '—'"
    },
    "arenaRank": {
      "name": "string",
      "division": "number (1–4, or 0 for unranked)",
      "image": "string (URL)"
    },
    "collectedAtUtc": "string (YYYYMMDDTHHMMSSZ)"
  }
]
```

### Field Notes

- **`totalKills`** — sum of `kills` tracker values across all legends for the player.
- **`topLegend`** — the legend with the highest kill count. Falls back to Bangalore if no kill
  data is present.
- **`rank.globalRankInt`** — global leaderboard position. Set to `"—"` if the API does not
  return a value (e.g. unranked players with no placement data).
- **`collectedAtUtc`** — the UTC timestamp of the retrieval run that produced this record.

## Adding or Removing Players

Edit `APEX_UIDS` in your `.env` file (or the corresponding GitHub Actions secret). UIDs are
comma-separated Xbox platform UIDs from the Apex Legends Status API.
