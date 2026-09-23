import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()
ADMIN_ID = os.getenv("ADMIN_ID", "").strip()
PRINTER_NAME = os.getenv("PRINTER_NAME", "").strip()
PRICE_PER_PAGE_BW = int(os.getenv("PRICE_PER_PAGE_BW", "200"))
PRICE_PER_PAGE_COLOR = int(os.getenv("PRICE_PER_PAGE_COLOR", "500"))

BASE_DIR = Path(__file__).parent
DOWNLOAD_DIR = BASE_DIR / os.getenv("DOWNLOAD_DIR", "downloads")
DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)
