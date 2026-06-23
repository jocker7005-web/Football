import logging
import asyncio
from aiogram import Bot, Dispatcher, Router, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.filters import CommandStart

# --- SOZLAMALAR ---
BOT_TOKEN = "8893476065:AAFseE8gnPCvfV_GALln-PCvK-tz7Wihn40"
ADMIN_ID = 1678146043

# --- DATA ---
REGIONS = ["Япония", "ОАЭ", "Египет", "Канада", "Мексика", "Соединенные Штаты", "Саудовская Аравия", "Австралия", "Швеция", "Швейцария", "Великобритания", "Индонезия", "Малайзия"]
ANDROID_PRICES = {
    "260": 40000, "300": 45000, "390": 60000, "550": 70000, "750": 95000, 
    "1040": 125000, "1790": 210000, "2130": 240000, "2680": 310000, "3250": 350000, 
    "4000": 440000, "5700": 560000, "7040": 730000, "9990": 1050000, "12800": 1190000
}
REGION_PRICES = {
    "578": 70000, "788": 100000, "1092": 135000, "2237": 250000, "2815": 315000, 
    "3413": 370000, "4474": 500000, "5985": 600000, "13440": 1250000, "32200": 2800000
}

# --- SETUP ---
logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())
router = Router()

class ShopStates(StatesGroup):
    receipt = State()
    proposal = State()

# --- KEYBOARDS ---
def get_main_kb(user_id):
    kb = [
        [KeyboardButton(text="🛒 Android Coins"), KeyboardButton(text="🌍 Regionlar uchun Coins")],
        [KeyboardButton(text="✍️ Taklif qoldirish")]
    ]
    if user_id == ADMIN_ID:
        kb.append([KeyboardButton(text="🛠 Admin Panel")])
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

# --- NAVIGATION ---
@router.message(CommandStart(), state="*")
async def start(msg: Message, state: FSMContext):
    await state.clear()
    await msg.answer("Assalomu alaykum! Xush kelibsiz.", reply_markup=get_main_kb(msg.from_user.id))

# --- ANDROID ---
@router.message(F.text == "🛒 Android Coins", state="*")
async def shop_android(msg: Message, state: FSMContext):
    await state.clear()
    await state.update_data(region="Android")
    kb = [[InlineKeyboardButton(text=f"{k} coins - {v} so'm", callback_data=f"pkg_{k}_{v}")] for k, v in ANDROID_PRICES.items()]
    await msg.answer("Android paketini tanlang:", reply_markup=InlineKeyboardMarkup(inline_keyboard=kb))

# --- REGION ---
@router.message(F.text == "🌍 Regionlar uchun Coins", state="*")
async def shop_region(msg: Message, state: FSMContext):
    await state.clear()
    kb = [[InlineKeyboardButton(text=r, callback_data=f"reg_{r}")] for r in REGIONS]
    await msg.answer("Regionni tanlang:", reply_markup=InlineKeyboardMarkup(inline_keyboard=kb))

@router.callback_query(F.data.startswith("reg_"), state="*")
async def select_reg(call: CallbackQuery, state: FSMContext):
    reg = call.data.split("_")[1]
    await state.update_data(region=reg)
    kb = [[InlineKeyboardButton(text=f"{k} coins - {v} so'm", callback_data=f"pkg_{k}_{v}")] for k, v in REGION_PRICES.items()]
    await call.message.answer(f"{reg} uchun paketni tanlang:", reply_markup=InlineKeyboardMarkup(inline_keyboard=kb))

# --- BUYURTMA ---
@router.callback_query(F.data.startswith("pkg_"), state="*")
async def buy_pkg(call: CallbackQuery, state: FSMContext):
    _, coins, price = call.data.split("_")
    await state.update_data(coins=coins, price=price)
    await state.set_state(ShopStates.receipt)
    await call.message.answer(f"💰 Narx: {price} so'm.\nChekni rasm yuboring:")

@router.message(ShopStates.receipt, F.photo)
async def get_receipt(msg: Message, state: FSMContext):
    data = await state.get_data()
    reg = data.get("region", "Aniqlanmagan")
    await bot.send_photo(ADMIN_ID, msg.photo[-1].file_id, 
                         caption=f"📦 Yangi buyurtma!\n📍 Region: {reg}\n💰 Paket: {data['coins']} coins\n💵 Narx: {data['price']} so'm\n👤 User: @{msg.from_user.username}")
    await msg.answer("✅ Chek qabul qilindi. Admin tekshiradi.", reply_markup=get_main_kb(msg.from_user.id))
    await state.clear()

# --- TAKLIF ---
@router.message(F.text == "✍️ Taklif qoldirish", state="*")
async def prop_start(msg: Message, state: FSMContext):
    await state.clear()
    await state.set_state(ShopStates.proposal)
    await msg.answer("Taklifingizni yozing:")

@router.message(ShopStates.proposal)
async def prop_end(msg: Message, state: FSMContext):
    await bot.send_message(ADMIN_ID, f"💡 Taklif: {msg.text}")
    await msg.answer("Rahmat!", reply_markup=get_main_kb(msg.from_user.id))
    await state.clear()

async def main():
    dp.include_router(router)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
    
