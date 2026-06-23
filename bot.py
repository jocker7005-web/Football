import logging
import sqlite3
import asyncio
from aiogram import Bot, Dispatcher, Router, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.filters import CommandStart, Command, CommandObject

# --- SOZLAMALAR ---
BOT_TOKEN = "8893476065:AAFseE8gnPCvfV_GALln-PCvK-tz7Wihn40"
ADMIN_ID = 1678146043  # Faqat musbat raqam!
CHANNEL_ID = "-1001908315496"
KARTA_RAQAM = "9860 3501 0897 5409"
KARTA_EGASI = "Xusanova M"

# Logging tizimi
logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())
router = Router()

# --- BAZA VA STATE ---
class OrderStates(StatesGroup):
    receipt = State()
    proposal = State()
    region_choice = State()

def init_db():
    conn = sqlite3.connect("bot_shop.db")
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, balance INTEGER DEFAULT 0, referrals INTEGER DEFAULT 0)")
    cursor.execute("CREATE TABLE IF NOT EXISTS orders (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, info TEXT, coins TEXT, price INTEGER, status TEXT, photo_id TEXT)")
    conn.commit()
    conn.close()

# --- MENYULAR ---
def get_main_kb():
    kb = ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="🛒 Android Coins"), KeyboardButton(text="🌍 Regionlar uchun Coins")],
        [KeyboardButton(text="🏆 Turnir"), KeyboardButton(text="🎁 Bonuslarim")],
        [KeyboardButton(text="📖 Qo'llanma"), KeyboardButton(text="📦 Mening buyurtmalarim")],
        [KeyboardButton(text="⭐ Sharhlar"), KeyboardButton(text="✍️ Taklif qoldirish")],
        [KeyboardButton(text="👨‍💻 Admin / Yordam")]
    ], resize_keyboard=True)
    return kb

# --- ANDROID VA REGION NARXLARI (RASMLAR BOYICHA) ---
ANDROID_PRICES = {
    "260 coins": 40000, "300 coins": 45000, "390 coins": 60000, "550 coins": 70000,
    "750 coins": 95000, "1040 coins": 125000, "1790 coins": 210000, "2130 coins": 240000,
    "2680 coins": 310000, "3250 coins": 350000, "4000 coins": 440000, "5700 coins": 560000,
    "7040 coins": 730000, "9990 coins": 1050000, "12800 coins": 1190000
}

REGION_PRICES = {
    "578 coins": 70000, "788 coins": 100000, "1092 coins": 135000, "2237 coins": 250000,
    "2815 coins": 315000, "3413 coins": 370000, "4474 coins": 500000, "5985 coins": 600000,
    "13440 coins": 1250000, "32200 coins": 2800000
}

# --- HANDLERLAR ---
@router.message(CommandStart())
async def cmd_start(message: Message):
    init_db()
    await message.answer("Assalomu alaykum! eFootball shop botiga xush kelibsiz.", reply_markup=get_main_kb())

@router.message(F.text == "🛒 Android Coins")
async def shop_android(message: Message):
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=f"{k} - {v:,} so'm", callback_data=f"pkg_a_{k.split()[0]}_{v}")] for k, v in ANDROID_PRICES.items()])
    await message.answer("Android paketini tanlang:", reply_markup=kb)

@router.message(F.text == "🌍 Regionlar uchun Coins")
async def shop_region(message: Message):
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=f"{k} - {v:,} so'm", callback_data=f"pkg_r_{k.split()[0]}_{v}")] for k, v in REGION_PRICES.items()])
    await message.answer("Region uchun paketni tanlang:", reply_markup=kb)

# --- BUYURTMA JARAYONI ---
@router.callback_query(F.data.startswith("pkg_"))
async def order_process(callback: CallbackQuery, state: FSMContext):
    type, coins, price = callback.data.split("_")[1], callback.data.split("_")[2], callback.data.split("_")[3]
    await state.update_data(coins=coins, price=price, type=type)
    await callback.message.answer(f"💳 To'lov: {KARTA_RAQAM}\n👤 {KARTA_EGASI}\n💰 Narx: {price} so'm\n\nChekni rasm sifatida yuboring:")
    await state.set_state(OrderStates.receipt)

@router.message(OrderStates.receipt, F.photo)
async def get_receipt(message: Message, state: FSMContext):
    data = await state.get_data()
    conn = sqlite3.connect("bot_shop.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO orders (user_id, info, coins, price, status, photo_id) VALUES (?, ?, ?, ?, ?, ?)", 
                   (message.from_user.id, data['type'], data['coins'], data['price'], "kutilmoqda", message.photo[-1].file_id))
    oid = cursor.lastrowid
    conn.commit()
    conn.close()
    
    await message.answer(f"✅ Chek qabul qilindi. Buyurtma raqami: #{oid}")
    await bot.send_photo(ADMIN_ID, message.photo[-1].file_id, caption=f"📦 Yangi buyurtma #{oid}\nPaket: {data['coins']}\nUser: @{message.from_user.username}",
                         reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="✅ Tasdiqlash", callback_data=f"ok_{oid}_{message.from_user.id}")]]))
    await state.clear()

# --- ADMIN PANEL ---
@router.callback_query(F.data.startswith("ok_"))
async def admin_ok(c: CallbackQuery):
    oid, uid = c.data.split("_")[1], c.data.split("_")[2]
    conn = sqlite3.connect("bot_shop.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE orders SET status = 'tasdiqlangan' WHERE id = ?", (oid,))
    conn.commit()
    conn.close()
    
    await bot.send_message(uid, f"✅ Buyurtmangiz #{oid} bajarildi! Rahmat!")
    await c.message.edit_caption(caption=f"✅ #{oid} TASDIQLANDI")
    try: await bot.send_message(CHANNEL_ID, f"🎉 Mijoz #{oid} buyurtmasi bajarildi! Rahmat!")
    except: pass

@router.message(F.text == "🏆 Turnir")
async def turnir(m: Message): await m.answer("🏆 Hozirda turnir mavjud emas.")

@router.message(F.text == "⭐ Sharhlar")
async def sharhlar(m: Message): await m.answer(f"Sharhlar kanali: https://t.me/c/{abs(int(CHANNEL_ID)) % 1000000000000}/1")

@router.message(F.text == "✍️ Taklif qoldirish")
async def proposal_start(m: Message, state: FSMContext):
    await m.answer("Taklifingizni yozing:")
    await state.set_state(OrderStates.proposal)

@router.message(OrderStates.proposal)
async def get_proposal(m: Message, state: FSMContext):
    await bot.send_message(ADMIN_ID, f"💡 Yangi taklif: @{m.from_user.username}\nMatn: {m.text}")
    await m.answer("Rahmat! Qabul qilindi.")
    await state.clear()

async def main():
    dp.include_router(router)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
    
