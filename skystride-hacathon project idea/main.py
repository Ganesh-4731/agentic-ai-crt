import os
from dotenv import load_dotenv
from telegram.ext import ApplicationBuilder, CommandHandler, ConversationHandler, MessageHandler, filters

from bot.handlers import (
    start,
    collect_dest,
    collect_dates,
    collect_budget,
    collect_transport,
    collect_style,
    cancel,
    COLLECT_START,
    COLLECT_DEST,
    COLLECT_DATES,
    COLLECT_BUDGET,
    COLLECT_TRANSPORT,
    COLLECT_STYLE,
)
from utils.logger import logger

load_dotenv()


def main() -> None:
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        raise ValueError("TELEGRAM_BOT_TOKEN is not set in .env")

    application = ApplicationBuilder().token(token).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            COLLECT_START: [MessageHandler(filters.TEXT & ~filters.COMMAND, collect_dest)],
            COLLECT_DEST: [MessageHandler(filters.TEXT & ~filters.COMMAND, collect_dates)],
            COLLECT_DATES: [MessageHandler(filters.TEXT & ~filters.COMMAND, collect_budget)],
            COLLECT_BUDGET: [MessageHandler(filters.TEXT & ~filters.COMMAND, collect_transport)],
            COLLECT_TRANSPORT: [MessageHandler(filters.TEXT & ~filters.COMMAND, collect_style)],
            COLLECT_STYLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, collect_style)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    application.add_handler(conv_handler)
    application.add_handler(CommandHandler("cancel", cancel))

    logger.info("SkyStride AI is running...")
    application.run_polling(stop_signals=None)


if __name__ == "__main__":
    main()