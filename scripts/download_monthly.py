"""Download monthly train datasets; credentials and signed URLs are never logged."""
import json
import os
from pathlib import Path
from urllib.parse import urlencode, urlparse
from urllib.request import Request, urlopen
from zipfile import ZipFile


def main():
    month = os.environ.get("DATA_MONTH", "202609")
    if len(month) != 6 or not month.isdigit() or not 1 <= int(month[4:]) <= 12:
        raise ValueError("Use YYYYMM")
    key = os.environ.get("LTA_ACCOUNT_KEY", "").strip()
    if not key:
        raise ValueError("Missing AccountKey")
    folder = Path("downloads") / month
    folder.mkdir(parents=True, exist_ok=True)
    for endpoint, name in [("Train", "station_volumes"), ("ODTrain", "train_od_flows")]:
        url = "https://datamall2.mytransport.sg/ltaodataservice/PV/" + endpoint
        request = Request(url + "?" + urlencode({"Date": month}),
                          headers={"AccountKey": key, "accept": "application/json"})
        with urlopen(request, timeout=60) as response:
            values = json.load(response)["value"]
        link = values[0]["Link"]
        if urlparse(link).scheme != "https":
            raise ValueError("Download must use HTTPS")
        # Download without forwarding the DataMall AccountKey to the file host.
        target = folder / f"{name}_{month}.zip"
        with urlopen(link, timeout=120) as response, target.open("wb") as output:
            while chunk := response.read(1024 * 1024):
                output.write(chunk)
        with ZipFile(target) as archive:
            if archive.testzip() is not None or not any(n.lower().endswith('.csv') for n in archive.namelist()):
                raise ValueError("Invalid dataset archive")
        print(f"Downloaded and validated {name} for {month}")


if __name__ == "__main__":
    try:
        main()
    except Exception:
        raise SystemExit("Download failed. Check the secret, requested month, and DataMall availability. No credentials or download links were printed.")
