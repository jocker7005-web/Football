import logging
from aiogram import Bot, Dispatcher, Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
import asyncio

# --- SOZLAMALAR ---
BOT_TOKEN = "8893476065:AAFseE8gnPCvfV_GALln-PCvK-tz7Wihn40"
ADMIN_ID = 1678146043  # O'zingizning ID raqamingiz

logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())
router = Router()

# --- HOLATLAR ---
class OrderStates(StatesGroup):
    waiting_for_receipt = State()

# --- PAKETLAR ---
COINS_PACKAGES = {
    "130 Coins": "15,000 so'm",
    "550 Coins": "60,000 so'm",
    "1050 Coins": "110,000 so'm"
}

# --- TUGMALAR ---
def get_main_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🛒 Coins sotib olish", callback_data="buy_menu")]
    ])

def get_coins_kb():
    kb = []
    for name, price in COINS_PACKAGES.items():
        kb.append([InlineKeyboardButton(text=f"{name} ({price})", callback_data=f"buy_{name}")])
    return InlineKeyboardMarkup(inline_keyboard=kb)

# --- HANDLERLAR ---
@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer("Assalomu alaykum! eFootball Coins botiga xush kelibsiz.", reply_markup=get_main_kb())

@router.callback_query(F.data == "buy_menu")
async def buy_menu(callback: CallbackQuery):
    await callback.message.edit_text("Kerakli paketni tanlang:", reply_markup=get_coins_kb())

@router.callback_query(F.data.startswith("buy_"))
async def buy_package(callback: CallbackQuery, state: FSMContext):
    pkg_name = callback.data.split("_")[1]
    await state.update_data(chosen_pkg=pkg_name)
    await callback.message.answer(f"Siz {pkg_name} tanladingiz. Endi to'lov chekini (rasm) yuboring:")
    await state.set_state(OrderStates.waiting_for_receipt)

@router.message(OrderStates.waiting_for_receipt, F.photo)
async def process_receipt(message: Message, state: FSMContext):
    data = await state.get_data()
    pkg_name = data.get("chosen_pkg")
    photo_id = message.photo[-1].file_id
    
    # Admin ga yuborish
    await bot.send_photo(
        chat_id=ADMIN_ID, 
        photo=photo_id, 
        caption=f"🚨 YANGI BUYURTMA!\nMijoz: @{message.from_user.username or message.from_user.id}\nPaket: {pkg_name}"
    )
    
    await message.answer("Rahmat! Buyurtmangiz adminga yuborildi. Tez orada aloqaga chiqamiz.")
    await state.clear()

# --- ISHGA TUSHIRISH ---
async def main():
    dp.include_router(router)
    print("Bot muvaffaqiyatli ishga tushdi...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
