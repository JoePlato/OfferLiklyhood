import asyncio
import html
import os
import re
import time
from datetime import datetime

import aiohttp
import pandas as pd
import undetected_chromedriver as uc
from tqdm import tqdm
from tqdm.asyncio import tqdm_asyncio

# --- CONFIGURATION ---
START_YEAR = 2017
END_YEAR = 2027
CONCURRENT_LIMIT = 15
OUTPUT_FILE = "g6_research_data.xlsx"
LOG_FILE = "scraper_log.txt"

# --- DEBUG ----
MAX_PLAYER_PROCESS = -1
DEBUT_OUTPUT_NAME = f"g6_research_data_{MAX_PLAYER_PROCESS}_players.xlsx"


P4_SCHOOLS = {
    "Alabama", "Arkansas", "Auburn", "Florida", "Georgia", "Kentucky", "LSU",
    "Mississippi State", "Missouri", "Oklahoma", "Ole Miss", "South Carolina",
    "Tennessee", "Texas", "Texas A&M", "Vanderbilt", "Illinois", "Indiana",
    "Iowa", "Maryland", "Michigan", "Michigan State", "Minnesota", "Nebraska",
    "Northwestern", "Ohio State", "Oregon", "Penn State", "Purdue", "Rutgers",
    "UCLA", "USC", "Washington", "Wisconsin", "Boston College", "California",
    "Clemson", "Duke", "Florida State", "Georgia Tech", "Louisville", "Miami",
    "North Carolina", "NC State", "Pittsburgh", "SMU", "Stanford", "Syracuse",
    "Virginia", "Virginia Tech", "Wake Forest", "Notre Dame", "Arizona",
    "Arizona State", "Baylor", "BYU", "Cincinnati", "Colorado", "Houston",
    "Iowa State", "Kansas", "Kansas State", "Oklahoma State", "TCU",
    "Texas Tech", "UCF", "Utah", "West Virginia", "Oregon State"
}

G5_SCHOOLS = {
    "Army", "Charlotte", "East Carolina", "Florida Atlantic", "Memphis",
    "Navy", "North Texas", "Rice", "South Florida", "Temple", "Tulane",
    "Tulsa", "UAB", "UTSA", "Wichita State", "FIU", "Jacksonville State",
    "Liberty", "Louisiana Tech", "Middle Tennessee", "New Mexico State",
    "Sam Houston", "UTEP", "Western Kentucky", "Kennesaw State", "Akron",
    "Ball State", "Bowling Green", "Buffalo", "Central Michigan",
    "Eastern Michigan", "Kent State", "Miami (OH)", "Northern Illinois",
    "Ohio", "Toledo", "Western Michigan", "Air Force", "Boise State",
    "Colorado State", "Fresno State", "Hawaii", "Nevada", "New Mexico",
    "San Diego State", "San Jose State", "UNLV", "Utah State", "Wyoming",
    "Appalachian State", "Arkansas State", "Coastal Carolina",
    "Georgia Southern", "Georgia State", "James Madison", "Louisiana",
    "Louisiana-Monroe", "Marshall", "Old Dominion", "South Alabama",
    "Southern Miss", "Texas State", "Troy", "UConn", "UMass", "USF",
    "Oregon State", "Washington State"
}


ALL_D1_SCHOOLS = P4_SCHOOLS | G5_SCHOOLS

D1_MAPPING = {s.lower(): s for s in ALL_D1_SCHOOLS}
SORTED_LOWER_D1_SCHOOLS = sorted(D1_MAPPING.keys(), key=len, reverse=True)


def get_team_from_string(text):
    text = text.lower().strip()
    for school in SORTED_LOWER_D1_SCHOOLS:
        if text.startswith(school):
            if len(text) == len(school) or not text[len(school)].isalnum():
                return D1_MAPPING[school]
    return "Unknown"


def log_message(message: str):
    """
    Writes diagnostic status updates out to a local tracking text file.
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {message}\n")


def get_selenium_cookies(url):
    """
    Launches an optimized headless browser to extract security tokens.
    """
    log_message(f"VISITING MAIN WEBSITE VIA SELENIUM: {url}")
    options = uc.ChromeOptions()
    options.page_load_strategy = 'eager'
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")

    driver = None
    cookies, user_agent = {}, ""

    try:
        driver = uc.Chrome(options=options, version_main=122)
        driver.set_page_load_timeout(25)
        driver.get(url)
        time.sleep(3)
        cookies = {c['name']: c['value'] for c in driver.get_cookies()}
        user_agent = driver.execute_script("return navigator.userAgent;")
        log_message("SUCCESSFULLY RETRIEVED COOKIES AND USER AGENT SIGNATURES")
    except Exception as e:
        log_message(f"CRITICAL ERROR EXTRACTING INITIAL COOKIES: {e}")
    finally:
        if driver:
            try:
                driver.quit()
            except Exception:
                pass
            try:
                driver.quit = lambda: None
            except Exception:
                pass
    return cookies, user_agent


def parse_timeline_date(date_str):
    """
    Converts literal string expressions into valid datetime object metrics.
    """
    date_str = date_str.strip()
    for fmt in ("%b %d, %Y", "%B %d, %Y"):
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    return None


def apply_timeline_logic(player, events, raw_offer_dict):
    """
    Universal state machine. Processes timelines regardless of whether
    the data came from the live scraper or the offline text log.
    Old reliable commit/sign logic combined with new flip lookaheads.
    """
    timeline_metrics = {
        "Total_Offers": 0, "P4_Offers": 0, "G6_Offers": 0,
        "All_Offers_List": "None",
        "Commit_Date": "N/A", "Decommit_Date": "N/A",
        "Sign_Date": "N/A", "Signed_School": "N/A",
        "Flip_Count": 0, "Flipped_From": "N/A",
        "Last_Commit": "Uncommitted"
    }

    events.reverse()  # Oldest to Newest

    ignore_tags = {
        "transfer", "draft", "update", "accolades",
        "unofficial visit", "junior day", "coach visit",
        "rating", "official visit", "school camp"
    }

    valid_events = []
    filtered_offer_dict = {}
    did_enroll = False

    # 1. Filter out ignored events but keep all chronological events
    for ev in events:
        tag = ev["type"].lower()

        if tag in ignore_tags:
            continue

        valid_events.append(ev)

        if tag == "enrollment":
            did_enroll = True
        if tag == "offer" and ev["team"] != "Unknown":
            filtered_offer_dict[ev["team"]] = ev["date_str"]

    # Inject raw graphic offers that didn't have parsed dates
    for team, date_str in raw_offer_dict.items():
        if team not in filtered_offer_dict:
            filtered_offer_dict[team] = date_str

    flipped_schools_list = []

    # 2. Process commit, decommit, and sign logic
    for idx in range(len(valid_events)):
        current = valid_events[idx]
        tag = current["type"].lower()
        team = current["team"]

        # --- NEW LOGIC: Decommits and Flips (Lookahead) ---
        if tag in ("decommit", "decommitment"):
            timeline_metrics["Decommit_Date"] = current["date_str"]
            timeline_metrics["Last_Commit"] = "Uncommitted"

            # Peek ahead up to 5 events to find the flip destination
            for j in range(idx + 1, min(idx + 5, len(valid_events))):
                nxt = valid_events[j]
                nxt_tag = nxt["type"].lower()
                day_gap = abs((nxt["date"] - current["date"]).days)

                if day_gap > 1:
                    break

                if nxt_tag in ("commitment", "signing", "enrollment"):
                    if team != nxt["team"] and team != "Unknown":
                        timeline_metrics["Flip_Count"] += 1
                        flipped_schools_list.append(team)
                    break

        # --- OLD RELIABLE LOGIC: Commits, Signings, Enrollments ---
        elif tag == "commitment":
            timeline_metrics["Commit_Date"] = current["date_str"]
            timeline_metrics["Last_Commit"] = team
            # Implicit Offer Injection
            if team != "Unknown" and team not in filtered_offer_dict:
                filtered_offer_dict[team] = "Unknown"

        elif tag in ("signing", "enrollment"):
            timeline_metrics["Sign_Date"] = current["date_str"]
            timeline_metrics["Signed_School"] = team
            timeline_metrics["Last_Commit"] = team
            # Implicit Offer Injection
            if team != "Unknown" and team not in filtered_offer_dict:
                filtered_offer_dict[team] = "Unknown"

    # 3. Final verification and formatting
    if not did_enroll:
        timeline_metrics["Sign_Date"] = "N/A"
        timeline_metrics["Signed_School"] = "N/A"

    if flipped_schools_list:
        timeline_metrics["Flipped_From"] = ", ".join(flipped_schools_list)

    timeline_metrics["Total_Offers"] = len(filtered_offer_dict)

    # Calculate P4/G6 classifications
    timeline_metrics["P4_Offers"] = len(
        [t for t in filtered_offer_dict.keys() if t in P4_SCHOOLS]
    )
    timeline_metrics["G6_Offers"] = len(
        [t for t in filtered_offer_dict.keys() if t in G5_SCHOOLS]
    )

    if filtered_offer_dict:
        formatted_offers = [
            f"{team} ({date})" for team, date in filtered_offer_dict.items()
        ]
        timeline_metrics["All_Offers_List"] = ", ".join(
            sorted(formatted_offers)
        )

    player.update(timeline_metrics)
    return player


class TwoFourSevenScraper:
    """
    Core engineering module optimized to map player timelines across multiple eras.
    """
    def __init__(self, cookies, user_agent):
        self.cookies = cookies
        self.headers = {"User-Agent": user_agent, "Accept": "application/json"}

    async def fetch_json_page(self, session, year, page, retries=3):
        """
        Gathers raw master registry listings directly from endpoint tables.
        """
        url = f"https://247sports.com/season/{year}-football/recruits.json"
        params = {'Items': 25, 'Page': page, 'Conf': 'all'}

        for attempt in range(retries):
            try:
                async with session.get(
                    url, params=params, cookies=self.cookies
                ) as resp:
                    if resp.status == 200:
                        return await resp.json()
                    elif resp.status in (403, 429):
                        await asyncio.sleep(5 * (attempt + 1))
            except Exception:
                await asyncio.sleep(2)
        return []

    async def gather_all_timeline_events(self, session, player_url,
                                         player_name):
        """
        Scans a recruit's history subpages strictly using text chunking.
        Optimized by removing expensive graphic offer regex parsing.
        """
        all_parsed_events = []
        offer_dict = {}

        if not player_url:
            return all_parsed_events, offer_dict

        base_timeline_url = f"{player_url.rstrip('/')}/timelineevents/"
        current_page = 1

        # We only need the date header pattern and next button pattern now
        date_header_pat = re.compile(
            r'([A-Z][a-z]+\s+\d{1,2},\s+\d{4}):\s*([A-Za-z0-9_\-\s]+)'
        )
        next_button_pat = re.compile(r'>Next\s*</', re.IGNORECASE)
        # Compiles all markers into a single OR (|) operation at the C-level
        footer_pat = re.compile(
            r'(?:CBS Sports Digital|YouTube|Facebook|X |Instagram|TikTok|'
            r'Podcast)', re.IGNORECASE
        )

        while True:
            target_url = f"{base_timeline_url}?Page={current_page}"
            log_message(
                f"HTTP REQUEST FIRED TO SITE: {target_url} FOR PLAYER: "
                f"{player_name}"
            )

            try:
                async with session.get(
                    target_url, cookies=self.cookies
                ) as resp:
                    if resp.status != 200:
                        log_message(
                            f"HTTP REQUEST FAILED WITH STATUS CODE: "
                            f"{resp.status}"
                        )
                        break

                    html_content = await resp.text()

                    # Find all Date: Event headers directly in the HTML
                    matches = list(date_header_pat.finditer(html_content))
                    log_message(
                        f"READ LOG: DISCOVERED {len(matches)} HISTORICAL "
                        f"EVENTS ON PAGE {current_page}"
                    )

                    for idx, match in enumerate(matches):
                        date_str = match.group(1)
                        event_type = match.group(2).strip()

                        # Chunk the HTML between this date and the next date
                        start_pos = match.end()
                        # Limit the chunk to 500 characters max
                        end_pos = (
                            matches[idx + 1].start()
                            if idx + 1 < len(matches)
                            else start_pos + 500
                        )
                        chunk = html_content[start_pos:end_pos]

                        # 1. Strip HTML and normalize whitespace
                        clean_snippet = " ".join(
                            re.sub(r'<[^>]+>', ' ', chunk).split()
                        )[:120]
                        # Strip trailing periods just in case
                        clean_snippet_lower = clean_snippet.lower().strip(" .")

                        team_name = "Unknown"
                        event_type = match.group(2).strip()
                        tag = event_type.lower()

                        ignore_tags = {
                            "transfer", "draft", "update", "accolades",
                            "unofficial visit", "junior day", "coach visit",
                            "rating", "official visit", "school camp"
                        }

                        if tag in ignore_tags:
                            pass  # Leaves team_name as "Unknown"

                        elif tag == "offer":
                            if "offer" in clean_snippet_lower:
                                prefix = clean_snippet_lower.split(
                                    "offer", 1
                                )[0]
                                # Safely strip broken HTML or pagination
                                prefix = prefix.split("...")[0].split(
                                    "<"
                                )[0].strip()

                                # Shrinking Array Search
                                parts = prefix.split()
                                for i in range(len(parts), 0, -1):
                                    candidate = " ".join(parts[:i])
                                    if candidate in D1_MAPPING:
                                        team_name = D1_MAPPING[candidate]
                                        break

                        elif tag in (
                            "commitment", "decommitment", "decommit",
                            "enrollment", "signing"
                        ):
                            if tag in ("decommit", "decommitment"):
                                separator = "decommits from"
                            elif tag == "commitment":
                                separator = "commits to"
                            elif tag == "enrollment":
                                separator = "enrolls at"
                            elif tag == "signing":
                                separator = (
                                    "signs letter of intent to"
                                    if "signs letter of intent to"
                                    in clean_snippet_lower
                                    else "signs with"
                                )
                            else:
                                separator = ""

                            if separator and separator in clean_snippet_lower:
                                suffix = clean_snippet_lower.split(
                                    separator, 1
                                )[-1]
                                # Safely strip broken HTML or pagination
                                suffix = suffix.split("...")[0].split(
                                    "<"
                                )[0].strip()

                                # Shrinking Array Search
                                parts = suffix.split()
                                for i in range(len(parts), 0, -1):
                                    candidate = " ".join(parts[:i])
                                    if candidate in D1_MAPPING:
                                        team_name = D1_MAPPING[candidate]
                                        break

                        log_message(
                            f"  READ RECORD -> DATE: {date_str} | TYPE: "
                            f"{event_type} | TEAM: {team_name} | SNIPPET: "
                            f"{clean_snippet}"
                        )

                        # 3. Save to timeline
                        parsed_date = parse_timeline_date(date_str)
                        if parsed_date:
                            all_parsed_events.append({
                                "date": parsed_date,
                                "date_str": date_str,
                                "type": event_type,
                                "team": team_name
                            })

                            # Add standard offers straight into the dictionary
                            if (
                                event_type.lower() == "offer"
                                and team_name != "Unknown"
                            ):
                                offer_dict[team_name] = date_str

                    if next_button_pat.search(html_content):
                        log_message(
                            f"PAGINATION SIGNATURE 'NEXT' FOUND. ADVANCING "
                            f"TO PAGE {current_page + 1}"
                        )
                        current_page += 1
                    else:
                        log_message(
                            "PAGINATION SIGNATURE 'NEXT' NOT FOUND. "
                            "TERMINATING RECRUIT LOOP."
                        )
                        break

            except Exception as e:
                log_message(
                    f"EXCEPTION ENCOUNTERED DURING TIMELINE PARSE LOOP: {e}"
                )
                break

        return all_parsed_events, offer_dict

    async def process_historical_profile(self, session, player):
        events, raw_offer_dict = await self.gather_all_timeline_events(
            session, player["Profile_URL"], player["Name"]
        )
        return apply_timeline_logic(player, events, raw_offer_dict)

    async def collect_year_data(self, semaphore, session, year):
        """
        Indexes primary user profiles before gathering historical logs.
        """
        discovered_recruits = []
        page = 1

        with tqdm(desc=f"Class of {year} Indexing", unit="pg") as pbar:
            while True:
                async with semaphore:
                    data = await self.fetch_json_page(session, year, page)
                if not data:
                    break

                for item in data:
                    player_info = item.get('Player', {})
                    if not player_info:
                        continue

                    hometown = player_info.get('Hometown') or {}
                    city = hometown.get('City', 'N/A')
                    state_full = hometown.get('State', 'N/A')

                    pos_abbr = 'N/A'
                    candidates = [
                        player_info.get('PrimaryPlayerPosition'),
                        player_info.get('Position'),
                        item.get('PrimaryPlayerPosition'),
                        item.get('Position')
                    ]

                    for candidate in candidates:
                        if isinstance(candidate, dict):
                            pos_abbr = candidate.get('Abbreviation', 'N/A')
                            break

                    if pos_abbr in ("DUAL", "PRO"):
                        pos_abbr = "QB"

                    discovered_recruits.append({
                        "Name": player_info.get('FullName'),
                        "Class_Year": year,
                        "Hometown": f"{city}, {state_full}",
                        "Position": pos_abbr,
                        "Stars": player_info.get('StarRating', 0),
                        "Profile_URL": player_info.get('Url')
                    })
                pbar.update(1)
                page += 1

        print(
            f"Processing structural history records for the class of {year}..."
        )
        tasks = [
            self.process_historical_profile(session, p)
            for p in discovered_recruits
        ]
        return await tqdm_asyncio.gather(*tasks, desc=f"Timelines {year}")


async def process_batch_timelines(scraper, semaphore, session, registry):
    """
    Processes timelines for a pre-loaded list of players.
    Wraps the extraction process in a semaphore to prevent network overload.
    """
    tasks = []

    for player in registry:
        # Bounded task handling matching the architecture rules
        async def bounded_process(p):
            async with semaphore:
                return await scraper.process_historical_profile(session, p)
        tasks.append(bounded_process(player))
        if MAX_PLAYER_PROCESS != -1 and len(tasks) == MAX_PLAYER_PROCESS:
            break

    log_message(
        f"Resuming state from local cache. Fetching timelines for "
        f"{len(tasks)} players..."
    )
    print(
        f"Resuming from local file. Fetching timelines for "
        f"{len(tasks)} players..."
    )

    return await tqdm_asyncio.gather(
        *tasks, desc="Timeline Extraction", unit="player"
    )


async def main():
    # Fetch structural access tokens using the automated driver sequence
    cookies, user_agent = get_selenium_cookies(
        "https://247sports.com/season/2022-football/recruits/"
    )

    semaphore = asyncio.Semaphore(CONCURRENT_LIMIT)
    scraper = TwoFourSevenScraper(cookies, user_agent)
    master_registry = []

    # Initialize a clean persistent connection pooling model
    async with aiohttp.ClientSession(headers=scraper.headers) as session:

        # === FIX: State Resumption Logic ===
        if os.path.exists(OUTPUT_FILE):
            print(
                f"Local file '{OUTPUT_FILE}' detected. Skipping directory "
                f"indexing."
            )

            # Read the existing data and replace empty Excel cells with "N/A"
            df = pd.read_excel(OUTPUT_FILE)
            df = df.fillna("N/A")

            # Convert the dataframe back into a list of dictionaries
            loaded_players = df.to_dict('records')

            # Pass the loaded players directly to the timeline processor
            master_registry = await process_batch_timelines(
                scraper, semaphore, session, loaded_players
            )

        else:
            print(
                "No local data found. Starting full directory extraction "
                "from scratch."
            )
            for year in range(START_YEAR, END_YEAR + 1):
                year_output = await scraper.collect_year_data(
                    semaphore, session, year
                )
                master_registry.extend(year_output)

    print(f"Exporting compiled research results to sheet: {OUTPUT_FILE}")

    # Save the updated records back to the Excel file
    final_df = pd.DataFrame(master_registry)
    if MAX_PLAYER_PROCESS != -1:
        final_df.to_excel(DEBUT_OUTPUT_NAME, index=False)
    else:
        final_df.to_excel(OUTPUT_FILE, index=False)

    print(
        f"Process complete. Check '{LOG_FILE}' to see exact parsing "
        f"diagnostics."
    )


if __name__ == "__main__":
    # THE FIX: The log file is safely cleared ONLY running scraper directly
    if os.path.exists(LOG_FILE):
        os.remove(LOG_FILE)

    asyncio.run(main())