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
ADMIN_ID = 1678146043  # O'z ID'ingizni tekshiring (minus belgisiz!)
CHANNEL_ID = "-1001908315496"
KARTA_RAQAM = "9860 3501 0897 5409"
KARTA_EGASI = "Xusanova M"

logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())
router = Router()

# --- MALUMOTLAR ---
REGIONS = ["Япония", "ОАЭ", "Египет", "Канада", "Мексика", "Соединенные Штаты", "Саудовская Аравия", "Австралия", "Швеция", "Швейцария", "Великобритания", "Индонезия", "Малайзия"]
ANDROID_PRICES = {"260 coins": 40000, "300 coins": 45000, "390 coins": 60000, "550 coins": 70000, "750 coins": 95000, "1040 coins": 125000, "1790 coins": 210000, "2130 coins": 240000, "2680 coins": 310000, "3250 coins": 350000, "4000 coins": 440000, "5700 coins": 560000, "7040 coins": 730000, "9990 coins": 1050000, "12800 coins": 1190000}
REGION_PRICES = {"578 coins": 70000, "788 coins": 100000, "1092 coins": 135000, "2237 coins": 250000, "2815 coins": 315000, "3413 coins": 370000, "4474 coins": 500000, "5985 coins": 600000, "13440 coins": 1250000, "32200 coins": 2800000}

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

# --- START & MENU HANDLERLARI ---
@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Assalomu alaykum! eFootball shop botiga xush kelibsiz.", reply_markup=get_main_kb(message.from_user.id))

@router.message(F.text == "🛒 Android Coins")
async def shop_android(message: Message, state: FSMContext):
    await state.clear()
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=f"{k} - {v:,} so'm", callback_data=f"pkg_a_{k.split()[0]}_{v}")] for k, v in ANDROID_PRICES.items()])
    await message.answer("Android paketini tanlang:", reply_markup=kb)

@router.message(F.text == "🌍 Regionlar uchun Coins")
async def shop_region(message: Message, state: FSMContext):
    await state.clear()
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=r, callback_data=f"reg_{r}")] for r in REGIONS])
    await message.answer("Regionni tanlang:", reply_markup=kb)

# --- ADMIN PANEL ---
@router.message(F.text == "🛠 Admin Panel")
async def admin_panel(message: Message):
    if message.from_user.id == ADMIN_ID:
        await message.answer("🛠 Admin Panel:\n1. Yangi buyurtmalarni ko'ring.\n2. Tasdiqlash tugmasini bosing.")
    else:
        await message.answer("Siz admin emassiz.")

# --- QOLGAN FUNKSIYALAR ---
@router.callback_query(F.data.startswith("reg_"))
async def choose_reg(callback: CallbackQuery):
    reg = callback.data.split("_")[1]
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=f"{k} - {v:,} so'm", callback_data=f"pkg_r_{k.split()[0]}_{v}")] for k, v in REGION_PRICES.items()])
    await callback.message.answer(f"{reg} uchun paketni tanlang:", reply_markup=kb)

@router.callback_query(F.data.startswith("pkg_"))
async def order(callback: CallbackQuery, state: FSMContext):
    data = callback.data.split("_")
    await state.update_data(coins=data[2], price=data[3])
    await state.set_state(OrderStates.waiting_receipt)
    await callback.message.answer(f"💳 To'lov: {KARTA_RAQAM}\n👤 {KARTA_EGASI}\n💰 Narx: {data[3]} so'm\n\nIltimos, chekni rasm sifatida yuboring:")

@router.message(OrderStates.waiting_receipt, F.photo)
async def get_receipt(message: Message, state: FSMContext):
    data = await state.get_data()
    await message.answer("✅ Chek qabul qilindi. Admin tasdiqlashini kuting.")
    await bot.send_photo(ADMIN_ID, message.photo[-1].file_id, caption=f"📦 Yangi buyurtma!\nPaket: {data['coins']}\nNarx: {data['price']} so'm\nUser: @{message.from_user.username}",
                         reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="✅ Tasdiqlash", callback_data=f"ok_{message.from_user.id}")]]))
    await state.clear()

@router.message(F.text == "✍️ Taklif qoldirish")
async def proposal_start(m: Message, state: FSMContext):
    await state.set_state(OrderStates.waiting_proposal)
    await m.answer("Taklifingizni yozib yuboring:")

@router.message(OrderStates.waiting_proposal)
async def get_proposal(m: Message, state: FSMContext):
    await bot.send_message(ADMIN_ID, f"💡 Yangi taklif: @{m.from_user.username}\nMatn: {m.text}")
    await m.answer("Rahmat! Taklifingiz qabul qilindi.")
    await state.clear()

# Boshqa tugmalar uchun ham shunday "await state.clear()" qo'shib chiqish kerak
@router.message(F.text.in_(["🏆 Turnir", "🎁 Bonuslarim", "📖 Qo'llanma", "📦 Mening buyurtmalarim", "⭐ Sharhlar", "👨‍💻 Admin / Yordam"]))
async def other_buttons(m: Message, state: FSMContext):
    await state.clear()
    await m.answer("Bu bo'lim ustida ish olib borilmoqda.")

async def main():
    dp.include_router(router)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
    
