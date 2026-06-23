import logging
import sqlite3
import asyncio
from aiogram import Bot, Dispatcher, Router, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.filters import CommandStart

# --- SOZLAMALAR ---
BOT_TOKEN = "8893476065:AAFseE8gnPCvfV_GALln-PCvK-tz7Wihn40"
ADMIN_ID = 1678146043  # Faqat raqam
CHANNEL_ID = "-1001908315496"
KARTA_RAQAM = "9860 3501 0897 5409"
KARTA_EGASI = "Xusanova M"

# --- LOGGING & BOT ---
logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)
router = Router()

# --- HOLATLAR ---
class OrderStates(StatesGroup):
    waiting_receipt = State()
    waiting_proposal = State()

# --- KIBOARDLAR ---
def get_main_kb(user_id):
    kb_list = [
        [KeyboardButton(text="🛒 Android Coins"), KeyboardButton(text="🌍 Regionlar uchun Coins")],
        [KeyboardButton(text="🏆 Turnir"), KeyboardButton(text="🎁 Bonuslarim")],
        [KeyboardButton(text="📖 Qo'llanma"), KeyboardButton(text="📦 Mening buyurtmalarim")],
        [KeyboardButton(text="⭐ Sharhlar"), KeyboardButton(text="✍️ Taklif qoldirish")],
        [KeyboardButton(text="👨‍💻 Admin / Yordam")]
    ]
    if user_id == ADMIN_ID:
        kb_list.append([KeyboardButton(text="🛠 Admin Panel")])
    return ReplyKeyboardMarkup(keyboard=kb_list, resize_keyboard=True)

# --- ASOSIY HANDLERLAR ---
@router.message(CommandStart())
async def start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Assalomu alaykum! Botga xush kelibsiz.", reply_markup=get_main_kb(message.from_user.id))

@router.message(F.text == "🛒 Android Coins")
async def shop_android(message: Message, state: FSMContext):
    await state.clear()
    await state.update_data(region="Android")
    prices = {"260 coins": 40000, "300 coins": 45000, "550 coins": 70000}
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=f"{k} - {v} so'm", callback_data=f"pkg_{k.split()[0]}_{v}")] for k, v in prices.items()])
    await message.answer("Paket tanlang:", reply_markup=kb)

@router.message(F.text == "🌍 Regionlar uchun Coins")
async def shop_region(message: Message, state: FSMContext):
    await state.clear()
    regions = ["Япония", "ОАЭ", "Египет", "Канада"]
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=r, callback_data=f"reg_{r}")] for r in regions])
    await message.answer("Regionni tanlang:", reply_markup=kb)

@router.callback_query(F.data.startswith("reg_"))
async def choose_reg(callback: CallbackQuery, state: FSMContext):
    reg = callback.data.split("_")[1]
    await state.update_data(region=reg)
    prices = {"578 coins": 70000, "788 coins": 100000}
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=f"{k} - {v} so'm", callback_data=f"pkg_{k.split()[0]}_{v}")] for k, v in prices.items()])
    await callback.message.answer(f"{reg} tanlandi. Paketni tanlang:", reply_markup=kb)

@router.callback_query(F.data.startswith("pkg_"))
async def order_start(callback: CallbackQuery, state: FSMContext):
    data = callback.data.split("_")
    await state.update_data(coins=data[1], price=data[2])
    await state.set_state(OrderStates.waiting_receipt)
    await callback.message.answer(f"Narx: {data[2]} so'm. Chekni rasm sifatida yuboring:")

@router.message(OrderStates.waiting_receipt, F.photo)
async def get_receipt(message: Message, state: FSMContext):
    data = await state.get_data()
    region = data.get('region', 'Noma\'lum')
    
    await bot.send_photo(ADMIN_ID, message.photo[-1].file_id, 
                         caption=f"📦 Buyurtma!\n📍 Region: {region}\n💰 Paket: {data['coins']}\n💵 Narx: {data['price']}")
    await message.answer("✅ Chek qabul qilindi.", reply_markup=get_main_kb(message.from_user.id))
    await state.clear()

@router.message(F.text == "✍️ Taklif qoldirish")
async def prop_start(message: Message, state: FSMContext):
    await state.clear()
    await state.set_state(OrderStates.waiting_proposal)
    await message.answer("Taklifingizni yozing:")

@router.message(OrderStates.waiting_proposal)
async def get_prop(message: Message, state: FSMContext):
    await bot.send_message(ADMIN_ID, f"💡 Taklif: {message.text}")
    await message.answer("Rahmat!", reply_markup=get_main_kb(message.from_user.id))
    await state.clear()

# Boshqa tugmalar uchun umumiy handler
@router.message(F.text.in_(["🏆 Turnir", "🎁 Bonuslarim", "📖 Qo'llanma", "📦 Mening buyurtmalarim", "⭐ Sharhlar", "👨‍💻 Admin / Yordam", "🛠 Admin Panel"]))
async def other_stuff(message: Message, state: FSMContext):
    await state.clear()
    if message.text == "🛠 Admin Panel" and message.from_user.id == ADMIN_ID:
        await message.answer("🛠 Admin Panel aktiv.")
    else:
        await message.answer("Ushbu bo'lim ustida ishlanmoqda.")

async def main():
    dp.include_router(router)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
    
