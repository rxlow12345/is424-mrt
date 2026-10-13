"""Collect DataMall observations without logging credentials or response bodies."""
import csv
import json
import os
import sys
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

URL = "https://datamall2.mytransport.sg/ltaodataservice/PCDRealTime"
LINES = "NSL EWL NEL CCL CEL CGL DTL TEL BPL SLRT PLRT".split()
FIELDS = ["Station", "StartTime", "EndTime", "CrowdLevel", "TrainLine", "CollectedAt"]
OUTPUT = Path(__file__).resolve().parents[1] / "data" / "crowd_density_log.csv"


def fetch(line, key):
    request = Request(URL + "?" + urlencode({"TrainLine": line}),
                      headers={"AccountKey": key, "accept": "application/json"})
    for attempt in range(4):
        try:
            with urlopen(request, timeout=30) as response:
                payload = json.load(response)
            rows = payload.get("value") if isinstance(payload, dict) else None
            if not isinstance(rows, list):
                raise ValueError("Unexpected API response structure")
            return rows
        except HTTPError as error:
            if error.code not in (429, 500, 502, 503, 504) or attempt == 3:
                raise RuntimeError(f"{line}: HTTP {error.code}") from None
        except (URLError, TimeoutError):
            if attempt == 3:
                raise RuntimeError(f"{line}: network request failed") from None
        except (ValueError, UnicodeError):
            raise RuntimeError(f"{line}: invalid API response") from None
        time.sleep(2 ** (attempt + 1))


def observation_key(row):
    return tuple(row[field] for field in FIELDS[:5])


def append_new(rows, path=OUTPUT):
    seen = set()
    if path.exists() and path.stat().st_size:
        with path.open(newline="", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            if reader.fieldnames != FIELDS:
                raise RuntimeError("Existing CSV has an unexpected header")
            seen = {observation_key(row) for row in reader}
    fresh = []
    for row in rows:
        identity = observation_key(row)
        if identity not in seen:
            fresh.append(row)
            seen.add(identity)
    if fresh:
        path.parent.mkdir(parents=True, exist_ok=True)
        needs_header = not path.exists() or path.stat().st_size == 0
        with path.open("a", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=FIELDS)
            if needs_header:
                writer.writeheader()
            writer.writerows(fresh)
    return len(fresh)


def main():
    key = os.environ.get("LTA_ACCOUNT_KEY", "").strip()
    if not key:
        raise RuntimeError("Set the LTA_ACCOUNT_KEY repository secret")
    collected_at = datetime.now(timezone(timedelta(hours=8))).isoformat(timespec="seconds")
    observations = []
    # Fetch and validate all lines before writing; failures leave the CSV unchanged.
    for line in LINES:
        rows = fetch(line, key)
        for row in rows:
            if not isinstance(row, dict) or any(
                not isinstance(row.get(field), str) or not row[field]
                for field in FIELDS[:4]
            ) or row["CrowdLevel"] not in {"l", "m", "h", "NA"}:
                raise RuntimeError(f"{line}: unexpected observation format")
            observations.append({**{field: row[field] for field in FIELDS[:4]},
                                 "TrainLine": line, "CollectedAt": collected_at})
        print(f"{line}: {len(rows)} observations")
    print(f"Saved {append_new(observations)} new observations")


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        # Only explicitly sanitized errors may be printed.
        print(str(error) if isinstance(error, RuntimeError) else
              "Collection failed; check connectivity, API format, and file access.", file=sys.stderr)
        sys.exit(1)
