# MRT crowd-density logger

Collects LTA DataMall PCDRealTime observations every 30 minutes, at minutes 07 and 37 of each hour (UTC; also 07 and 37 in Singapore). Python 3.12's standard library is sufficient; no packages to install.

## Repository layout

Upload the CONTENTS of this folder to the repository root, including the hidden `.github` directory:

```text
.github/workflows/collect-crowd.yml
scripts/log_crowd_density.py
data/crowd_density_log.csv
.gitignore
README.md
```

## Activate on GitHub

1. Create a GitHub repository, or use your existing project repository. Commit these files to its default branch (usually `main`). Preserve the paths above: the workflow must be at `.github/workflows/collect-crowd.yml`, not inside a nested `mrt-crowd-logger` folder.
2. Obtain an LTA DataMall AccountKey through https://datamall.lta.gov.sg/. Do not put the key in source files, CSV, commits, screenshots, or chat.
3. In the repository, open **Settings → Secrets and variables → Actions → New repository secret**. Name it **LTA_ACCOUNT_KEY** and paste the AccountKey as its value. The workflow provides it only to the collection step as an environment variable.
4. Ensure GitHub Actions is enabled and repository/organization policy permits the workflow's `contents: write` permission. The built-in GITHUB_TOKEN handles commits; no personal access token is needed. Branch protection/rules must permit the bot to push to the default branch. If your project requires PRs, use a dedicated collection repository whose default branch permits bot writes.
5. Open **Actions → Collect MRT crowd density → Run workflow**. Select the default branch. A successful run creates a bot commit when new observations exist. Check the CSV and the run's collection counts. Subsequent runs happen automatically; your laptop can be off.

## Data behavior

Columns are Station, StartTime, EndTime, CrowdLevel, TrainLine, and CollectedAt. CollectedAt includes Singapore's +08:00 offset. API interval timestamps are preserved. CrowdLevel means `l` low, `m` moderate, `h` high, or `NA` unavailable. This is station crowdedness, not passenger counts.

All 11 documented MRT/LRT line codes are queried, including extensions. Edit LINES in the script if you want MRT only. Empty results are accepted and produce no fabricated observations. Transient failures retry with bounded waits and request timeouts; any failed line or malformed response fails the run before appending. The script never prints the key or raw API responses.

Exact repeats are skipped using station, interval, crowd level, and line. A changed crowd level for the same interval is retained as a separate observation; analysis should use CollectedAt to choose the latest version when needed. Only the CSV is staged for the bot commit. Workflow runs are serialized; a concurrent conflicting human edit can still cause a visible failed push/rebase.

This builds history from activation onward. A 30-minute sample misses some 10-minute API intervals; it cannot recover observations from missed runs. Change cron to `7,17,27,37,47,57 * * * *` for a 10-minute target, with more Actions usage and commits. Monitor Actions usage/billing, run failures, CSV growth, and gaps. Scheduled runs can be delayed or dropped, run only from the default branch, and public-repository schedules may be disabled after 60 days without repository activity.

## Sources

- LTA endpoint, line codes, fields, and update frequency: https://datamall.lta.gov.sg/content/dam/datamall/datasets/LTA_DataMall_API_User_Guide.pdf
- GitHub Secrets setup: https://docs.github.com/en/actions/how-tos/write-workflows/choose-what-workflows-do/use-secrets
- Scheduling behavior: https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#schedule

No live API validation is possible until you configure your own AccountKey and run the workflow.
