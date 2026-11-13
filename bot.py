import os
import logging
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

TOKEN = os.getenv("BOT_TOKEN")
CHANNEL = os.getenv("CHANNEL_USERNAME", "@ceaser_update_territory")
CHANNEL_LINK = os.getenv(
    "CHANNEL_LINK",
    "https://t.me/ceaser_update_territory"
)
ADMIN_ID = os.getenv("ADMIN_ID")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(name)

users = set()

WELCOME = """
╔══════════════════════════╗
    ⚡ CEASER TECHNOLOGY
        ENGINE v1.0
╚══════════════════════════╝

Welcome to your advanced technology hub!

Select a service below.

🟢 SYSTEM STATUS: ONLINE
🔐 SECURITY: ENABLED
⚡ ENGINE: ACTIVE

POWERED BY CEASER
"""

def menu():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🔍 WEB SEARCH", callback_data="web"),
            InlineKeyboardButton("✈️ TELEGRAM", callback_data="telegram")
        ],
        [
            InlineKeyboardButton("📱 WHATSAPP", callback_data="whatsapp"),
            InlineKeyboardButton("🛡️ REPORT HELP", callback_data="report")
        ],
        [
            InlineKeyboardButton("📊 DASHBOARD", callback_data="stats"),
            InlineKeyboardButton("ℹ️ HELP", callback_data="help")
        ]
    ])

async def is_member(bot, user_id):
    try:
        member = await bot.get_chat_member(CHANNEL, user_id)
        return member.status in [
            "member", "administrator", "creator"
        ]
    except Exception:
        return False

def join_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📢 JOIN CHANNEL", url=CHANNEL_LINK)],
        [InlineKeyboardButton("✅ VERIFY MEMBERSHIP",
                              callback_data="verify")]
    ])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    if not await is_member(context.bot, user.id):
        await update.message.reply_text(
            "🔐 ACCESS RESTRICTED\n\n"
            "Join our official channel to access the engine.",
            reply_markup=join_menu()
        )
        return

    users.add(user.id)

    await update.message.reply_text(
        WELCOME,
        reply_markup=menu()
    )

async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    action = query.data

    if action == "verify":
        if await is_member(context.bot, user_id):
            users.add(user_id)
            await query.edit_message_text(
                WELCOME,
                reply_markup=menu()
            )
        else:
            await query.answer(
                "Please join the channel first!",
                show_alert=True
            )
        return

    if not await is_member(context.bot, user_id):
        await query.edit_message_text(
            "🔐 ACCESS RESTRICTED\n\nJoin our channel first.",
            reply_markup=join_menu()
        )
        return

    users.add(user_id)

    if action == "home":
        await query.edit_message_text(
            WELCOME,
            reply_markup=menu()
        )
        return

    if action == "stats":
        if ADMIN_ID and str(user_id) == ADMIN_ID:
            message = (
                "📊 ADMIN DASHBOARD\n\n"
                f"Users seen this session: {len(users)}\n"
                "🟢 Engine: Online"
            )
        else:
            message = "📊 SYSTEM STATUS\n\n🟢 Engine operational."

    elif action == "web":
        message = "🔍 PUBLIC WEB SEARCH\n\nChoose a search provider."

    elif action == "telegram":
        message = "✈️ TELEGRAM TOOLS\n\nExplore public Telegram resources."

    elif action == "whatsapp":
        message = "📱 WHATSAPP TOOLS\n\nAccess official WhatsApp resources."

    elif action == "report":
        message = (
            "🛡️ REPORT ASSISTANT\n\n"
            "Get help documenting suspicious activity "
            "and submitting genuine reports through official channels."
        )

    elif action == "help":
        message = "ℹ️ CEASER ENGINE HELP CENTER\n\nSelect a service from the main menu."

    else:
        message = "Unknown command."

    buttons_list = []

    if action == "web":
        buttons_list.append([
            InlineKeyboardButton(
                "🌐 GOOGLE SEARCH",
                url="https://www.google.com"
            )
        ])

    elif action == "telegram":
        buttons_list.append([
            InlineKeyboardButton(
                "✈️ TELEGRAM",
                url="https://telegram.org"
            )
        ])

    elif action == "whatsapp":
        buttons_list.append([
            InlineKeyboardButton(
                "📱 WHATSAPP",
                url="https://www.whatsapp.com"
            )
        ])

    elif action == "report":
        buttons_list.append([
            InlineKeyboardButton(
                "🛡️ TELEGRAM SUPPORT",
                url="https://telegram.org/support"
            )
        ])
        buttons_list.append([
            InlineKeyboardButton(
                "🛡️ WHATSAPP HELP",
                url="https://faq.whatsapp.com/"
            )
        ])

    buttons_list.append([
        InlineKeyboardButton(
            "⬅️ MAIN MENU",
            callback_data="home"
        )
    ])

    await query.edit_message_text(
        message,
        reply_markup=InlineKeyboardMarkup(buttons_list)
    )

def main():
    if not TOKEN:
        raise ValueError("BOT_TOKEN is missing!")

    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(buttons))

    print("⚡ CEASER TECHNOLOGY ENGINE ONLINE")

    app.run_polling()

if name == "main":
    main()
