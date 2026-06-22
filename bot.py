import logging
import asyncio
from aiogram import Bot, Dispatcher, Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import CommandStart

# Bot sozlamalari
BOT_TOKEN = "8893476065:AAFseE8gnPCvfV_GALln-PCvK-tz7Wihn40"
logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
router = Router()

# Coins paketlari (Nomi: Narxi)
COINS_PACKAGES = {
    "130 Coins": "15,000 so'm",
    "550 Coins": "60,000 so'm",
    "1050 Coins": "110,000 so'm",
    "2150 Coins": "210,000 so'm"
}

# Menyular
def get_main_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🛒 Coins sotib olish", callback_data="buy_menu")],
        [InlineKeyboardButton(text="🏆 Turnir", callback_data="tour_menu")]
    ])

def get_coins_kb():
    kb = []
    for name, price in COINS_PACKAGES.items():
        kb.append([InlineKeyboardButton(text=f"{name} ({price})", callback_data=f"buy_{name}")])
    kb.append([InlineKeyboardButton(text="⬅️ Ortga", callback_data="main_menu")])
    return InlineKeyboardMarkup(inline_keyboard=kb)

# Handlerlar
@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer("Assalomu alaykum! eFootball Coins botiga xush kelibsiz.", reply_markup=get_main_kb())

@router.callback_query(F.data == "main_menu")
async def back_to_main(callback: CallbackQuery):
    await callback.message.edit_text("Asosiy menyu:", reply_markup=get_main_kb())

@router.callback_query(F.data == "buy_menu")
async def buy_menu(callback: CallbackQuery):
    await callback.message.edit_text("Kerakli paketni tanlang:", reply_markup=get_coins_kb())

@router.callback_query(F.data.startswith("buy_"))
async def buy_package(callback: CallbackQuery):
    pkg_name = callback.data.split("_")[1]
    await callback.message.answer(f"Siz {pkg_name} ni tanladingiz. To'lovni amalga oshirish uchun adminga yozing.")

@router.callback_query(F.data == "tour_menu")
async def tour_menu(callback: CallbackQuery):
    await callback.message.edit_text("Turnir bo'limi hozircha tayyorlanmoqda.", reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="⬅️ Ortga", callback_data="main_menu")]]))

# Ishga tushirish
async def main():
    dp.include_router(router)
    print("Bot paketlar menyusi bilan ishlamoqda...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
