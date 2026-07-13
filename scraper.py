import time
import json
import os
import argparse
import concurrent.futures
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

from videogame import VideoGame


NINTENDO_CONSOLES = [
    "super-nintendo", "nes", "nintendo-64", "gamecube", "wii", "wii-u",
    "nintendo-switch", "nintendo-switch-2", "gameboy", "gameboy-color", "gameboy-advance",
    "nintendo-ds", "nintendo-3ds", "virtual-boy", "game-&-watch",
]

SONY_CONSOLES = [
    "playstation", "playstation-2", "playstation-3", "playstation-4",
    "playstation-5", "psp", "playstation-vita",
]

XBOX_CONSOLES = [
    "xbox", "xbox-360", "xbox-one", "xbox-series-x"
]

ATARI_CONSOLES = [
    "atari-2600", "atari-5200", "atari-7800", "atari-400", "atari-lynx", "jaguar",
]

NEO_GEO_CONSOLES = [
    "neo-geo-mvs", "neo-geo-aes", "neo-geo-cd", "neo-geo-pocket-color"
]

SEGA_CONSOLES = [
    "sega-master-system", "sega-genesis", "sega-32x", "sega-cd",
    "sega-saturn", "sega-dreamcast", "sega-game-gear", "sega-pico"
]

CONSOLES = [
    *NINTENDO_CONSOLES,
    *SONY_CONSOLES,
    *XBOX_CONSOLES,
    *ATARI_CONSOLES,
    *NEO_GEO_CONSOLES,
    *SEGA_CONSOLES,
]


def make_browser():
    """Creates a headless Chrome browser instance configured for WSL/Linux."""
    print("Making browser...")
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=options)


def scroll_to_bottom(browser, pause_time):
    """Scrolls to the bottom of the page repeatedly until no new content loads.

    pricecharting.com lazy-loads games in batches, so we keep scrolling until
    the page height has been stable for STABLE_SCROLL_COUNT consecutive checks.

    Args:
        browser: the browser instance
        pause_time: time to wait between scrolls
    """
    prev_height = browser.execute_script("return document.body.scrollHeight")
    stable_count = 0
    # Number of consecutive times height must be unchanged before we consider the page fully loaded.
    # Guards against lag between scroll and content render.
    STABLE_SCROLL_COUNT = 3

    while stable_count < STABLE_SCROLL_COUNT:
        browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(pause_time)
        curr_height = browser.execute_script("return document.body.scrollHeight")
        if curr_height == prev_height:
            stable_count += 1
        else:
            stable_count = 0
        prev_height = curr_height


def scrape_console(console, pause_time):
    """Opens the pricecharting page for a console, scrolls to load all games,
    then parses and returns a list of VideoGame objects.

    Args:
        console: console slug as it appears in the pricecharting.com URL
        pause_time: time to wait between scrolls

    Returns:
        list of VideoGame objects
    """
    print(f"[{console}] Starting scrape...")
    browser = make_browser()
    games = []

    try:
        browser.get(f"https://www.pricecharting.com/console/{console}")

        # Wait for the games table to be present before we start scrolling
        WebDriverWait(browser, 20).until(
            EC.presence_of_element_located((By.ID, "games_table"))
        )

        scroll_to_bottom(browser, pause_time)

        soup = BeautifulSoup(browser.page_source, "lxml")
        table = soup.find("table", {"id": "games_table"})

        if not table:
            print(f"[{console}] WARNING: games_table not found on page.")
            return games

        for row in table.select("tbody tr"):
            title_td = row.find("td", class_="title")
            if not title_td:
                continue

            title_tag = title_td.find("a")
            title = title_tag.get_text(strip=True) if title_tag else title_td.get_text(strip=True)

            def parse_price(css_class):
                td = row.find("td", class_=css_class)
                if not td:
                    return "N/A"
                text = td.get_text(strip=True).replace("$", "").replace(",", "")
                return text if text else "N/A"

            loose = parse_price("used_price")
            complete = parse_price("cib_price")
            new = parse_price("new_price")

            # Cover image lives in the "image" cell. The listing serves the
            # 60px thumbnail; the 240px version is the same URL with /60.jpg
            # swapped for /240.jpg (no extra request needed).
            image_small = None
            image_large = None
            image_td = row.find("td", class_="image")
            img_tag = image_td.find("img") if image_td else None
            if img_tag:
                src = img_tag.get("src") or img_tag.get("data-src")
                if src:
                    image_small = src
                    image_large = src.replace("/60.jpg", "/240.jpg")

            games.append(VideoGame(title, console, loose, complete, new,
                                   image_small, image_large))

        print(f"[{console}] Done — {len(games)} games scraped.")
    except Exception as exc:
        print(f"[{console}] ERROR: {exc}")
    finally:
        browser.quit()

    return games


def write_json(console, games, output_dir, date):
    """Writes one console's games to a dated JSON file.

    The file is a flat list of games; the console and scrape date are carried
    by the filename (DD-MM-YYYY-<console>.json) rather than repeated inside.

    Args:
        console: console slug (used in the filename)
        games: list of VideoGame objects for this console
        output_dir: directory to write the file into
        date: scrape date string in DD-MM-YYYY form

    Returns:
        the path of the file written
    """
    filename = os.path.join(output_dir, f"{date}-{console}.json")
    data = [g.to_dict() for g in games]

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"JSON written to {os.path.abspath(filename)} ({len(games)} games)")
    return filename


def main():
    parser = argparse.ArgumentParser(description="Scrape video game prices from pricecharting.com")
    parser.add_argument(
        "--workers",
        type=int,
        default=1,
        help="Number of concurrent browser instances (default: 1). Increase with caution on WSL."
    )
    parser.add_argument(
        "--console",
        type=str,
        default=None,
        help="Scrape a single console by name (e.g. --console super-nintendo). Omit to scrape all consoles."
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default=".",
        help="Directory for the output JSON files (default: current directory). "
             "Each console is written to <DD-MM-YYYY>-<console>.json."
    )
    parser.add_argument(
        "--pause",
        type=float,
        default=1.5,
        help="Seconds to wait between scrolls (default: 1.5). Increase if games are not fully loading."
    )
    args = parser.parse_args()
    
    if args.console:
        target_consoles = [args.console]
    else:
        target_consoles = CONSOLES
        
    if args.console and args.console not in CONSOLES:
        print(f"WARNING: '{args.console}' is not in the known CONSOLES list. Proceeding anyway...")

    os.makedirs(args.output_dir, exist_ok=True)
    date = datetime.now().strftime("%d-%m-%Y")

    print(f"Scraping values from pricecharting.com (max_workers={args.workers})\n")
    total_games = 0

    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as executor:
        future_to_console = {
            executor.submit(scrape_console, console, args.pause): console
            for console in target_consoles
        }
        for future in concurrent.futures.as_completed(future_to_console):
            console = future_to_console[future]
            try:
                games = future.result()
                write_json(console, games, args.output_dir, date)
                total_games += len(games)
            except Exception as exc:
                print(f"[{console}] Unhandled exception: {exc}")

    print(f"\nFinished — {total_games} total games across {len(target_consoles)} console(s).")


if __name__ == "__main__":
    main()
