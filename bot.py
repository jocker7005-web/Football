import logging
import sqlite3
from aiogram import Bot, Dispatcher, Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import CommandStart
import asyncio

# Token
BOT_TOKEN = "8893476065:AAFseE8gnPCvfV_GALln-PCvK-tz7Wihn40"

logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
router = Router()

# Asosiy menyu tugmalari
def get_main_kb():
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🛒 Coins sotib olish", callback_data="buy_menu")],
        [InlineKeyboardButton(text="🏆 Turnir", callback_data="tour_menu")]
    ])
    return kb

# Start komandasi
@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer(
        "Assalomu alaykum! eFootball botiga xush kelibsiz. Quyidagilardan birini tanlang:", 
        reply_markup=get_main_kb()
    )

# Tugmalarni bosganda javob qaytarish
@router.callback_query(F.data == "buy_menu")
async def buy_menu(callback: CallbackQuery):
    await callback.message.edit_text("🛒 Coins bo'limi ochildi (tez orada qo'shamiz).", reply_markup=get_main_kb())

@router.callback_query(F.data == "tour_menu")
async def tour_menu(callback: CallbackQuery):
    await callback.message.edit_text("🏆 Turnir bo'limi ochildi (tez orada qo'shamiz).", reply_markup=get_main_kb())

# Botni ishga tushirish
async def main():
    dp.include_router(router)
    print("Bot menyu bilan ishga tushdi...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
