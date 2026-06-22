import logging
import asyncio
import sqlite3
from aiogram import Bot, Dispatcher, Router
from aiogram.filters import CommandStart

# Botni sozlash
BOT_TOKEN = "8893476065:AAFseE8gnPCvfV_GALln-PCvK-tz7Wihn40"
ADMIN_ID = 1678146043

logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
router = Router()

# Baza yaratish
def init_db():
    conn = sqlite3.connect("/data/bot_database.db")
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, username TEXT)")
    conn.commit()
    conn.close()

# Start komandasi
@router.message(CommandStart())
async def cmd_start(message):
    await message.answer("Assalomu alaykum! Bot ishlamoqda.")

# Botni ishga tushirish
async def main():
    init_db()
    dp.include_router(router)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
