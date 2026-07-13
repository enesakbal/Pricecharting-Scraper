# Pricecharting Scraper

> Uses web scraping to pull loose, CIB, and new market values (plus cover images) for video games from pricecharting.com and outputs them to one JSON file per console.

## Requirements

- Python 3.8+
- Google Chrome installed

On WSL/Ubuntu:

```bash
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo apt install ./google-chrome-stable_current_amd64.deb
```

## Setup

MacOS/Linux

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Windows

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

## Usage

```bash
python3 scraper.py [--console CONSOLE] [--output-dir DIR] [--workers N] [--pause SECONDS]
```

Each console is written to its own file named `<DD-MM-YYYY>-<console>.json`
(the scrape date followed by the console slug), e.g. `13-07-2026-virtual-boy.json`.

### Arguments

| Argument       | Default             | Description                                                                            |
| -------------- | ------------------- | ------------------------------------------------------------------------------------- |
| `--console`    | _(all consoles)_    | Scrape a single console by slug (e.g. `super-nintendo`). Omit to scrape all consoles.  |
| `--output-dir` | _(current dir)_     | Directory for the output JSON files. One `<DD-MM-YYYY>-<console>.json` file per console.|
| `--workers`    | `1`                 | Number of concurrent browser instances. See note below before increasing.             |
| `--pause`      | `1.5`               | Seconds to wait between scroll attempts. Increase if games are not fully loading.      |

### Examples

```bash
# Scrape all consoles, one JSON file per console in the current directory
python3 scraper.py

# Scrape a single console (writes e.g. 13-07-2026-super-nintendo.json)
python3 scraper.py --console super-nintendo

# Scrape a single console into a specific directory
python3 scraper.py --console nintendo-64 --output-dir ./data

# Increase scroll pause time (useful if games aren't fully loading)
python3 scraper.py --console nes --pause 3.0
```

### A note on `--workers`

By default the scraper runs one console at a time. You can increase `--workers` to scrape multiple consoles concurrently, but be aware:

- Each worker spawns a full headless Chrome instance. On WSL, RAM is limited and multiple Chrome instances compete for CPU.
- Under high CPU load, the page's lazy-loading may not fire within the pause window, resulting in only the first ~100 games being scraped per console.
- If you increase workers, also increase `--pause` to compensate (e.g. `--workers 3 --pause 3.0`).

## Consoles Scraped

By default, all major NTSC consoles are scraped:

**Nintendo:** NES, SNES, N64, GameCube, Wii, Wii U, Switch, Switch 2, Game Boy, Game Boy Color, Game Boy Advance, DS, 3DS, Virtual Boy, Game & Watch

**Sony:** PlayStation, PS2, PS3, PS4, PS5, PSP, PS Vita

**Microsoft:** Xbox, Xbox 360, Xbox One, Xbox Series X

**Sega:** Master System, Genesis, 32X, CD, Saturn, Dreamcast, Game Gear, Pico

**Atari:** 2600, 5200, 7800, 400, Lynx, Jaguar

**SNK:** Neo Geo MVS, Neo Geo AES, Neo Geo CD, Neo Geo Pocket Color

## JSON Format

Each output file is a **flat list** of games for one console. The console slug
and scrape date are carried by the filename (`<DD-MM-YYYY>-<console>.json`), so
they are not repeated inside the file.

```json
[
  {
    "game": "Jack Bros.",
    "loose": "867.90",
    "complete": "2000.00",
    "new": "4000.00",
    "image": {
      "small": "https://storage.googleapis.com/images.pricecharting.com/…/60.jpg",
      "large": "https://storage.googleapis.com/images.pricecharting.com/…/240.jpg"
    }
  }
]
```

| Field            | Description                                                        |
| ---------------- | ----------------------------------------------------------------- |
| `game`           | Game title                                                        |
| `loose`          | Loose / cartridge-only price (string; `"N/A"` when unlisted)      |
| `complete`       | Complete in box (CIB) price (string; `"N/A"` when unlisted)       |
| `new`            | New/sealed price (string; `"N/A"` when unlisted)                  |
| `image.small`    | Cover thumbnail URL (60px)                                        |
| `image.large`    | Cover image URL (240px)                                           |

When a game has no cover image, `"image"` is `null`.

## Known Limitations

- **WSL concurrency** — Running multiple workers (`--workers > 1`) on WSL can cause Chrome to crash or pages to load incompletely due to CPU and memory contention. If you see only ~100 games scraped per console, try reducing to `--workers 1` and increasing `--pause` to `2.5` or higher.
- **Apple Silicon (M1/M2/M3)** — `webdriver-manager` may download an incorrect ChromeDriver binary on ARM Macs. If Chrome fails to launch, install Chrome manually and use Selenium's built-in driver manager by removing the `Service(ChromeDriverManager().install())` call and passing only `options` to `webdriver.Chrome()`.
- **Site changes** — This scraper targets specific HTML element IDs and CSS classes on pricecharting.com. If the site updates its layout, the scraper may stop returning data or return incomplete results. If you encounter this, please [open an issue](https://github.com/markfoster314/Pricecharting-Scraper/issues/new).
- **Rate limiting** — No request throttling is implemented between consoles. Running many workers simultaneously may result in your IP being temporarily rate-limited by pricecharting.com.
- **N/A prices** — Some games do not have a listed price for all three conditions (loose, CIB, new). These are recorded as `"N/A"` in the JSON.

## Disclaimer

This project is intended for personal and educational use only. It is not affiliated with, endorsed by, or connected to [PriceCharting.com](https://www.pricecharting.com) in any way. If you need programmatic access to their data at scale, consider using their [official API](https://www.pricecharting.com/api-documentation).
Please use this tool responsibly and in accordance with PriceCharting's [terms of service](https://www.pricecharting.com/page/terms-of-service).
