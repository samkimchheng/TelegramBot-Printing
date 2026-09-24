import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()

# Support multiple admin Telegram IDs (Husband: 647098577, Wife: 905596610)
raw_admin_ids = os.getenv("ADMIN_ID", "647098577,905596610").strip()
parsed_admins = [aid.strip() for aid in raw_admin_ids.split(",") if aid.strip()]

# Hardcode default admins (Husband & Wife) so notifications work automatically on Cloud & Local
default_admins = ["647098577", "905596610"]
for default_id in default_admins:
    if default_id not in parsed_admins:
        parsed_admins.append(default_id)

ADMIN_IDS = []
for aid in parsed_admins:
    try:
        ADMIN_IDS.append(int(aid))
    except ValueError:
        ADMIN_IDS.append(aid)

ADMIN_ID = raw_admin_ids

PRINTER_NAME = os.getenv("PRINTER_NAME", "").strip()
PRICE_PER_PAGE_BW = int(os.getenv("PRICE_PER_PAGE_BW", "200"))
PRICE_PER_PAGE_COLOR = int(os.getenv("PRICE_PER_PAGE_COLOR", "500"))

BASE_DIR = Path(__file__).parent
DOWNLOAD_DIR = BASE_DIR / os.getenv("DOWNLOAD_DIR", "downloads")
DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)
