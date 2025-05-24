import logging
from telegram.ext import ApplicationBuilder, CommandHandler
from telegram import Update
from telegram.ext import ContextTypes
import os
import asyncio

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Привет! Я DeutschCheckBot.")


def main() -> None:
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))

    async def run():
        await app.bot.delete_webhook(drop_pending_updates=True)
        await app.run_polling()

    try:
        asyncio.get_event_loop().run_until_complete(run())
    except RuntimeError as e:
        if "already running" in str(e):
            asyncio.create_task(run())
        else:
            raise


if __name__ == "__main__":
    main()
