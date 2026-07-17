# 247Sports Player Recruiting & Timeline Scraper

An asynchronous Python tool designed to scrap historical college football recruiting data and timeline events from 247Sports. This tool indexes player profiles for specific recruiting cycles, extracts chronological timeline milestones (offers, commitments, decommitments, signings, and enrollments), maps schools into P4/G5 athletic classifications, and tracks complex historical scenarios such as team flips.

## Features

* **Asynchronous Networking:** Built on top of `asyncio` and `aiohttp` to perform rapid, parallel network operations without choking bandwidth or hitting endpoint walls.
* **Smart Anti-Scraping Bypass:** Leverages `undetected-chromedriver` to extract initial operational cookies and user-agent signatures before handing off connections to the async HTTP connection pool.
* **State Resumption Logic:** Detects an existing spreadsheet cache upon execution. If present, it skips indexing over target years and resumes working down player timelines where it left off.
* **Contextual Tokenization:** Scans recruit milestones using fast HTML string-chunking patterns to extract exact offering, committing, and signing information without relying on heavy graphic assets.
* **Athletic Conference Classifications:** Maps major FBS programs into exact Power 4 (P4) or Group of 5 (G5) containers to calculate specific offer breakdowns for every single player.
* **Flip Lookahead Engine:** Evaluates decommitment events up to a specific frame forward to catch structural flipped-recruitment trajectories.

## Requirements

The codebase requires Python 3.8+ along with dependencies for webdriver execution, asynchronous progress tracking, and spreadsheet creation.

```bash
pip install asyncio aiohttp pandas openpyxl undetected-chromedriver tqdm
```

*Note: Google Chrome must be installed on your local machine to allow `undetected-chromedriver` to complete its initial structural handshake.*

## Configuration

You can tune execution bounds via configuration parameters directly within `player_scrapper.py`:

```python
START_YEAR = 2017                 # The start year for directory indexing
END_YEAR = 2027                   # The final year for directory indexing
CONCURRENT_LIMIT = 15             # Maximum number of concurrent async network tasks
OUTPUT_FILE = "g6_research_data.xlsx"  # Target spreadsheet storage file
LOG_FILE = "scraper_log.txt"       # File name for parsing and error logging
MAX_PLAYER_PROCESS = -1           # Set to a positive integer to test a small subset of players
```

## Architecture

The script operates through a clean pipeline:

1. **Handshake Phase:** Starts a headless Chrome instance to extract operational session cookies, closing the driver immediately after values are stored.
2. **Indexing Phase:** If no local file is found, it queries yearly recruit indexes page-by-page to aggregate foundational player metrics (Name, Class Year, Hometown, Position, Star Rating, and URL).
3. **Resumption Phase:** If a local spreadsheet is detected, the program skips indexing and converts the sheet rows into working dictionaries.
4. **Extraction Phase:** Spawns bounded asynchronous requests within a semaphore pool to traverse player timelines, run text tokenization, and update structural variables.
5. **Persistence Phase:** Groups player metrics into a Pandas DataFrame and exports clean tables into Excel format.

## Execution

Run the script directly via your terminal:

```bash
python player_scrapper.py
```

## Logging & Monitoring

* **Terminal Progress:** Monitored via clean `tqdm` progress bars broken into indexing windows and active timeline extractions.
* **Diagnostic Log File:** Real-time extraction logs and raw text snippet data are appended cleanly to `scraper_log.txt`. This file is cleared out at the launch of any non-cached scratch run.
