import logging
import sqlite3
import asyncio
from aiogram import Bot, Dispatcher, Router, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.filters import CommandStart, Command, CommandObject

# --- KONFIGURATSIYA ---
BOT_TOKEN = "8893476065:AAFseE8gnPCvfV_GALln-PCvK-tz7Wihn40"
ADMIN_ID = 1678146043
CHANNEL_ID = "-1001908315496"
KARTA_RAQAM = "9860 3501 0897 5409"
KARTA_EGASI = "Xusanova M"

# --- SOZLAMALAR ---
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
    cursor.execute("CREATE TABLE IF NOT EXISTS orders (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, info TEXT, coins_amount TEXT, status TEXT, photo_id TEXT)")
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

# --- START VA REGISTRATSIYA ---
@router.message(CommandStart())
async def start(message: Message, command: CommandObject):
    conn = sqlite3.connect("bot_shop.db")
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO users (user_id, referrer_id) VALUES (?, ?)", (message.from_user.id, command.args))
    conn.commit()
    conn.close()
    await message.answer("Assalomu alaykum! eFootball Coins botiga xush kelibsiz.", reply_markup=get_main_kb())

# --- SHOP (ANDROID VA REGION) ---
@router.message(F.text == "🛒 Android Coins")
async def shop_android(message: Message, state: FSMContext):
    await state.update_data(shop="Android")
    prices = {
        "260 coins": 40000, "300 coins": 45000, "390 coins": 60000, 
        "550 coins": 70000, "750 coins": 95000, "1040 coins": 125000, 
        "1790 coins": 210000, "2130 coins": 240000, "2680 coins": 310000, 
        "3250 coins": 350000, "4000 coins": 440000, "5700 coins": 560000, 
        "7040 coins": 730000, "9990 coins": 1050000, "12800 coins": 1190000
    }
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=f"{k} - {v:,} so'm", callback_data=f"pkg_{k.split()[0]}_{v}")] for k, v in prices.items()])
    await message.answer("Android uchun paketni tanlang:", reply_markup=kb)

@router.message(F.text == "🌍 Regionlar uchun Coins")
async def shop_region(message: Message, state: FSMContext):
    await state.update_data(shop="Region")
    prices = {
        "578 coins": 70000, "788 coins": 100000, "1092 coins": 135000, 
        "2237 coins": 250000, "2815 coins": 315000, "3413 coins": 370000, 
        "4474 coins": 500000, "5985 coins": 600000, "13440 coins": 1250000, 
        "32200 coins": 2800000
    }
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=f"{k} - {v:,} so'm", callback_data=f"pkg_{k.split()[0]}_{v}")] for k, v in prices.items()])
    await message.answer("Region uchun paketni tanlang:", reply_markup=kb)

@router.callback_query(F.data.startswith("pkg_"))
async def get_pkg(callback: CallbackQuery, state: FSMContext):
    _, coins, price = callback.data.split("_")
    await state.update_data(coins=coins, price=price)
    await callback.message.answer(f"💳 To'lov: {KARTA_RAQAM}\n👤 {KARTA_EGASI}\n💰 Narx: {price} so'm\n\nIltimos, chekni rasm ko'rinishida yuboring:")
    await state.set_state(OrderStates.receipt)

@router.message(OrderStates.receipt, F.photo)
async def get_receipt(message: Message, state: FSMContext):
    data = await state.get_data()
    conn = sqlite3.connect("bot_shop.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO orders (user_id, info, coins_amount, status, photo_id) VALUES (?, ?, ?, ?, ?)", 
                   (message.from_user.id, data['shop'], data['coins'], "kutilmoqda", message.photo[-1].file_id))
    oid = cursor.lastrowid
    conn.commit()
    conn.close()
    
    await message.answer(f"✅ Chek qabul qilindi. ID: #{oid}")
    await bot.send_photo(ADMIN_ID, message.photo[-1].file_id, caption=f"📦 Buyurtma #{oid}\nPaket: {data['coins']}\nUser: @{message.from_user.username}", 
                         reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="✅ Tasdiqlash", callback_data=f"ok_{oid}_{message.from_user.id}")]]))
    await state.clear()

# --- ADMIN TASDIQ ---
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
    
    await bot.send_message(uid, f"✅ Buyurtmangiz #{oid} bajarildi! Fikringizni bildiring: /taklif")
    await c.message.edit_caption(caption=f"✅ #{oid} TASDIQLANDI")
    try: await bot.send_message(CHANNEL_ID, f"🎉 Mijoz #{oid} buyurtmasi bajarildi! Rahmat!")
    except: pass

# --- BONUSLAR ---
@router.message(F.text == "🎁 Bonuslarim")
async def bonus(m: Message):
    conn = sqlite3.connect("bot_shop.db")
    bal = conn.cursor().execute("SELECT balance FROM users WHERE user_id = ?", (m.from_user.id,)).fetchone()
    conn.close()
    balance = bal[0] if bal else 0
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="💰 Bonusni yechish", callback_data="withdraw")]]) if balance >= 550 else None
    await m.answer(f"💰 Sizdagi bonus: {balance} coin.\n{'(Bonus yechish mumkin!)' if balance >= 550 else ''}", reply_markup=kb)

@router.callback_query(F.data == "withdraw")
async def withdraw(c: CallbackQuery):
    await bot.send_message(ADMIN_ID, f"⚠️ Mijoz {c.from_user.id} 550+ bonusini yechmoqchi!")
    await c.message.answer("✅ So'rov adminga yuborildi.")

# --- QOLGAN MENYULAR ---
@router.message(F.text == "📦 Mening buyurtmalarim")
async def my_orders(m: Message):
    conn = sqlite3.connect("bot_shop.db")
    orders = conn.cursor().execute("SELECT id, status FROM orders WHERE user_id = ?", (m.from_user.id,)).fetchall()
    conn.close()
    txt = "\n".join([f"#{o[0]} - {o[1]}" for o in orders])
    await m.answer(f"Sizning buyurtmalaringiz:\n{txt}" if txt else "Buyurtmalar mavjud emas.")

@router.message(F.text == "📖 Qo'llanma")
async def guide(m: Message):
    await m.answer("📖 **MyKonami ID uchun qo'llanma:**\n1. Extras -> Support -> Data Transfer\n2. Link to KONAMI ID account\n3. Email/Parol kiritib, 'Success' yozuvini kuting.")

@router.message(F.text == "✍️ Taklif qoldirish")
async def proposal_start(m: Message, state: FSMContext):
    await m.answer("Taklif yoki shikoyatingizni yozing:")
    await state.set_state(OrderStates.proposal)

@router.message(OrderStates.proposal)
async def get_proposal(m: Message, state: FSMContext):
    await bot.send_message(ADMIN_ID, f"💡 Yangi taklif: @{m.from_user.username}\nMatn: {m.text}")
    await m.answer("Rahmat! Taklifingiz qabul qilindi.")
    await state.clear()

@router.message(F.text == "👨‍💻 Admin / Yordam")
async def help_cmd(m: Message):
    await m.answer("Savollaringiz bo'lsa @admin_username ga yozing.")

async def main():
    init_db()
    dp.include_router(router)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
    
