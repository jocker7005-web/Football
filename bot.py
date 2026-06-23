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
ADMIN_ID = 1678146043
CHANNEL_ID = "-1001908315496"  # SHU YERGA O'Z KANAL ID INGIZNI YOZING
KARTA_RAQAM = "9860 3501 0897 5409"
KARTA_EGASI = "Xusanova M"

logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())
router = Router()

class OrderStates(StatesGroup):
    receipt = State()
    proposal = State()

def init_db():
    conn = sqlite3.connect("bot_shop.db")
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, referrer_id INTEGER, balance INTEGER DEFAULT 0)")
    cursor.execute("CREATE TABLE IF NOT EXISTS orders (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, info TEXT, coins_amount INTEGER, status TEXT, photo_id TEXT)")
    conn.commit()
    conn.close()

def get_main_kb():
    return ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="🛒 Android Coins"), KeyboardButton(text="🌍 Regionlar uchun Coins")],
        [KeyboardButton(text="🏆 Turnir"), KeyboardButton(text="🎁 Bonuslarim")],
        [KeyboardButton(text="📖 Qo'llanma"), KeyboardButton(text="📦 Mening buyurtmalarim")],
        [KeyboardButton(text="⭐ Sharhlar"), KeyboardButton(text="✍️ Taklif qoldirish")],
        [KeyboardButton(text="👨‍💻 Admin / Yordam")]
    ], resize_keyboard=True)

# --- BONUS VA YECHISH ---
@router.message(F.text == "🎁 Bonuslarim")
async def bonus(m: Message):
    conn = sqlite3.connect("bot_shop.db")
    bal = conn.cursor().execute("SELECT balance FROM users WHERE user_id = ?", (m.from_user.id,)).fetchone()
    conn.close()
    balance = bal[0] if bal else 0
    
    kb = None
    if balance >= 550:
        kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="💰 Bonusni yechish", callback_data="withdraw")]])
    
    await m.answer(f"💰 Sizdagi bonus: {balance} coin.", reply_markup=kb)

@router.callback_query(F.data == "withdraw")
async def withdraw(c: CallbackQuery):
    await bot.send_message(ADMIN_ID, f"⚠️ Mijoz {c.from_user.id} 550+ bonusini yechmoqchi! Bog'laning.")
    await c.message.answer("✅ So'rov adminga yuborildi. Siz bilan bog'lanamiz.")

# --- ADMIN TASDIQ (OTZYV BILAN) ---
@router.callback_query(F.data.startswith("ok_"))
async def admin_ok(c: CallbackQuery):
    _, oid, uid = c.data.split("_")
    conn = sqlite3.connect("bot_shop.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE orders SET status = 'tasdiqlangan' WHERE id = ?", (oid,))
    cursor.execute("SELECT referrer_id FROM users WHERE user_id = ?", (uid,))
    ref = cursor.fetchone()[0]
    if ref: cursor.execute("UPDATE users SET balance = balance + 10 WHERE user_id = ?", (ref,))
    conn.commit()
    conn.close()
    
    # Kanalga otzyv yuborish
    try:
        await bot.send_message(CHANNEL_ID, f"🎉 Mijoz #{oid} buyurtmasi bajarildi! Rahmat!")
    except: pass
    
    await bot.send_message(uid, f"✅ Buyurtmangiz #{oid} bajarildi! Fikringizni /taklif orqali bildiring.")
    await c.message.edit_caption(caption=f"✅ #{oid} TASDIQLANDI")

# --- QOLGAN FUNKSIYALAR ---
@router.message(CommandStart())
async def start(message: Message, command: CommandObject):
    conn = sqlite3.connect("bot_shop.db")
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO users (user_id, referrer_id) VALUES (?, ?)", (message.from_user.id, command.args))
    conn.commit()
    conn.close()
    await message.answer("Assalomu alaykum! Xush kelibsiz.", reply_markup=get_main_kb())

@router.message(F.text.in_(["🛒 Android Coins", "🌍 Regionlar uchun Coins"]))
async def shop(message: Message, state: FSMContext):
    prices = {"578 coins": 70000, "788 coins": 100000} # Qo'shib chiqing
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=f"{k} - {v} so'm", callback_data=f"pkg_{k.split()[0]}_{v}")] for k, v in prices.items()])
    await message.answer("Paketni tanlang:", reply_markup=kb)

@router.callback_query(F.data.startswith("pkg_"))
async def get_pkg(callback: CallbackQuery, state: FSMContext):
    coins, price = callback.data.split("_")[1], callback.data.split("_")[2]
    await state.update_data(coins=coins, price=price)
    await callback.message.answer(f"💳 Karta: {KARTA_RAQAM}\n👤 {KARTA_EGASI}\n\nChekni rasm sifatida yuboring:")
    await state.set_state(OrderStates.receipt)

@router.message(OrderStates.receipt, F.photo)
async def get_receipt(message: Message, state: FSMContext):
    data = await state.get_data()
    conn = sqlite3.connect("bot_shop.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO orders (user_id, info, coins_amount, status, photo_id) VALUES (?, ?, ?, ?, ?)", 
                   (message.from_user.id, "Buyurtma", data['coins'], "kutilmoqda", message.photo[-1].file_id))
    oid = cursor.lastrowid
    conn.commit()
    conn.close()
    await message.answer(f"✅ Chek qabul qilindi. ID: #{oid}")
    await bot.send_photo(ADMIN_ID, message.photo[-1].file_id, caption=f"📦 Buyurtma #{oid}\nPaket: {data['coins']}", reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="✅ Tasdiqlash", callback_data=f"ok_{oid}_{message.from_user.id}")]]))
    await state.clear()

async def main():
    init_db()
    dp.include_router(router)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
    
