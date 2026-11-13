# HELP COMMAND
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "/start - Start bot\n"
        "/search WORDS - Search public resources\n"
        "/help - Help center"
    )

# ADMIN COMMAND
async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not ADMIN_ID or str(update.effective_user.id) != ADMIN_ID:
        await update.message.reply_text(
            "⛔ Administrator access only."
        )
        return

    await update.message.reply_text(
        "👑 CEASER ADMIN PANEL\n\n"
        f"Total registered users: {user_count()}\n"
        "System status: ONLINE"
    )

# START APPLICATION
def main():

    if not TOKEN:
        raise ValueError("BOT_TOKEN missing from environment!")

    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("search", search))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("stats", stats))

    app.add_handler(
        CallbackQueryHandler(buttons)
    )

    print("⚡ CEASER TECHNOLOGY ENGINE ONLINE")

    app.run_polling()

if name == "main":
    main()
