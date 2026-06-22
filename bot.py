import logging
import sqlite3
import asyncio
from aiogram import Bot, Dispatcher, Router, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.filters import CommandStart

# --- SOZLAMALAR ---
BOT_TOKEN = "8893476065:AAFseE8gnPCvfV_GALln-PCvK-tz7Wihn40"
ADMIN_ID = 1678146043

logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())
router = Router()

# --- HOLATLAR ---
class OrderStates(StatesGroup):
    get_email = State()
    get_pass = State()
    get_receipt = State()

# --- TUGMALAR ---
def get_main_kb():
    return ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="🛒 Android Coins"), KeyboardButton(text="🌍 Region Shop")],
        [KeyboardButton(text="🏆 Turnir"), KeyboardButton(text="🎁 Bonuslarim")],
        [KeyboardButton(text="⭐ Sharhlar"), KeyboardButton(text="👨‍💻 Admin / Yordam")]
    ], resize_keyboard=True)

# --- HANDLERLAR ---
@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer("Assalomu alaykum! eFootball Coins botiga xush kelibsiz.", reply_markup=get_main_kb())

# 1. Android Shop
@router.message(F.text == "🛒 Android Coins")
async def android_shop(message: Message):
    await message.answer("Android uchun paketni tanlang:", reply_markup=InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="130 Coins - 15,000", callback_data="buy_130")],
        [InlineKeyboardButton(text="550 Coins - 60,000", callback_data="buy_550")]
    ]))

# 2. Region Shop
@router.message(F.text == "🌍 Region Shop")
async def region_shop(message: Message):
    await message.answer("Regionni tanlang:", reply_markup=InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Global", callback_data="reg_Global")],
        [InlineKeyboardButton(text="Turkey", callback_data="reg_Turkey")]
    ]))

# 3, 4, 5, 6. Qo'shimcha bo'limlar
@router.message(F.text == "🏆 Turnir")
async def turnir_handler(message: Message):
    await message.answer("🏆 Hozirgi turnir: Guruh bosqichi davom etmoqda. Pley-off yaqin!")

@router.message(F.text == "🎁 Bonuslarim")
async def bonus_handler(message: Message):
    await message.answer("Sizning hisobingizda: 0 coin mavjud.")

@router.message(F.text == "⭐ Sharhlar")
async def reviews_handler(message: Message):
    await message.answer("Mijozlarimizdan kelgan sharhlar: \n'Zo'r bot, tez ishlaydi!' - @user1")

@router.message(F.text == "👨‍💻 Admin / Yordam")
async def support_handler(message: Message):
    await message.answer("Savollar bo'yicha adminga yozing: @admin_username")

# --- XARID JARAYONI (MyKonami Login) ---
@router.callback_query(F.data.startswith(("buy_", "reg_")))
async def start_order(callback: CallbackQuery, state: FSMContext):
    await state.update_data(info=callback.data)
    await callback.message.answer("Endi MyKonami Email manzilini yozing:")
    await state.set_state(OrderStates.get_email)

@router.message(OrderStates.get_email)
async def get_email(message: Message, state: FSMContext):
    await state.update_data(email=message.text)
    await message.answer("Endi MyKonami parolini yozing:")
    await state.set_state(OrderStates.get_pass)

@router.message(OrderStates.get_pass)
async def get_pass(message: Message, state: FSMContext):
    await state.update_data(password=message.text)
    await message.answer("Oxirgi qadam: To'lov chekini rasm ko'rinishida yuboring:")
    await state.set_state(OrderStates.get_receipt)

@router.message(OrderStates.get_receipt, F.photo)
async def process_receipt(message: Message, state: FSMContext):
    data = await state.get_data()
    
    # Adminga yuborish
    caption = (f"📦 YANGI BUYURTMA\n"
               f"Info: {data['info']}\n"
               f"Email: {data['email']}\n"
               f"Parol: {data['password']}\n"
               f"Mijoz: @{message.from_user.username}")
    
    await bot.send_photo(chat_id=ADMIN_ID, photo=message.photo[-1].file_id, caption=caption)
    await message.answer("✅ Rahmat! Buyurtmangiz admin tekshiruviga yuborildi.")
    await state.clear()

# --- ISHGA TUSHIRISH ---
async def main():
    dp.include_router(router)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
                          
