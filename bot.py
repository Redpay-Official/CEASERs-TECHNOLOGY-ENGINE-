import os
import sqlite3
import logging
from urllib.parse import quote_plus
from dotenv import load_dotenv

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)

from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes
)

load_dotenv()

TOKEN = os.getenv("9028470009:AAFkBt632Ry7WcrWfGEG63uorZ_YhfwKMFA")
CHANNEL = os.getenv(
    "CHANNEL_USERNAME",
    "@ceaser_update_territory"
)
CHANNEL_LINK = os.getenv(
    "CHANNEL_LINK",
    "https://t.me/ceaser_update_territory"
)
ADMIN_ID = os.getenv("ADMIN_ID")

logging.basicConfig(level=logging.INFO)

# DATABASE
db = sqlite3.connect("ceaser.db", check_same_thread=False)
db.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    username TEXT
)
""")
db.commit()

def save_user(user):
    db.execute(
        "INSERT OR IGNORE INTO users VALUES (?, ?)",
        (user.id, user.username or "Unknown")
    )
    db.commit()

def user_count():
    return db.execute(
        "SELECT COUNT(*) FROM users"
    ).fetchone()[0]

# WELCOME SCREEN
WELCOME = """
╔════════════════════════════╗
     ⚡ CEASER TECHNOLOGY
         ENGINE v2.0
╚════════════════════════════╝

Welcome to the multifunction technology engine.

🟢 SYSTEM STATUS: ONLINE
🔐 SECURITY: ACTIVE
⚡ ENGINE: OPERATIONAL

Select your preferred service below.

POWERED BY CEASER
"""

# MAIN MENU
def main_menu():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "🔍 WEB SEARCH",
                callback_data="web"
            ),
            InlineKeyboardButton(
                "✈️ TELEGRAM",
                callback_data="telegram"
            )
        ],
        [
            InlineKeyboardButton(
                "📱 WHATSAPP",
                callback_data="whatsapp"
            ),
            InlineKeyboardButton(
                "🛡️ REPORT CENTER",
                callback_data="report"
            )
        ],
        [
            InlineKeyboardButton(
                "📊 DASHBOARD",
                callback_data="dashboard"
            ),
            InlineKeyboardButton(
                "⚙️ SETTINGS",
                callback_data="settings"
            )
        ],
        [
            InlineKeyboardButton(
                "ℹ️ HELP",
                callback_data="help"
            )
        ]
    ])

def join_menu():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "📢 JOIN OFFICIAL CHANNEL",
                url=CHANNEL_LINK
            )
        ],
        [
            InlineKeyboardButton(
                "✅ VERIFY MEMBERSHIP",
                callback_data="verify"
            )
        ]
    ])

# FORCE JOIN
async def check_member(bot, user_id):
    try:
        member = await bot.get_chat_member(
            CHANNEL,
            user_id
        )
        return member.status in (
            "member",
            "administrator",
            "creator"
        )
    except Exception:
        return False

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.effective_user

    if not await check_member(context.bot, user.id):
        await update.message.reply_text(
            "🔐 ACCESS RESTRICTED\n\n"
            "Join our official channel before accessing "
            "CEASER TECHNOLOGY ENGINE.",
            reply_markup=join_menu()
        )
        return

    save_user(user)

    await update.message.reply_text(
        WELCOME,
        reply_markup=main_menu()
    )

# SEARCH COMMAND
async def search(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not await check_member(
        context.bot,
        update.effective_user.id
    ):
        await update.message.reply_text(
            "Join our channel first.",
            reply_markup=join_menu()
        )
        return

    if not context.args:
        await update.message.reply_text(
            "Usage:\n/search your search words"
        )
        return

    query = quote_plus(" ".join(context.args))

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "🌐 GOOGLE",
                url=f"https://www.google.com/search?q={query}"
            )
        ],
        [
            InlineKeyboardButton(
                "✈️ TELEGRAM",
                url=f"https://www.google.com/search?q={quote_plus('site:t.me ' + ' '.join(context.args))}"
            )
        ],
        [
            InlineKeyboardButton(
                "▶️ YOUTUBE",
                url=f"https://www.youtube.com/results?search_query={query}"
            )
        ]
    ])

    await update.message.reply_text(
        "🔍 SEARCH RESULTS\n\n"
        f"Query: {' '.join(context.args)}\n\n"
        "Choose your search provider:",
        reply_markup=keyboard
    )

# BUTTON HANDLER
async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    user = query.from_user
    action = query.data

    if action == "verify":
        if await check_member(context.bot, user.id):
            save_user(user)

            await query.edit_message_text(
                WELCOME,
                reply_markup=main_menu()
            )
        else:
            await query.answer(
                "Join the channel before verifying!",
                show_alert=True
            )
        return

    if not await check_member(context.bot, user.id):
        await query.edit_message_text(
            "🔐 ACCESS RESTRICTED\n\n"
            "Join our official channel first.",
            reply_markup=join_menu()
        )
        return

    save_user(user)

    if action == "home":
        await query.edit_message_text(
            WELCOME,
            reply_markup=main_menu()
        )
        return

    if action == "web":
        text = (
            "🔍 WEB SEARCH CENTER\n\n"
            "Search Google, YouTube and public web resources.\n\n"
            "Usage:\n/search your keywords"
        )

    elif action == "telegram":
        text = (
            "✈️ TELEGRAM CENTER\n\n"
            "Explore public Telegram resources.\n"
            "Use the search command to find publicly indexed channels."
        )

    elif action == "whatsapp":
        text = (
            "📱 WHATSAPP CENTER\n\n"
            "Access WhatsApp official resources.\n"
            "Learn about account security, privacy and suspicious messages."
        )

    elif action == "report":
        text = (
            "🛡️ REPORT ASSISTANCE CENTER\n\n"
            "Available assistance:\n\n"
            "• Suspicious Telegram account guidance\n"
            "• WhatsApp scam reporting guidance\n"
            "• Evidence organization\n"
            "• Official reporting resources\n\n"
            "Reports should be genuine and evidence-based. "
            "Automated mass reporting is not supported."
        )

    elif action == "dashboard":
        if ADMIN_ID and str(user.id) == ADMIN_ID:
            text = (
                "👑 ADMIN DASHBOARD\n\n"
                f"Registered users: {user_count()}\n"
                "System: ONLINE"
            )
        else:
            text = (
                "📊 SYSTEM DASHBOARD\n\n"
                "🟢 Bot: ONLINE\n"
                "🟢 Membership: ACTIVE\n"
                "🟢 Database: CONNECTED"
            )

    elif action == "settings":
        text = (
            "⚙️ SETTINGS\n\n"
            "CEASER ENGINE v2.0\n"
            "Membership verification: ENABLED\n"
            "Interface: CYBER DARK"
        )

    elif action == "help":
        text = (
            "ℹ️ HELP CENTER\n\n"
            "/start - Open main menu\n"
            "/search - Search public resources\n"
            "/help - Show help information"
        )

    else:
        text = "Unknown option."

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "⬅️ MAIN MENU",
                callback_data="home"
            )
        ]
    ])

    await query.edit_message_text(
        text,
        reply_markup=keyboard
    )
