import logging
import os
import sqlite3
from urllib.parse import quote_plus

from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")
CHANNEL = os.getenv("CHANNEL_USERNAME", "@ceaser_update_territory")
CHANNEL_LINK = os.getenv(
    "CHANNEL_LINK",
    "https://t.me/ceaser_update_territory",
)
ADMIN_ID = os.getenv("ADMIN_ID", "").strip()
DATABASE_PATH = os.getenv("DATABASE_PATH", "ceaser.db")

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# SQLite database
# ---------------------------------------------------------------------------
# The database file is created automatically beside this script unless
# DATABASE_PATH is set to another location in the environment.
db = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
db.execute(
    """
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        username TEXT NOT NULL
    )
    """
)
db.commit()


def save_user(user) -> None:
    """Insert a user or update their username if they already exist."""
    username = user.username or "Unknown"
    with db:
        db.execute(
            """
            INSERT INTO users (user_id, username)
            VALUES (?, ?)
            ON CONFLICT(user_id) DO UPDATE SET username = excluded.username
            """,
            (user.id, username),
        )


def user_count() -> int:
    row = db.execute("SELECT COUNT(*) FROM users").fetchone()
    return int(row[0]) if row else 0


# ---------------------------------------------------------------------------
# Text and keyboards
# ---------------------------------------------------------------------------
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


def main_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("🔍 WEB SEARCH", callback_data="web"),
                InlineKeyboardButton("✈️ TELEGRAM", callback_data="telegram"),
            ],
            [
                InlineKeyboardButton("📱 WHATSAPP", callback_data="whatsapp"),
                InlineKeyboardButton("🛡️ REPORT CENTER", callback_data="report"),
            ],
            [
                InlineKeyboardButton("📊 DASHBOARD", callback_data="dashboard"),
                InlineKeyboardButton("⚙️ SETTINGS", callback_data="settings"),
            ],
            [InlineKeyboardButton("ℹ️ HELP", callback_data="help")],
        ]
    )


def join_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("📢 JOIN OFFICIAL CHANNEL", url=CHANNEL_LINK)],
            [InlineKeyboardButton("✅ VERIFY MEMBERSHIP", callback_data="verify")],
        ]
    )


def back_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton("⬅️ MAIN MENU", callback_data="home")]]
    )


def is_admin(user_id: int) -> bool:
    return bool(ADMIN_ID) and str(user_id) == ADMIN_ID


# ---------------------------------------------------------------------------
# Channel membership verification
# ---------------------------------------------------------------------------
async def check_member(bot, user_id: int) -> bool:
    try:
        member = await bot.get_chat_member(CHANNEL, user_id)
        return member.status in ("member", "administrator", "creator")
    except Exception:
        # Common causes include the bot not being an administrator in the
        # channel, an invalid channel username, or a Telegram API error.
        logger.exception("Could not verify channel membership for user %s", user_id)
        return False


async def require_membership_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """Return True when the user is a channel member; otherwise show join UI."""
    user = update.effective_user
    if user is None or not await check_member(context.bot, user.id):
        if update.message:
            await update.message.reply_text(
                "🔐 ACCESS RESTRICTED\n\n"
                "Join our official channel before accessing "
                "CEASER TECHNOLOGY ENGINE.",
                reply_markup=join_menu(),
            )
        return False
    return True


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    if user is None:
        return

    if not await require_membership_message(update, context):
        return

    save_user(user)
    await update.message.reply_text(WELCOME, reply_markup=main_menu())


async def search(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    if user is None or not await require_membership_message(update, context):
        return

    if not context.args:
        await update.message.reply_text(
            "Usage:\n/search your search words"
        )
        return

    save_user(user)
    search_terms = " ".join(context.args)
    encoded_query = quote_plus(search_terms)
    telegram_query = quote_plus(f"site:t.me {search_terms}")

    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "🌐 GOOGLE",
                    url=f"https://www.google.com/search?q={encoded_query}",
                )
            ],
            [
                InlineKeyboardButton(
                    "✈️ TELEGRAM",
                    url=f"https://www.google.com/search?q={telegram_query}",
                )
            ],
            [
                InlineKeyboardButton(
                    "▶️ YOUTUBE",
                    url=f"https://www.youtube.com/results?search_query={encoded_query}",
                )
            ],
            [InlineKeyboardButton("⬅️ MAIN MENU", callback_data="home")],
        ]
    )

    await update.message.reply_text(
        "🔍 SEARCH RESULTS\n\n"
        f"Query: {search_terms}\n\n"
        "Choose your search provider:",
        reply_markup=keyboard,
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await require_membership_message(update, context):
        return

    await update.message.reply_text(
        "ℹ️ CEASER TECHNOLOGY HELP\n\n"
        "/start - Start the bot and open the main menu\n"
        "/search WORDS - Search public web resources\n"
        "/help - Show this help message\n"
        "/stats - View administrator statistics (admin only)"
    )


async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    if user is None or not is_admin(user.id):
        await update.message.reply_text("⛔ Administrator access only.")
        return

    await update.message.reply_text(
        "👑 CEASER ADMIN PANEL\n\n"
        f"Total registered users: {user_count()}\n"
        "System status: ONLINE"
    )


# ---------------------------------------------------------------------------
# Inline button handler
# ---------------------------------------------------------------------------
async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if query is None:
        return

    user = query.from_user
    action = query.data

    # Verify is handled separately so the callback is only answered once.
    if action == "verify":
        if await check_member(context.bot, user.id):
            save_user(user)
            await query.answer("Membership verified.")
            await query.edit_message_text(WELCOME, reply_markup=main_menu())
        else:
            await query.answer(
                "Please join the channel before verifying!",
                show_alert=True,
            )
        return

    await query.answer()

    # Require membership for all menu actions, including returning home.
    if not await check_member(context.bot, user.id):
        await query.edit_message_text(
            "🔐 ACCESS RESTRICTED\n\n"
            "Join our official channel first.",
            reply_markup=join_menu(),
        )
        return

    save_user(user)

    if action == "home":
        await query.edit_message_text(WELCOME, reply_markup=main_menu())
        return

    if action == "web":
        message = (
            "🔍 WEB SEARCH CENTER\n\n"
            "Search Google, YouTube and public web resources.\n\n"
            "Usage:\n/search your keywords"
        )
        keyboard = back_menu()

    elif action == "telegram":
        message = (
            "✈️ TELEGRAM CENTER\n\n"
            "Explore public Telegram resources.\n"
            "Use /search followed by keywords to find publicly indexed pages."
        )
        keyboard = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("🌐 OPEN TELEGRAM", url="https://telegram.org")],
                [InlineKeyboardButton("⬅️ MAIN MENU", callback_data="home")],
            ]
        )

    elif action == "whatsapp":
        message = (
            "📱 WHATSAPP CENTER\n\n"
            "Access official WhatsApp resources and learn about account "
            "security, privacy and suspicious messages."
        )
        keyboard = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("📱 WHATSAPP WEBSITE", url="https://www.whatsapp.com")],
                [InlineKeyboardButton("⬅️ MAIN MENU", callback_data="home")],
            ]
        )

    elif action == "report":
        message = (
            "🛡️ REPORT ASSISTANCE CENTER\n\n"
            "Available assistance:\n\n"
            "• Suspicious Telegram account guidance\n"
            "• WhatsApp scam reporting guidance\n"
            "• Evidence organization\n"
            "• Official reporting resources\n\n"
            "Reports should be genuine and evidence-based. "
            "Automated mass reporting is not supported."
        )
        keyboard = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("🛡️ TELEGRAM SUPPORT", url="https://telegram.org/support")],
                [InlineKeyboardButton("🛡️ WHATSAPP HELP", url="https://faq.whatsapp.com/")],
                [InlineKeyboardButton("⬅️ MAIN MENU", callback_data="home")],
            ]
        )

    elif action == "dashboard":
        if is_admin(user.id):
            message = (
                "👑 ADMIN DASHBOARD\n\n"
                f"Registered users: {user_count()}\n"
                "System: ONLINE"
            )
        else:
            message = (
                "📊 SYSTEM DASHBOARD\n\n"
                "🟢 Bot: ONLINE\n"
                "🟢 Membership: ACTIVE\n"
                "🟢 Database: CONNECTED"
            )
        keyboard = back_menu()

    elif action == "settings":
        message = (
            "⚙️ SETTINGS\n\n"
            "CEASER ENGINE v2.0\n"
            "Membership verification: ENABLED\n"
            "Interface: CYBER DARK"
        )
        keyboard = back_menu()

    elif action == "help":
        message = (
            "ℹ️ HELP CENTER\n\n"
            "/start - Open the main menu\n"
            "/search - Search public resources\n"
            "/help - Show help information\n"
            "/stats - Administrator statistics"
        )
        keyboard = back_menu()

    else:
        message = "Unknown option."
        keyboard = back_menu()

    await query.edit_message_text(message, reply_markup=keyboard)


# ---------------------------------------------------------------------------
# Application entry point
# ---------------------------------------------------------------------------
def main() -> None:
    if not TOKEN:
        raise ValueError("BOT_TOKEN is missing from the .env file!")

    if not ADMIN_ID:
        logger.warning("ADMIN_ID is not configured; the admin commands will be unavailable.")

    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("search", search))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(CallbackQueryHandler(buttons))

    logger.info("CEASER TECHNOLOGY ENGINE v2.0 is starting")
    app.run_polling()


if __name__ == "__main__":
    main()
