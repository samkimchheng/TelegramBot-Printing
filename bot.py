import os
import sys
import re
import time
import logging
import json
import threading
import urllib.request
from http.server import HTTPServer, BaseHTTPRequestHandler
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

# Configure logging securely
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Directory paths
ORDERS_DIR = config.BASE_DIR / "orders"
ORDERS_DIR.mkdir(parents=True, exist_ok=True)

BANNED_USERS_FILE = config.BASE_DIR / "banned_users.json"


def load_banned_users() -> set:
    if BANNED_USERS_FILE.exists():
        try:
            with open(BANNED_USERS_FILE, "r", encoding="utf-8") as f:
                return set(json.load(f))
        except Exception:
            return set()
    return set()


def save_banned_users(banned_set: set):
    with open(BANNED_USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(list(banned_set), f, indent=2)


BANNED_USERS = load_banned_users()


def is_user_banned(user_id: int) -> bool:
    return user_id in BANNED_USERS or str(user_id) in [str(u) for u in BANNED_USERS]

# Temporary user order sessions & rate limiters
USER_SESSIONS = {}
USER_LAST_ACTION = {}  # Anti-flood rate limiting: user_id -> timestamp
LAST_USER_MESSAGES = {}  # Track user message IDs to forward for direct 1-click admin chat link

MAX_FILE_SIZE_BYTES = 20 * 1024 * 1024  # 20 MB max file size limit
ALLOWED_EXTENSIONS = {".pdf", ".png", ".jpg", ".jpeg"}


class HealthCheckHandler(BaseHTTPRequestHandler):
    """Lightweight HTTP Handler to satisfy Cloud Web Service Health Checks."""
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain; charset=utf-8")
        self.end_headers()
        self.wfile.write(b"OK - Telegram Bot is running 24/7!")

    def log_message(self, format, *args):
        pass  # Suppress health check access logs


def start_health_server():
    """Start background HTTP health check server for Render Free Web Service."""
    port = int(os.getenv("PORT", "10000"))
    try:
        server = HTTPServer(("0.0.0.0", port), HealthCheckHandler)
        logger.info(f"Health check HTTP server started on port {port}")
        server.serve_forever()
    except Exception as e:
        logger.error(f"Error starting health check server: {e}")


def keep_alive_pinger():
    """Self-pinger background thread to prevent Render Free Web Service from sleeping."""
    url = os.getenv("RENDER_EXTERNAL_URL") or os.getenv("SELF_PING_URL")
    if not url:
        return
    logger.info(f"Keep-Alive pinger started for URL: {url}")
    time.sleep(15)
    while True:
        try:
            urllib.request.urlopen(url, timeout=10)
            logger.info("Keep-Alive ping sent successfully to prevent sleep.")
        except Exception as e:
            logger.error(f"Keep-Alive ping error: {e}")
        time.sleep(240)  # Ping every 4 minutes (Render sleeps after 15 min)


def check_rate_limit(user_id: int, limit_seconds: float = 1.0) -> bool:
    """Anti-flood rate limiter & Banned user check: returns False if user is banned or spamming."""
    if is_user_banned(user_id):
        return False
    now = time.time()
    last_time = USER_LAST_ACTION.get(user_id, 0)
    if now - last_time < limit_seconds:
        return False
    USER_LAST_ACTION[user_id] = now
    return True


def sanitize_filename(filename: str) -> str:
    """Security Hardening: Sanitize filename against Path Traversal vulnerabilities."""
    clean_name = Path(filename).name  # Strips directory prefixes
    clean_name = re.sub(r'[^a-zA-Z0-9_\ Khmer.-]', '_', clean_name)
    return clean_name or "file.pdf"


def load_catalog() -> dict:
    """Load catalog dynamically from catalog.json file safely."""
    if not CATALOG_FILE.exists():
        return {"categories": {}}
    try:
        with open(CATALOG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading catalog.json: {e}")
        return {"categories": {}}


def get_invitation_menu_keyboard() -> InlineKeyboardMarkup:
    """Generate inline keyboard specialized for Wedding & Event Invitations."""
    keyboard = [
        [InlineKeyboardButton("💍 ចុចមើលម៉ូដធៀប", callback_data="inv_samples")],
        [InlineKeyboardButton("📩 ផ្ញើគំរូធៀបផ្ទាល់ខ្លួន (Upload Custom Design)", callback_data="inv_order")],
        [InlineKeyboardButton("🎁 កញ្ចប់ប្រូម៉ូសិនថែមជូនពិសេស", callback_data="inv_promos")],
        [InlineKeyboardButton("📞 ទំនាក់ទំនងពិគ្រោះយោបល់", callback_data="inv_contact")],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_categories_keyboard(catalog: dict) -> InlineKeyboardMarkup:
    """Generate inline keyboard for main categories."""
    categories = catalog.get("categories", {})
    keyboard = []
    
    for cat_key, cat_info in categories.items():
        name = cat_info.get("name", cat_key)
        item_count = len(cat_info.get("items", []))
        button_text = f"{name} ({item_count} ម៉ូដ)"
        keyboard.append([InlineKeyboardButton(button_text, callback_data=f"cat_{cat_key}")])

    keyboard.append([InlineKeyboardButton("📩 ផ្ញើគំរូធៀបផ្ទាល់ខ្លួនរបស់អ្នក", callback_data="inv_order")])
    keyboard.append([InlineKeyboardButton("🔙 ត្រឡប់ទៅម៉ឺនុយដើម", callback_data="main_menu")])
    return InlineKeyboardMarkup(keyboard)


def get_session_keyboard(session: dict) -> InlineKeyboardMarkup:
    """Generate inline keyboard for order settings."""
    copies = session.get("copies", 100)

    copy_buttons = [
        InlineKeyboardButton(
            f"{'✅ ' if copies == c else ''}{c} ធៀប", callback_data=f"set_copy_{c}"
        )
        for c in [50, 100, 200, 300, 500]
    ]

    action_buttons = [
        InlineKeyboardButton("✅ បញ្ជូនការកុម្ម៉ង់ឥឡូវនេះ", callback_data="action_submit_order"),
        InlineKeyboardButton("🔙 ជ្រើសរើសម៉ូដផ្សេង", callback_data="inv_samples"),
    ]

    keyboard = [
        copy_buttons,
        action_buttons
    ]
    return InlineKeyboardMarkup(keyboard)


def get_session_text(session: dict) -> str:
    """Format session status text in Khmer."""
    design_title = session.get("design_title", "គំរូផ្ទាល់ខ្លួន (Custom Design)")
    price_per_card = session.get("price_per_card", 0)
    copies = session.get("copies", 100)
    
    total_price_text = f"{copies * price_per_card:,} រៀល" if price_per_card > 0 else "ពិភាក្សាតាម File"

    text = (
        f"💍 **ព័ត៌មានកុម្ម៉ង់ធៀប**\n\n"
        f"▪️ **ម៉ូដដែលបានជ្រើសរើស**: {design_title}\n"
        f"▪️ **តម្លៃក្នុង ១ ធៀប**: {price_per_card:,} រៀល\n"
        f"▪️ **ចំនួនធៀបកុម្ម៉ង់**: **{copies} ធៀប**\n"
        f"▪️ **តម្លៃសរុបប្រហែល**: **{total_price_text}**\n\n"
        f"👇 សូមជ្រើសរើសចំនួនធៀប រួចចុច **'បញ្ជូនការកុម្ម៉ង់ឥឡូវនេះ'**:"
    )
    return text


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command with anti-flood rate limit."""
    user = update.effective_user
    if not check_rate_limit(user.id):
        return

    if update.message:
        LAST_USER_MESSAGES[user.id] = update.message.message_id

    welcome_msg = (
        f"សួស្តី {user.first_name}! 👋\n\n"
        f"💍 **ស្វាគមន៍មកកាន់ សេវាកម្មបោះពុម្ពធៀបការ និងធៀបកម្មវិធីផ្សេងៗ**\n\n"
        f"ពួកយើងមានសេវាកម្មរចនា និងបោះពុម្ពធៀបអាពាហ៍ពិពាហ៍ ធៀបឡើងផ្ទះ ធៀបខួបកំណើត និងធៀបកម្មវិធីគ្រប់ប្រភេទ ដោយគុណភាពខ្ពស់ និងតម្លៃសមរម្យបំផុត!\n\n"
        f"សូមជ្រើសរើសជម្រើសខាងក្រោម៖"
    )
    
    await update.message.reply_text(
        welcome_msg,
        reply_markup=get_invitation_menu_keyboard(),
        parse_mode="Markdown"
    )


async def safe_edit_or_reply(target, text, reply_markup=None, parse_mode="Markdown", is_callback=True):
    """Safely edit message or delete photo message and send new text message without raising Telegram BadRequest errors."""
    bot = target.get_bot() if hasattr(target, "get_bot") else None
    
    if is_callback:
        msg_obj = target.message if hasattr(target, "message") else target
        if not bot and msg_obj and hasattr(msg_obj, "get_bot"):
            bot = msg_obj.get_bot()

        if msg_obj and msg_obj.photo:
            try:
                await msg_obj.delete()
            except Exception:
                pass
            if bot:
                await bot.send_message(chat_id=msg_obj.chat_id, text=text, reply_markup=reply_markup, parse_mode=parse_mode)
        else:
            try:
                await target.edit_message_text(text, reply_markup=reply_markup, parse_mode=parse_mode)
            except Exception:
                if msg_obj:
                    try:
                        await msg_obj.delete()
                    except Exception:
                        pass
                    if bot:
                        await bot.send_message(chat_id=msg_obj.chat_id, text=text, reply_markup=reply_markup, parse_mode=parse_mode)
    else:
        if hasattr(target, "message") and target.message:
            await target.message.reply_text(text, reply_markup=reply_markup, parse_mode=parse_mode)


async def show_categories(target, is_callback=True):
    catalog = load_catalog()
    msg = (
        "📂 **កាតាឡុកប្រភេទទិន្នន័យម៉ូដធៀប (Invitation Categories)**\n\n"
        "សូមជ្រើសរើសប្រភេទទិន្នន័យម៉ូដធៀបខាងក្រោម ដើម្បីមើលរូបថត និងតម្លៃកំណត់៖"
    )
    kb = get_categories_keyboard(catalog)
    await safe_edit_or_reply(target, msg, reply_markup=kb, parse_mode="Markdown", is_callback=is_callback)


async def show_item_photo(query, context, cat_key: str, item_index: int):
    catalog = load_catalog()
    category = catalog.get("categories", {}).get(cat_key)
    if not category:
        await safe_edit_or_reply(query, "⚠️ មិនមានប្រភេទទិន្នន័យនេះឡើយ。", is_callback=True)
        return

    items = category.get("items", [])
    if not items:
        await safe_edit_or_reply(query, f"⚠️ ប្រភេទ `{category.get('name')}` មិនទាន់មានរូបថតគំរូធៀបនៅឡើយទេ។", is_callback=True)
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
        f"📸 **{item_name}** ({cat_name})\n\n"
        f"📝 **ព័ត៌មានលម្អិត**: {desc}\n"
        f"💰 **តម្លៃកំណត់**: **{price:,} រៀល / ធៀប**\n\n"
        f"🎁 *ប្រូម៉ូសិន*: ឥតគិតថ្លៃសេវារចនា (Free Design) សម្រាប់ការកុម្ម៉ង់ចាប់ពី ២០០ ធៀបឡើងទៅ!"
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
    chat_id = msg_obj.chat_id if msg_obj else (query.effective_chat.id if hasattr(query, "effective_chat") else None)

    if msg_obj:
        try:
            await msg_obj.delete()
        except Exception:
            pass

    if img_path.exists():
        with open(img_path, "rb") as photo_file:
            await context.bot.send_photo(
                chat_id=chat_id,
                photo=photo_file,
                caption=caption,
                reply_markup=kb,
                parse_mode="Markdown"
            )
    else:
        await context.bot.send_message(
            chat_id=chat_id,
            text=caption,
            reply_markup=kb,
            parse_mode="Markdown"
        )


async def show_promos(target, is_callback=True):
    msg = (
        "🎁 **កញ្ចប់ប្រូម៉ូសិនពិសេស សម្រាប់ធៀបការ & កម្មវិធី**\n\n"
        "🎉 **ការផ្តល់ជូនពិសេស**:\n"
        "១. **FREE Design**: ឥតគិតថ្លៃសេវារចនាម៉ូដធៀប សម្រាប់ការកុម្ម៉ង់ចាប់ពី ២០០ ធៀបឡើងទៅ!\n"
        "២. **FREE Welcome Board Frame**: ថែមជូនស៊ុមរូបថតស្វាគមន៍មុខរោងការ ១ ឈុតដោយឥតគិតថ្លៃ!\n"
        "៣. **FREE Delivery**: សេវាដឹកជញ្ជូនដល់ទីកន្លែងសម្រាប់អតិថិជនក្នុងតំបន់!\n\n"
        "📩 កុម្ម៉ង់កាន់តែច្រើន បញ្ចុះតម្លៃកាន់តែពិសេស!"
    )
    back_kb = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 ត្រឡប់ទៅម៉ឺនុយដើម", callback_data="main_menu")]])
    await safe_edit_or_reply(target, msg, reply_markup=back_kb, parse_mode="Markdown", is_callback=is_callback)


async def show_contact(target, is_callback=True):
    msg = (
        "📞 **ព័ត៌មានទំនាក់ទំនង & ពិគ្រោះយោបល់**\n\n"
        "🏪 **ឆេងមុនីបោះពុម្ព**\n"
        "☎️ **ទូរស័ព្ទ**: 093586024 / 078515484\n"
        "💬 **Telegram**: https://t.me/Kimchheng12\n"
        "📍 **ទីតាំង**: ខាងជើងវត្តយាកាបក្រោម / ទល់មុខតារាងបាល់ទះកុងចេក\n\n"
        "⏰ បើកទទួលការកុម្ម៉ង់រៀងរាល់ថ្ងៃ ពីម៉ោង 7:30 ព្រឹក - 7:00 យប់!"
    )
    back_kb = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 ត្រឡប់ទៅម៉ឺនុយដើម", callback_data="main_menu")]])
    await safe_edit_or_reply(target, msg, reply_markup=back_kb, parse_mode="Markdown", is_callback=is_callback)


async def show_upload_instruction(target, is_callback=True):
    msg = (
        "📩 **សេវាទទួលកុម្ម៉ង់បោះពុម្ពធៀបផ្ទាល់ខ្លួន**\n\n"
        "📥 **សូមផ្ញើ File គំរូធៀប (PDF) ឬរូបភាព (JPG/PNG) ចូលក្នុង Chat នេះ!**\n\n"
        "បន្ទាប់មក អ្នកអាចជ្រើសរើសចំនួនធៀប (៥០, ១០០, ២០០, ៣០០, ៥۰۰...) រួចចុចបញ្ជូនការកុម្ម៉ង់បានភ្លាមៗ..."
    )
    back_kb = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 ត្រឡប់ទៅម៉ឺនុយដើម", callback_data="main_menu")]])
    await safe_edit_or_reply(target, msg, reply_markup=back_kb, parse_mode="Markdown", is_callback=is_callback)


async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle uploaded document file securely."""
    user = update.effective_user
    if not check_rate_limit(user.id):
        return
    if update.message:
        LAST_USER_MESSAGES[user.id] = update.message.message_id

    doc = update.message.document
    if doc.file_size and doc.file_size > MAX_FILE_SIZE_BYTES:
        await update.message.reply_text("⚠️ ឯកសារធំពេក! សូមផ្ញើឯកសារដែលមានទំហំតូចជាង 20MB។")
        return

    raw_file_name = doc.file_name or "invitation_design.pdf"
    ext = Path(raw_file_name).suffix.lower()

    if ext not in ALLOWED_EXTENSIONS:
        await update.message.reply_text(
            "⚠️ សូមផ្ញើឯកសារប្រភេទ **PDF** ឬ **រូបភាព (PNG/JPG)** នៃគំរូធៀបរបស់អ្នក!"
        )
        return

    file_name = sanitize_filename(raw_file_name)
    status_msg = await update.message.reply_text("📥 កំពុងទាញយកឯកសារគំរូធៀប...")

    user_dir = config.DOWNLOAD_DIR / str(user.id)
    user_dir.mkdir(parents=True, exist_ok=True)
    file_path = user_dir / file_name

    tg_file = await context.bot.get_file(doc.file_id)
    await tg_file.download_to_drive(file_path)

    session = {
        "design_key": "custom",
        "design_title": f"គំរូផ្ទាល់ខ្លួន (`{file_name}`)",
        "price_per_card": 0,
        "file_path": str(file_path),
        "file_name": file_name,
        "copies": 100,
    }
    USER_SESSIONS[user.id] = session

    text = get_session_text(session)
    keyboard = get_session_keyboard(session)

    await status_msg.edit_text(text, reply_markup=keyboard, parse_mode="Markdown")


async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle uploaded photo file securely."""
    user = update.effective_user
    if not check_rate_limit(user.id):
        return
    if update.message:
        LAST_USER_MESSAGES[user.id] = update.message.message_id

    photo = update.message.photo[-1]
    if photo.file_size and photo.file_size > MAX_FILE_SIZE_BYTES:
        await update.message.reply_text("⚠️ រូបភាពធំពេក! សូមផ្ញើរូបភាពដែលមានទំហំតូចជាង 20MB។")
        return

    file_name = f"invitation_{photo.file_id[:8]}.jpg"

    status_msg = await update.message.reply_text("📥 កំពុងទាញយករូបភាពគំរូធៀប...")

    user_dir = config.DOWNLOAD_DIR / str(user.id)
    user_dir.mkdir(parents=True, exist_ok=True)
    image_path = user_dir / file_name

    tg_file = await context.bot.get_file(photo.file_id)
    await tg_file.download_to_drive(image_path)

    session = {
        "design_key": "custom",
        "design_title": f"រូបភាពគំរូផ្ទាល់ខ្លួន (`{file_name}`)",
        "price_per_card": 0,
        "file_path": str(image_path),
        "file_name": file_name,
        "copies": 100,
    }
    USER_SESSIONS[user.id] = session

    text = get_session_text(session)
    keyboard = get_session_keyboard(session)

    await status_msg.edit_text(text, reply_markup=keyboard, parse_mode="Markdown")


async def process_finalize_order(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int, session: dict):
    """Finalize order record, save to file, notify customer, and send multi-admin alert with phone number."""
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
        "file_name": session.get("file_name"),
        "file_path": session.get("file_path"),
        "copies": copies,
        "total_price": total_price_text,
        "order_time": order_time
    }

    # Save order details to orders directory safely
    order_file = ORDERS_DIR / f"{order_record['order_id']}.json"
    with open(order_file, "w", encoding="utf-8") as f:
        json.dump(order_record, f, ensure_ascii=False, indent=2)

    import html
    user_full_name = html.escape(user.full_name or user.first_name or "Customer")
    username_str = html.escape(f"@{user.username}" if user.username else "N/A")
    design_title = html.escape(str(session.get("design_title", "")))
    safe_phone = html.escape(phone_text)

    # Notify customer & clear reply keyboard
    customer_msg = (
        f"✅ <b>ទទួលបានការកុម្ម៉ង់ធៀបដោយជោគជ័យ!</b>\n\n"
        f"▪️ <b>លេខកុម្ម៉ង់ (Order ID)</b>: <code>{order_record['order_id']}</code>\n"
        f"▪️ <b>ម៉ូដធៀប</b>: {design_title}\n"
        f"▪️ <b>ចំនួនកុម្ម៉ង់</b>: <b>{copies} ធៀប</b>\n"
        f"▪️ <b>តម្លៃសរុបប្រហែល</b>: <b>{total_price_text}</b>\n"
        f"📞 <b>លេខទូរស័ព្ទទំនាក់ទំនង</b>: <b>{safe_phone}</b>\n\n"
        f"📩 ក្រុមការងារ <b>ឆេងមុនីបោះពុម្ព</b> បានទទួលព័ត៌មានកុម្ម៉ង់របស់អ្នករួចរាល់ហើយ។ ពួកយើងនឹងពិនិត្យមើល និងទាក់ទងមកលោកអ្នកវិញក្នុងពេលឆាប់ៗនេះ!\n\n"
        f"សូមអរគុណ!"
    )
    await context.bot.send_message(
        chat_id=user_id,
        text=customer_msg,
        reply_markup=ReplyKeyboardRemove(),
        parse_mode="HTML"
    )

    # Send instant Real-Time Order Alert with Design Photo to Shop Admin(s)
    admin_ids = getattr(config, "ADMIN_IDS", [])
    if not admin_ids and getattr(config, "ADMIN_ID", None):
        admin_ids = [config.ADMIN_ID]

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

        photo_data = None
        is_pdf = False
        if full_img_path and full_img_path.exists():
            try:
                ext = full_img_path.suffix.lower()
                photo_data = full_img_path.read_bytes()
                if ext == ".pdf":
                    is_pdf = True
            except Exception as e:
                logger.error(f"Error reading design image file: {e}")

        for admin_id in admin_ids:
            try:
                if photo_data:
                    import io
                    file_obj = io.BytesIO(photo_data)
                    file_obj.name = full_img_path.name
                    if is_pdf:
                        await context.bot.send_document(
                            chat_id=admin_id,
                            document=file_obj,
                            caption=admin_alert,
                            reply_markup=admin_kb,
                            parse_mode="HTML"
                        )
                    else:
                        await context.bot.send_photo(
                            chat_id=admin_id,
                            photo=file_obj,
                            caption=admin_alert,
                            reply_markup=admin_kb,
                            parse_mode="HTML"
                        )
                else:
                    await context.bot.send_message(chat_id=admin_id, text=admin_alert, reply_markup=admin_kb, parse_mode="HTML")
                
                # Forward customer's original message to admin
                last_msg_id = LAST_USER_MESSAGES.get(user_id)
                if last_msg_id:
                    await context.bot.forward_message(chat_id=admin_id, from_chat_id=user_id, message_id=last_msg_id)
            except Exception as e:
                logger.error(f"Error sending admin notification to {admin_id}: {e}")

    if user_id in USER_SESSIONS:
        del USER_SESSIONS[user_id]


async def block_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin command to block spammer/troll user ID."""
    user = update.effective_user
    admin_ids = getattr(config, "ADMIN_IDS", [])
    if user.id not in admin_ids and str(user.id) not in [str(a) for a in admin_ids]:
        return

    args = context.args
    if not args:
        await update.message.reply_text("⚠️ សូមប្រើប្រាស់ទម្រង់៖ `/block <user_id>`\nឧទាហរណ៍៖ `/block 6645972722`", parse_mode="Markdown")
        return

    try:
        target_id = int(args[0])
        BANNED_USERS.add(target_id)
        save_banned_users(BANNED_USERS)
        await update.message.reply_text(f"🚫 **បានបិទគណនី (Block)** User ID `{target_id}` រួចរាល់ដោយជោគជ័យ! គណនីនេះមិនអាចប្រើប្រាស់ Bot បានទៀតឡើយ។", parse_mode="Markdown")
    except ValueError:
        await update.message.reply_text("⚠️ លេខ User ID មិនត្រឹមត្រូវឡើយ។")


async def unblock_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin command to unblock user ID."""
    user = update.effective_user
    admin_ids = getattr(config, "ADMIN_IDS", [])
    if user.id not in admin_ids and str(user.id) not in [str(a) for a in admin_ids]:
        return

    args = context.args
    if not args:
        await update.message.reply_text("⚠️ សូមប្រើប្រាស់ទម្រង់៖ `/unblock <user_id>`", parse_mode="Markdown")
        return

    try:
        target_id = int(args[0])
        if target_id in BANNED_USERS or str(target_id) in [str(u) for u in BANNED_USERS]:
            BANNED_USERS.discard(target_id)
            BANNED_USERS.discard(str(target_id))
            save_banned_users(BANNED_USERS)
            await update.message.reply_text(f"✅ **បានបើកគណនី (Unblock)** User ID `{target_id}` វិញរួចរាល់!", parse_mode="Markdown")
        else:
            await update.message.reply_text(f"ℹ️ User ID `{target_id}` មិនស្ថិតក្នុងបញ្ជី Banned ឡើយ។", parse_mode="Markdown")
    except ValueError:
        await update.message.reply_text("⚠️ លេខ User ID មិនត្រឹមត្រូវឡើយ។")


async def handle_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle 1-tap phone contact sharing from customer (Telegram Verified)."""
    user = update.effective_user
    if not check_rate_limit(user.id):
        return
    if update.message:
        LAST_USER_MESSAGES[user.id] = update.message.message_id

    contact = update.message.contact
    raw_phone = contact.phone_number if contact else "N/A"
    phone_label = f"{raw_phone} (✅ ផ្ទៀងផ្ទាត់ដោយ Telegram 100%)"

    session = USER_SESSIONS.get(user.id)
    if session and session.get("awaiting_phone"):
        session["phone"] = phone_label
        session["awaiting_phone"] = False
        await process_finalize_order(update, context, user.id, session)


async def handle_text_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not check_rate_limit(user.id):
        return
    if update.message:
        LAST_USER_MESSAGES[user.id] = update.message.message_id

    text = update.message.text.strip()
    session = USER_SESSIONS.get(user.id)

    if session and session.get("awaiting_phone"):
        # Validate phone input (must contain digits)
        digits = re.sub(r'\D', '', text)
        if len(digits) < 8:
            await update.message.reply_text(
                "⚠️ **លេខទូរស័ព្ទមិនត្រឹមត្រូវឡើយ!**\n\n"
                "សូមចុចប៊ូតុង **'📱 ចែករំលែកលេខទូរស័ព្ទ'** ខាងក្រោម ឬវាយបញ្ចូលលេខទូរស័ព្ទត្រឹមត្រូវ (ឧទាហរណ៍៖ 093586024)!",
                parse_mode="Markdown"
            )
            return

        session["phone"] = f"{text} (📝 វាយបញ្ចូលដោយដៃ)"
        session["awaiting_phone"] = False
        await process_finalize_order(update, context, user.id, session)
        return

    if "ម៉ូដធៀប" in text:
        await show_item_photo(update, context, "classic", 0)
    elif "ផ្ញើគំរូធៀបកុម្ម៉ង់" in text:
        await show_upload_instruction(update, is_callback=False)
    elif "ប្រូម៉ូសិន" in text:
        await show_promos(update, is_callback=False)
    elif "ទំនាក់ទំនង" in text:
        await show_contact(update, is_callback=False)


async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    if not check_rate_limit(user_id, 0.5):
        await query.answer("⚠️ សូមរង់ចាំមួយភ្លែត...", show_alert=False)
        return

    await query.answer()
    data = query.data

    if data == "no_username_info":
        await query.answer_callback_query(
            "ℹ️ អតិថិជននេះមិនមាន Telegram Username ទេ។\n\n👉 សូមចុចលើឈ្មោះអតិថិជន (អក្សរពណ៌ខៀវ) ក្នុងសារខាងលើ ដើម្បី Chat ទៅកាន់គាត់ مباشرة!",
            show_alert=True
        )
        return

    elif data == "main_menu":
        welcome_msg = (
            "💍 **សេវាកម្មបោះពុម្ពធៀបការ និងធៀបកម្មវិធីផ្សេងៗ**\n\n"
            "សូមជ្រើសរើសជម្រើសខាងក្រោម៖"
        )
        await safe_edit_or_reply(query, welcome_msg, reply_markup=get_invitation_menu_keyboard(), parse_mode="Markdown", is_callback=True)
        return

    elif data == "inv_samples":
        await show_item_photo(query, context, "classic", 0)
        return

    elif data == "inv_categories":
        await show_categories(query, is_callback=True)
        return

    elif data.startswith("cat_"):
        cat_key = data.replace("cat_", "")
        await show_item_photo(query, context, cat_key, 0)
        return

    elif data.startswith("viewitem_"):
        parts = data.split("_")
        cat_key = parts[1]
        item_index = int(parts[2])
        await show_item_photo(query, context, cat_key, item_index)
        return

    elif data.startswith("selectitem_"):
        parts = data.split("_")
        cat_key = parts[1]
        item_index = int(parts[2])
        
        catalog = load_catalog()
        category = catalog.get("categories", {}).get(cat_key, {})
        items = category.get("items", [])
        
        if 0 <= item_index < len(items):
            item = items[item_index]
            session = {
                "design_key": item.get("id"),
                "design_title": item.get("name"),
                "price_per_card": item.get("price", 0),
                "file_name": f"{item.get('id')}.pdf",
                "file_path": item.get("image"),
                "copies": 100,
            }
            USER_SESSIONS[user_id] = session

            text = get_session_text(session)
            keyboard = get_session_keyboard(session)
            await safe_edit_or_reply(query, text, reply_markup=keyboard, parse_mode="Markdown", is_callback=True)
        return

    elif data == "inv_order":
        await show_upload_instruction(query, is_callback=True)
        return

    elif data == "inv_promos":
        await show_promos(query, is_callback=True)
        return
    elif data == "inv_contact":
        await show_contact(query, is_callback=True)
        return

    session = USER_SESSIONS.get(user_id)

    if not session:
        await safe_edit_or_reply(query, "⚠️ មិនមានប្រតិបត្តិការកុម្ម៉ង់សកម្មឡើយ។ សូមជ្រើសរើសម៉ូដធៀបម្តងទៀត!", is_callback=True)
        return

    if data.startswith("set_copy_"):
        copies = int(data.replace("set_copy_", ""))
        session["copies"] = copies
        text = get_session_text(session)
        keyboard = get_session_keyboard(session)
        await safe_edit_or_reply(query, text, reply_markup=keyboard, parse_mode="Markdown", is_callback=True)

    elif data == "action_cancel":
        del USER_SESSIONS[user_id]
        await safe_edit_or_reply(query, "❌ ប្រតិបត្តិការកុម្ម៉ង់ត្រូវបានបោះបង់។", is_callback=True)

    elif data == "action_submit_order":
        session["awaiting_phone"] = True

        contact_kb = ReplyKeyboardMarkup(
            [[KeyboardButton("📱 ចែករំលែកលេខទូរស័ព្ទ (Share Phone Number)", request_contact=True)]],
            resize_keyboard=True,
            one_time_keyboard=True
        )

        if query.message:
            try:
                await query.message.delete()
            except Exception:
                pass

        await context.bot.send_message(
            chat_id=user_id,
            text=(
                "📱 <b>សូមផ្ញើ ឬចែករំលែកលេខទូរស័ព្ទទំនាក់ទំនងរបស់អ្នក!</b>\n\n"
                "ដើម្បីឱ្យក្រុមការងារ <b>ឆេងមុនីបោះពុម្ព</b> អាចទាក់ទងបញ្ជាក់ព័ត៌មានបោះពុម្ព និងដឹកជញ្ជូនជូនលោកអ្នកបានលឿនបំផុត។\n\n"
                "👇 <b>ចុចប៊ូតុងខាងក្រោមដើម្បីចែករំលែក (ឬវាយបញ្ចូលលេខទូរស័ព្ទក្នុង Chat នេះ)</b>:"
            ),
            reply_markup=contact_kb,
            parse_mode="HTML"
        )


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Global Exception Handler: Catches all unexpected errors securely without leaking sensitive info."""
    logger.error("Exception while handling an update:", exc_info=context.error)


async def post_init(app):
    """Set bot commands description in Telegram menu."""
    from telegram import BotCommand
    commands = [
        BotCommand("start", "💍 ចុចមើលម៉ូដធៀប")
    ]
    try:
        await app.bot.set_my_commands(commands)
    except Exception as e:
        logger.error(f"Error setting bot commands: {e}")


def main():
    """Start the bot application securely."""
    token = config.BOT_TOKEN
    if not token or token == "YOUR_TELEGRAM_BOT_TOKEN_HERE":
        print("ERROR: BOT_TOKEN is missing in .env file!")
        sys.exit(1)

    print("Starting Hardened Telegram Invitation Order Bot...")

    # Start background HTTP health server for Render Cloud Free Web Service
    threading.Thread(target=start_health_server, daemon=True).start()

    # Start Keep-Alive pinger to prevent Render Web Service from sleeping
    threading.Thread(target=keep_alive_pinger, daemon=True).start()

    app = ApplicationBuilder().token(token).post_init(post_init).build()

    app.add_error_handler(error_handler)

    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("block", block_command))
    app.add_handler(CommandHandler("unblock", unblock_command))
    app.add_handler(MessageHandler(filters.CONTACT, handle_contact))
    app.add_handler(MessageHandler(filters.Document.ALL, handle_document))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_reply))
    app.add_handler(CallbackQueryHandler(handle_callback))

    print("Bot is running securely and listening for Telegram messages...")
    app.run_polling()


if __name__ == "__main__":
    main()
