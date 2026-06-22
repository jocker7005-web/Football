import os
import sqlite3
import asyncio
import logging
from aiogram import Bot, Dispatcher, Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import CommandStart

# Logging
logging.basicConfig(level=logging.INFO)

# Token va Admin ID
BOT_TOKEN = "8893476065:AAFseE8gnPCvfV_GALln-PCvK-tz7Wihn40"
ADMIN_ID = 1678146043

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
router = Router()

# Ma'lumotlar bazasi manzili
DB_PATH = "/data/efootball_master.db"

def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # Foydalanuvchilar va Buyurtmalar uchun jadval
    cursor.execute("CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, username TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS orders (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, package TEXT, price TEXT)")
    conn.commit()
    conn.close()

# Start komandasi
@router.message(CommandStart())
async def cmd_start(message: Message):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO users (user_id, username) VALUES (?, ?)", (message.from_user.id, message.from_user.username))
    conn.commit()
    conn.close()
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🛒 Coins sotib olish", callback_data="buy")],
        [InlineKeyboardButton(text="🏆 Turnir", callback_data="tour")]
    ])
    await message.answer("Assalomu alaykum! eFootball Coins botiga xush kelibsiz.", reply_markup=kb)

# Tugmalar uchun handler
@router.callback_query(F.data == "buy")
async def buy_callback(callback: CallbackQuery):
    await callback.message.answer("Coins bo'limi ochildi.")

@router.callback_query(F.data == "tour")
async def tour_callback(callback: CallbackQuery):
    await callback.message.answer("Turnir bo'limi ochildi.")

# Botni ishga tushirish
async def main():
    init_db()
    dp.include_router(router)
    print("Bot muvaffaqiyatli ishga tushdi...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
    
