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
ADMIN_ID = 1678146043  # O'z ID'ingizni tekshiring (MINUS BELGISIZ!)
CHANNEL_ID = "-1001908315496"
KARTA_RAQAM = "9860 3501 0897 5409"
KARTA_EGASI = "Xusanova M"

logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())
router = Router()

# --- MALUMOTLAR ---
REGIONS = ["Япония", "ОАЭ", "Египет", "Канада", "Мексика", "Соединенные Штаты", "Саудовская Аравия", "Австралия", "Швеция", "Швейцария", "Великобритания", "Индонезия", "Малайзия"]
ANDROID_PRICES = {"260 coins": 40000, "300 coins": 45000, "550 coins": 70000, "1040 coins": 125000, "5700 coins": 560000}
REGION_PRICES = {"578 coins": 70000, "788 coins": 100000, "1092 coins": 135000, "2237 coins": 250000, "32200 coins": 2800000}

class OrderStates(StatesGroup):
    waiting_receipt = State()
    waiting_proposal = State()

# --- DYNAMIC KEYBOARD ---
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

# --- START & MENU (HAR DOIM STATE NI TOZALAYDI) ---
@router.message(CommandStart(), state="*")
async def start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Assalomu alaykum! Xush kelibsiz.", reply_markup=get_main_kb(message.from_user.id))

@router.message(F.text == "🛒 Android Coins", state="*")
async def shop_android(message: Message, state: FSMContext):
    await state.clear()
    await state.update_data(region="Android") # Regionni Android deb belgilaymiz
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=f"{k} - {v:,} so'm", callback_data=f"pkg_{k.split()[0]}_{v}")] for k, v in ANDROID_PRICES.items()])
    await message.answer("Android paketini tanlang:", reply_markup=kb)

@router.message(F.text == "🌍 Regionlar uchun Coins", state="*")
async def shop_region(message: Message, state: FSMContext):
    await state.clear()
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=r, callback_data=f"reg_{r}")] for r in REGIONS])
    await message.answer("Regionni tanlang:", reply_markup=kb)

# --- CALLBACK LOGIKA ---
@router.callback_query(F.data.startswith("reg_"))
async def choose_reg(callback: CallbackQuery, state: FSMContext):
    reg = callback.data.split("_")[1]
    await state.update_data(region=reg) # Regionni xotiraga saqlaymiz
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=f"{k} - {v:,} so'm", callback_data=f"pkg_{k.split()[0]}_{v}")] for k, v in REGION_PRICES.items()])
    await callback.message.answer(f"{reg} uchun paketni tanlang:", reply_markup=kb)

@router.callback_query(F.data.startswith("pkg_"))
async def order_start(callback: CallbackQuery, state: FSMContext):
    data = callback.data.split("_")
    await state.update_data(coins=data[1], price=data[2])
    await state.set_state(OrderStates.waiting_receipt)
    await callback.message.answer(f"💰 Narx: {data[2]} so'm.\nIltimos, chekni rasm sifatida yuboring:")

# --- CHEKNI QABUL QILISH ---
@router.message(OrderStates.waiting_receipt, F.photo)
async def get_receipt(message: Message, state: FSMContext):
    data = await state.get_data()
    region_val = data.get('region', 'Noma\'lum')
    
    # Adminga yuborish
    await bot.send_photo(ADMIN_ID, message.photo[-1].file_id, 
                         caption=f"📦 Yangi buyurtma!\n📍 Region: {region_val}\n💰 Paket: {data['coins']}\n💵 Narx: {data['price']} so'm\n👤 User: @{message.from_user.username}",
                         reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="✅ Tasdiqlash", callback_data="ok")]]))
    
    await message.answer("✅ Chek qabul qilindi. Admin tez orada tekshiradi.", reply_markup=get_main_kb(message.from_user.id))
    await state.clear() # Muhim: Holat tozalandi

# --- TAKLIF QOLDIRISH ---
@router.message(F.text == "✍️ Taklif qoldirish", state="*")
async def proposal_start(message: Message, state: FSMContext):
    await state.clear()
    await state.set_state(OrderStates.waiting_proposal)
    await message.answer("Taklifingizni yozib yuboring:")

@router.message(OrderStates.waiting_proposal)
async def get_proposal(message: Message, state: FSMContext):
    await bot.send_message(ADMIN_ID, f"💡 Yangi taklif: @{message.from_user.username}\nMatn: {message.text}")
    await message.answer("Rahmat! Qabul qilindi.", reply_markup=get_main_kb(message.from_user.id))
    await state.clear()

# --- ADMIN PANEL ---
@router.message(F.text == "🛠 Admin Panel", state="*")
async def admin_panel(message: Message, state: FSMContext):
    await state.clear()
    if message.from_user.id == ADMIN_ID:
        await message.answer("🛠 Admin Panel: Yangi buyurtmalarni kuting.")
    else:
        await message.answer("Siz admin emassiz.")

async def main():
    dp.include_router(router)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
    
