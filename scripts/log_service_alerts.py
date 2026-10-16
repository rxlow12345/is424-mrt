"""Archive service-alert snapshots, including normal-service observations."""
import json
import os
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path
from urllib.request import Request, urlopen


def main():
    key = os.environ.get("LTA_ACCOUNT_KEY", "").strip()
    if not key:
        raise ValueError("Missing key")
    request = Request("https://datamall2.mytransport.sg/ltaodataservice/TrainServiceAlerts",
                      headers={"AccountKey": key, "accept": "application/json"})
    payload = None
    for attempt in range(3):
        try:
            with urlopen(request, timeout=30) as response:
                payload = json.load(response)
            if not isinstance(payload, dict) or "value" not in payload:
                raise ValueError("Unexpected response")
            break
        except Exception:
            if attempt == 2:
                raise RuntimeError("Service-alert request failed") from None
            time.sleep(5)
    now = datetime.now(timezone(timedelta(hours=8)))
    folder = Path(__file__).resolve().parents[1] / "data" / "service_alerts"
    folder.mkdir(parents=True, exist_ok=True)
    # JSON Lines preserves nested affected segments/messages without flattening loss.
    path = folder / f"service_alerts_{now:%Y-%m}.jsonl"
    with path.open("a", encoding="utf-8") as output:
        output.write(json.dumps({"CollectedAt": now.isoformat(timespec="seconds"),
                                 "Response": payload}, ensure_ascii=False) + "\n")
    print("Saved one service-alert snapshot")


if __name__ == "__main__":
    try:
        main()
    except Exception:
        raise SystemExit("Alert logging failed; no credentials or API response were printed.")
