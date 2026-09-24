import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()

# Support multiple admin Telegram IDs separated by comma (e.g. Husband & Wife)
raw_admin_ids = os.getenv("ADMIN_ID", "647098577").strip()
ADMIN_IDS = [aid.strip() for aid in raw_admin_ids.split(",") if aid.strip()]

PRINTER_NAME = os.getenv("PRINTER_NAME", "").strip()
PRICE_PER_PAGE_BW = int(os.getenv("PRICE_PER_PAGE_BW", "200"))
PRICE_PER_PAGE_COLOR = int(os.getenv("PRICE_PER_PAGE_COLOR", "500"))

BASE_DIR = Path(__file__).parent
DOWNLOAD_DIR = BASE_DIR / os.getenv("DOWNLOAD_DIR", "downloads")
DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)
