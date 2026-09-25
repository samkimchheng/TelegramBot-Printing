# 📘 សៀវភៅមេរៀន៖ ការបង្កើត Telegram Bot សេវាកម្មបោះពុម្ពធៀប (Telegram Bot Printing Coursebook)
**កម្រិត៖ ចាប់ពីកម្រិតដំបូង (Beginner) ដល់កម្រិតអាជីព (Production-Ready 24/7 Cloud Deployment)**
**រៀបចំ និងរចនាសម្រាប់៖ ហាង ឆេងមុនីបោះពុម្ព (Cheng Muny Printing)**

---

## 📌 មាតិកាសៀវភៅ (Table of Contents)
1. **មេរៀនទី១**៖ ការណែនាំ និងការរៀបចំប្រព័ន្ធ (Introduction & System Setup)
2. **មេរៀនទី២**៖ រចនាសម្ព័ន្ធគម្រោង (Project Architecture & Folder Structure)
3. **មេរៀនទី៣**៖ ការរៀបចំទិន្នន័យកាតាឡុក `catalog.json` (JSON Data Catalog)
4. **មេរៀនទី៤**៖ ការរៀបចំប្រព័ន្ធសុវត្ថិភាព `config.py` និង `.env` (Secure Configuration)
5. **មេរៀនទី៥**៖ ការសរសេរកូដមុខងារ Bot `bot.py` (Core Logic & Khmer Text Formatting)
6. **មេរៀនទី៦**៖ ការដំឡើង Bot លើ Cloud Render.com (24/7 Free Cloud Deployment)
7. **មេរៀនទី៧**៖ ការថែទាំ និងការកែសម្រួលបន្ថែម (Customization & Maintenance Guide)

---

## 📖 មេរៀនទី១៖ ការណែនាំ និងការរៀបចំប្រព័ន្ធ (Introduction & System Setup)

### ១.១ តើ Telegram Bot API ជាអ្វី?
Telegram Bot គឺជាគណនីស្វ័យប្រវត្តិនៃកម្មវិធី Telegram ដែលដើរតួជាអ្នកបម្រើសេវាកម្ម (Automated Assistant)។ Bot អាច៖
- ឆ្លើយតបសារ និងបង្ហាញម៉ឺនុយបញ្ជា (Interactive Keyboards)
- បង្ហាញរូបថតផលិតផល កាតាឡុក និងព័ត៌មានលម្អិត
- ទទួលព័ត៌មានកុម្ម៉ង់ និងផ្ទៀងផ្ទាត់លេខទូរស័ព្ទអតិថិជន
- ផ្ញើសារប្រាប់ម្ចាស់ហាង (Admin Alerts) ភ្លាមៗក្នុងពេលជាក់ស្តែង (Real-Time)

### ១.២ ការរៀបចំដំឡើងកម្មវិធីចាំបាច់
1. **Python 3.10+**៖ ទាញយក និងដំឡើងពី [python.org](https://www.python.org/) (សូមប្រាកដថានិមិត្តសញ្ញា `Add Python to PATH` ត្រូវបានគូសធីក)।
2. **Git**៖ កម្មវិធីគ្រប់គ្រង Version កូដ ទាញយកពី [git-scm.com](https://git-scm.com/)।
3. **VS Code**៖ កម្មវិធីសរសេរកូដ ទាញយកពី [code.visualstudio.com](https://code.visualstudio.com/)।

### ១.៣ ការបង្កើត Bot ជាមួយ `@BotFather`
1. បើកកម្មវិធី Telegram រួចស្វែងរក `@BotFather`
2. វាយបញ្ជា `/newbot`
3. វាយបញ្ចូលឈ្មោះ Bot (ឧទាហរណ៍៖ `ឆេងមុនីបោះពុម្ព Bot`)
4. វាយបញ្ចូល Username នៃ Bot (ត្រូវបញ្ចប់ដោយ `bot` ឧទាហរណ៍៖ `ChengMunyPrinting_bot`)
5. `@BotFather` នឹងផ្តល់ជូន **API Token** (ឧទាហរណ៍៖ `7890123456:AAFd...`)។ **សូមរក្សាទុក Token នេះជាការសម្ងាត់!**

### ១.៤ ការស្វែងរក Telegram User ID របស់ Admin
ដើម្បីឱ្យ Bot ស្គាល់ថាអ្នកណាជាម្ចាស់ហាងសម្រាប់ផ្ញើសារ Alert ការកុម្ម៉ង់៖
1. ស្វែងរក `@userinfobot` ក្នុង Telegram
2. វាយបញ្ជា `/start`
3. វាយចម្លងយកលេខ **Id** (ឧទាហរណ៍៖ `647098577` សម្រាប់ប្តី និង `905596610` សម្រាប់ប្រពន្ធ)។

---

## 🏗️ មេរៀនទី២៖ រចនាសម្ព័ន្ធគម្រោង (Project Architecture)

សៀវភៅនេះប្រើប្រាស់រចនាសម្ព័ន្ធ Folder ច្បាស់លាស់ ងាយស្រួលគ្រប់គ្រង៖

```text
TelegramBot Printing/
├── catalog.json              # ឯកសាររក្សាទុកទិន្នន័យម៉ូដធៀប និងតម្លៃ
├── config.py                 # ឯកសារអានព័ត៌មានកំណត់ និង Admin IDs
├── bot.py                    # ឯកសារកូដមេ (Main Logic & Handlers)
├── .env                      # ឯកសាររក្សាទុក BOT_TOKEN & Sensitive Keys
├── requirements.txt          # បញ្ជីឈ្មោះ Libraries ដែលត្រូវប្រើ
├── downloads/                # Folder រក្សាទុករូបភាព/PDF ដែលអតិថិជនផ្ញើមក
├── orders/                   # Folder រក្សាទុកឯកសារ JSON នៃរាល់ការកុម្ម៉ង់
└── sample_images/            # Folder រក្សាទុករូបថតគំរូធៀប ៨០ ម៉ូដ
```

### ២.១ ការបង្កើត Virtual Environment & Install Libraries
បើក Terminal (PowerShell / Command Prompt) ក្នុង Folder គម្រោង រួចវាយ៖

```bash
# ១. បង្កើត Virtual Environment
python -m venv venv

# ២. បើកដំណើរការ Virtual Environment (Windows)
.\venv\Scripts\activate

# ៣. ដំឡើង Libraries ចាំបាច់
pip install python-telegram-bot python-dotenv
```

---

## 📊 មេរៀនទី៣៖ ការរៀបចំទិន្នន័យកាតាឡុក `catalog.json`

ឯកសារ `catalog.json` ត្រូវរៀបចំជាប្រភេទ JSON Object ដោយបែងចែកជា Categories (ប្រភេទធៀប) និង Items (ម៉ូដធៀបនីមួយៗ)៖

```json
{
  "categories": {
    "classic": {
      "name": "ធៀបការបុរាណ (Classic)",
      "items": [
        {
          "id": "classic_01",
          "name": "ធៀបការបុរាណ ម៉ូដទី ១",
          "price": 1200,
          "description": "រចនាបែបបុរាណ ក្រដាស់ក្រាស់អក្សរមាស ឥតគិតថ្លៃសេវារចនា",
          "image": "sample_images/classic_01.jpg"
        },
        {
          "id": "classic_02",
          "name": "ធៀបការបុរាណ ម៉ូដទី ២",
          "price": 1200,
          "description": "ម៉ូដបុរាណប្រណិត ក្រដាស់ក្លិនក្រអូប ផ្កាយផ្លេកៗ",
          "image": "sample_images/classic_02.jpg"
        }
      ]
    },
    "modern": {
      "name": "ធៀបការសម័យទំនើប (Modern)",
      "items": [
        {
          "id": "modern_01",
          "name": "ធៀបសម័យទំនើប ម៉ូដទី ១",
          "price": 1500,
          "description": "រចនាម៉ូដអឺរ៉ុប ពណ៌ Pastel ស្រទន់ ទាន់សម័យ",
          "image": "sample_images/modern_01.jpg"
        }
      ]
    }
  }
}
```

---

## 🔑 មេរៀនទី៤៖ ការរៀបចំប្រព័ន្ធសុវត្ថិភាព `config.py` និង `.env`

### ៤.១ ឯកសារ `.env` (កំណត់តម្លៃសម្ងាត់)
បង្កើតឯកសារឈ្មោះ `.env` ក្នុង Folder គម្រោង៖

```env
BOT_TOKEN=7890123456:AAFd...
ADMIN_ID=647098577,905596610
PORT=10000
```

### ៤.២ ឯកសារ `config.py` (កូដអាន Configuration)
បង្កើតឯកសារ `config.py`៖

```python
import os
from pathlib import Path
from dotenv import load_dotenv

# ផ្ទុកព័ត៌មានពី .env
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()

# គាំទ្រ Multi-Admin Telegram IDs (ប្តី: 647098577, ប្រពន្ធ: 905596610)
raw_admin_ids = os.getenv("ADMIN_ID", "647098577,905596610").strip()
parsed_admins = [aid.strip() for aid in raw_admin_ids.split(",") if aid.strip()]

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

BASE_DIR = Path(__file__).parent
DOWNLOAD_DIR = BASE_DIR / os.getenv("DOWNLOAD_DIR", "downloads")
DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)
```

---

## 💻 មេរៀនទី៥៖ ការសរសេរកូដមុខងារ Bot `bot.py`

### ៥.១ គោលការណ៍សំខាន់នៃការសរសេរកូដ Bot អាជីព
1. **HTML Mode Formatting**៖ ត្រូវប្រើ `parse_mode="HTML"` និង `html.escape()` ជានិច្ច ដើម្បីការពារការ Crash លើអក្សរខ្មែរ និងសញ្ញាពិសេស `()` `*` `_`।
2. **Anti-Flood Rate Limiting**៖ កំណត់រយៈពេលរង់ចាំ (Rate limit 1 សេកថ៍) ការពារ Spam!
3. **Safe Photo Send Flow**៖ ផ្ញើរូបថតទៅ Telegram ឱ្យជោគជ័យសិន ទើបលុបសារចាស់ចេញ ជៀសវាងអេក្រង់ទទេ។
4. **Verified Phone Collection**៖ ប្រើ `request_contact=True` ដើម្បីទាញយកលេខទូរស័ព្ទ Telegram ផ្ទាល់ 100% ជៀសវាងការវាយលេខលេងរំខាន។

### ៥.២ កូដពេញលេញនៃ `bot.py`

```python
import os
import sys
import re
import time
import logging
import json
import threading
import urllib.request
from http.server import HTTPServer, BaseHTTPRequestHandler
import html
from datetime import datetime
from pathlib import Path
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)

import config

# កំណត់ព័ត៌មាន Logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

ORDERS_DIR = config.BASE_DIR / "orders"
ORDERS_DIR.mkdir(parents=True, exist_ok=True)
BANNED_USERS_FILE = config.BASE_DIR / "banned_users.json"
CATALOG_FILE = config.BASE_DIR / "catalog.json"

USER_SESSIONS = {}
USER_LAST_ACTION = {}
LAST_USER_MESSAGES = {}

MAX_FILE_SIZE_BYTES = 20 * 1024 * 1024  # 20 MB

# ១. ប្រព័ន្ធ Health Check Server សម្រាប់ Cloud Deployment លើ Render
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain; charset=utf-8")
        self.end_headers()
        self.wfile.write(b"OK - Telegram Bot is running 24/7!")

    def log_message(self, format, *args):
        pass

def start_health_server():
    port = int(os.getenv("PORT", "10000"))
    try:
        server = HTTPServer(("0.0.0.0", port), HealthCheckHandler)
        logger.info(f"Health check HTTP server started on port {port}")
        server.serve_forever()
    except Exception as e:
        logger.error(f"Error starting health check server: {e}")

def keep_alive_pinger():
    url = os.getenv("RENDER_EXTERNAL_URL") or os.getenv("SELF_PING_URL")
    if not url:
        return
    time.sleep(15)
    while True:
        try:
            urllib.request.urlopen(url, timeout=10)
        except Exception:
            pass
        time.sleep(240) # Ping រៀងរាល់ ៤ នាទី

# ២. ប្រព័ន្ធការពារ Anti-Flood Rate Limit
def check_rate_limit(user_id: int, limit_seconds: float = 1.0) -> bool:
    now = time.time()
    last_time = USER_LAST_ACTION.get(user_id, 0)
    if now - last_time < limit_seconds:
        return False
    USER_LAST_ACTION[user_id] = now
    return True

def load_catalog() -> dict:
    if not CATALOG_FILE.exists():
        return {"categories": {}}
    try:
        with open(CATALOG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading catalog.json: {e}")
        return {"categories": {}}

def get_invitation_menu_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton("💍 ចុចមើលម៉ូដធៀប", callback_data="inv_samples")],
        [InlineKeyboardButton("📩 ផ្ញើគំរូធៀបផ្ទាល់ខ្លួន (Upload Custom Design)", callback_data="inv_order")],
        [InlineKeyboardButton("🎁 កញ្ចប់ប្រូម៉ូសិនថែមជូនពិសេស", callback_data="inv_promos")],
        [InlineKeyboardButton("📞 ទំនាក់ទំនងពិគ្រោះយោបល់", callback_data="inv_contact")],
    ]
    return InlineKeyboardMarkup(keyboard)

# ៣. មុខងារបង្ហាញរូបថតគំរូធៀប និងប៊ូតុងបញ្ជា
async def show_item_photo(query, context, cat_key: str, item_index: int):
    catalog = load_catalog()
    category = catalog.get("categories", {}).get(cat_key)
    if not category:
        return

    items = category.get("items", [])
    if not items:
        return

    item_index = item_index % len(items)
    item = items[item_index]

    cat_name = category.get("name", "ប្រភេទធៀប")
    item_name = item.get("name", f"ម៉ូដ {item_index + 1}")
    price = item.get("price", 0)
    desc = item.get("description", "")
    img_rel_path = item.get("image", "")

    img_path = config.BASE_DIR / img_rel_path

    caption = (
        f"📸 <b>{html.escape(str(item_name))}</b> ({html.escape(str(cat_name))})\n\n"
        f"📝 <b>ព័ត៌មានលម្អិត</b>: {html.escape(str(desc))}\n"
        f"💰 <b>តម្លៃកំណត់</b>: <b>{price:,} រៀល / ធៀប</b>\n\n"
        f"🎁 <i>ប្រូម៉ូសិន</i>: ឥតគិតថ្លៃសេវារចនា (Free Design) សម្រាប់ការកុម្ម៉ង់ចាប់ពី ២០០ ធៀបឡើងទៅ!"
    )

    prev_idx = (item_index - 1) % len(items)
    next_idx = (item_index + 1) % len(items)

    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("👉 ជ្រើសរើសម៉ូដនេះ (Select This Design)", callback_data=f"selectitem_{cat_key}_{item_index}")],
        [
            InlineKeyboardButton("⬅️ ម៉ូដមុន", callback_data=f"viewitem_{cat_key}_{prev_idx}"),
            InlineKeyboardButton(f"ម៉ូដ {item_index + 1}/{len(items)}", callback_data="noop"),
            InlineKeyboardButton("➡️ ម៉ូដបន្ទាប់", callback_data=f"viewitem_{cat_key}_{next_idx}")
        ],
        [InlineKeyboardButton("📂 មើលប្រភេទធៀបផ្សេងទៀត", callback_data="inv_categories")]
    ])

    msg_obj = query.message if hasattr(query, "message") and query.message else None
    chat_id = msg_obj.chat_id if msg_obj else query.effective_chat.id

    new_msg = None
    if img_path.exists():
        with open(img_path, "rb") as photo_file:
            new_msg = await context.bot.send_photo(
                chat_id=chat_id,
                photo=photo_file,
                caption=caption,
                reply_markup=kb,
                parse_mode="HTML"
            )
    else:
        new_msg = await context.bot.send_message(
            chat_id=chat_id, text=caption, reply_markup=kb, parse_mode="HTML"
        )

    if new_msg and msg_obj and msg_obj.message_id != new_msg.message_id:
        try:
            await msg_obj.delete()
        except Exception:
            pass

# ៤. មុខងារបញ្ជូនការកុម្ម៉ង់ និងផ្ញើ Alert ទៅកាន់ Admin
async def process_finalize_order(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int, session: dict):
    user = update.effective_user
    order_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    copies = session["copies"]
    price_per_card = session.get("price_per_card", 0)
    total_price_text = f"{copies * price_per_card:,} រៀល" if price_per_card > 0 else "ពិភាក្សាតាម File"
    phone_text = session.get("phone", "N/A")

    order_record = {
        "order_id": f"ORD_{user_id}_{int(datetime.now().timestamp())}",
        "user_id": user_id,
        "user_name": user.full_name or user.username or "Customer",
        "username": f"@{user.username}" if user.username else "N/A",
        "phone": phone_text,
        "design_title": session.get("design_title"),
        "copies": copies,
        "total_price": total_price_text,
        "order_time": order_time
    }

    user_full_name = html.escape(user.full_name or user.first_name or "Customer")
    username_str = html.escape(f"@{user.username}" if user.username else "N/A")
    design_title = html.escape(str(session.get("design_title", "")))
    safe_phone = html.escape(phone_text)

    # ផ្ញើសារបញ្ជាក់ជូនអតិថិជន
    customer_msg = (
        f"✅ <b>ទទួលបានការកុម្ម៉ង់ធៀបដោយជោគជ័យ!</b>\n\n"
        f"▪️ <b>លេខកុម្ម៉ង់ (Order ID)</b>: <code>{order_record['order_id']}</code>\n"
        f"▪️ <b>ម៉ូដធៀប</b>: {design_title}\n"
        f"▪️ <b>ចំនួនកុម្ម៉ង់</b>: <b>{copies} ធៀប</b>\n"
        f"▪️ <b>តម្លៃសរុបប្រហែល</b>: <b>{total_price_text}</b>\n"
        f"📞 <b>លេខទូរស័ព្ទទំនាក់ទំនង</b>: <b>{safe_phone}</b>\n\n"
        f"📩 ក្រុមការងារ <b>ឆេងមុនីបោះពុម្ព</b> នឹងទាក់ទងមកលោកអ្នកវិញក្នុងពេលឆាប់ៗនេះ!"
    )
    await context.bot.send_message(chat_id=user_id, text=customer_msg, reply_markup=ReplyKeyboardRemove(), parse_mode="HTML")

    # ផ្ញើសារ Instant Alert + រូបថត ទៅកាន់ Admin (ប្តី & ប្រពន្ធ)
    admin_ids = getattr(config, "ADMIN_IDS", [])
    if admin_ids:
        admin_alert = (
            f"🔔 <b>មានការកុម្ម៉ង់ធៀបថ្មី! (New Order Alert)</b>\n\n"
            f"👤 <b>អតិថិជន</b>: {user_full_name} ({username_str})\n"
            f"📞 <b>លេខទូរស័ព្ទ</b>: <b>{safe_phone}</b>\n"
            f"🆔 <b>User ID</b>: <code>{user_id}</code>\n"
            f"📜 <b>ម៉ូដធៀប</b>: {design_title}\n"
            f"🔢 <b>ចំនួនកុម្ម៉ង់</b>: <b>{copies} ធៀប</b>\n"
            f"💰 <b>តម្លៃសរុប</b>: <b>{total_price_text}</b>\n"
            f"⏰ <b>កាលបរិច្ឆេទ</b>: {order_time}"
        )
        admin_kb = None
        if user.username:
            admin_kb = InlineKeyboardMarkup([[InlineKeyboardButton("💬 ចុច Chat ទៅអតិថិជន (t.me)", url=f"https://t.me/{user.username}")]])

        img_file_path = session.get("file_path")
        full_img_path = (config.BASE_DIR / img_file_path) if img_file_path else None

        for admin_id in admin_ids:
            try:
                if full_img_path and full_img_path.exists():
                    with open(full_img_path, "rb") as pf:
                        await context.bot.send_photo(chat_id=admin_id, photo=pf, caption=admin_alert, reply_markup=admin_kb, parse_mode="HTML")
                else:
                    await context.bot.send_message(chat_id=admin_id, text=admin_alert, reply_markup=admin_kb, parse_mode="HTML")
            except Exception as e:
                logger.error(f"Error sending admin notification: {e}")

    if user_id in USER_SESSIONS:
        del USER_SESSIONS[user_id]

# ៥. កម្មវិធីមេ (Main Entry Point)
def main():
    token = config.BOT_TOKEN
    print("Starting Hardened Telegram Invitation Order Bot...")

    threading.Thread(target=start_health_server, daemon=True).start()
    threading.Thread(target=keep_alive_pinger, daemon=True).start()

    app = ApplicationBuilder().token(token).build()
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CallbackQueryHandler(handle_callback))
    app.add_handler(MessageHandler(filters.CONTACT, handle_contact))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_reply))

    app.run_polling()

if __name__ == "__main__":
    main()
```

---

## 🚀 មេរៀនទី៦៖ ការដំឡើង Bot លើ Cloud Render.com (24/7 Free Deployment)

ដើម្បីឱ្យ Bot ដំណើរការ ២៤ ម៉ោងលើ Cloud ឥតគិតថ្លៃ៖

1. **បង្កើត `requirements.txt`**៖
   ```text
   python-telegram-bot>=20.0
   python-dotenv>=1.0.0
   ```

2. **Push កូដទៅកាន់ GitHub**៖
   ```bash
   git add .
   git commit -m "Complete Telegram Bot Implementation"
   git push origin main
   ```

3. **ដំឡើងលើ Render.com**៖
   - ចុះឈ្មោះ/ចូលគណនីលើ [render.com](https://render.com)
   - ចុច **New +** ជ្រើសរើស **Web Service**
   - ភ្ជាប់ជាមួយ GitHub Repository `TelegramBot-Printing`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python bot.py`
   - **Environment Variables**:
     - `BOT_TOKEN`: `7890123456:AAFd...`
     - `ADMIN_ID`: `647098577,905596610`
   - ចុច **Create Web Service**! Render នឹងដំឡើង និងរ៉ាន់ Bot ស្វ័យប្រវត្តិ ២៤ ម៉ោង!

---

## 🛠️ មេរៀនទី៧៖ ការថែទាំ និងការកែសម្រួលបន្ថែម (Customization Guide)

### ៧.១ របៀបបន្ថែមម៉ូដធៀបថ្មីៗចូលក្នុង Bot
១. ថតរូបគំរូធៀបថ្មី រួចដាក់ចូលក្នុង Folder `sample_images/` (ឧទាហរណ៍៖ `classic_21.jpg`)
២. បើកឯកសារ `catalog.json` រួចបន្ថែមទិន្នន័យក្នុងផ្នែកប្រភេទដែលត្រូវគ្នា៖
```json
{
  "id": "classic_21",
  "name": "ធៀបការបុរាណ ម៉ូដទី ២១",
  "price": 1300,
  "description": "ម៉ូដថ្មីប្រណិត ក្រដាស់ក្រាស់ពិសេស",
  "image": "sample_images/classic_21.jpg"
}
```
៣. ធ្វើការ Commit & Push ទៅ GitHub (`git commit -am "Add new catalog item" ; git push`)។ Render នឹង Update ម៉ូដថ្មីចូល Bot ភ្លាមៗ!

### ៧.២ របៀបកែប្រែប្រូម៉ូសិន ឬព័ត៌មានទំនាក់ទំនង
បើកឯកសារ `bot.py` រួចស្វែងរកអនុគមន៍ `show_promos` ឬ `show_contact` ដើម្បីកែប្រែអត្ថបទ រួច Commit & Push ជាការស្រេច!

---
**🎓 បញ្ចប់សៀវភៅមេរៀន - សូមជូនពរឱ្យការសិក្សា និងការអនុវត្តទទួលបានជោគជ័យ 100%!**
