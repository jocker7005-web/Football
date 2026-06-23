import os
import json
import logging
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

logging.basicConfig(level=logging.INFO)

# --- MAXFIY MA'LUMOTLAR VA KONSTANTALAR ---
BOT_TOKEN = "8893476065:AAFseE8gnPCvfV_GALln-PCvK-tz7Wihn40"
ADMIN_ID = 1678146043
KARTA = "9860 3501 0897 5409 (Xusanova M)"
REVIEWS_CHANNEL = -1001908315496

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# AMVERA HOSTINGIDA MA'LUMOTLAR O'CHIB KETMASLIGI UCHUN MAXSUS /data/ PAPKASI
DATA_DIR = "/data"
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)
DATA_FILE = os.path.join(DATA_DIR, "bot_data.json")

# --- MA'LUMOTLAR BAZASI FUNKSIYALARI ---
def load_data():
    if not os.path.exists(DATA_FILE):
        return {"last_id": 1000, "orders": {}, "users": {}, "tournament": []}
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {"last_id": 1000, "orders": {}, "users": {}, "tournament": []}

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def init_user(user_id, username=None, full_name=None):
    data = load_data()
    s_user_id = str(user_id)
    if s_user_id not in data["users"]:
        data["users"][s_user_id] = {
            "bonus": 0,
            "referred_by": None,
            "referrals_count": 0,
            "has_purchased": False,
            "username": username or "Mijoz",
            "full_name": full_name or "Mijoz"
        }
        save_data(data)
    else:
        # Username yoki Ism o'zgargan bo'lsa yangilab qo'yamiz
        if username: data["users"][s_user_id]["username"] = username
        if full_name: data["users"][s_user_id]["full_name"] = full_name
        save_data(data)

# --- FSM HOLATLARI ---
class BotStates(StatesGroup):
    choosing_android_coins = State()
    choosing_region = State()
    choosing_region_coins = State()
    entering_credentials = State()
    sending_receipt = State()
    writing_review = State()
    writing_suggestion = State()

# --- ASOSIY MENYU (REPLY MENYU) ---
def get_main_menu(user_id):
    builder = ReplyKeyboardBuilder()
    builder.row(types.KeyboardButton(text="🛒 Android Coins"), types.KeyboardButton(text="🌍 Regionlar uchun Coins"))
    builder.row(types.KeyboardButton(text="🏆 Turnir"), types.KeyboardButton(text="🎁 Bonuslarim"))
    builder.row(types.KeyboardButton(text="📖 Qo'llanma"), types.KeyboardButton(text="📦 Mening buyurtmalarim"))
    builder.row(types.KeyboardButton(text="⭐ Sharhlar"), types.KeyboardButton(text="✍️ Taklif qoldirish"))
    builder.row(types.KeyboardButton(text="👨‍💻 Admin / Yordam"))
    if user_id == ADMIN_ID:
        builder.row(types.KeyboardButton(text="🛠 Admin Panel"))
    return builder.as_markup(resize_keyboard=True)

# --- START KOMANDASI (REFERAL TIZIMI BILAN) ---
@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    user_id = message.from_user.id
    username = message.from_user.username
    full_name = message.from_user.full_name
    init_user(user_id, username, full_name)
    
    args = message.text.split()
    if len(args) > 1:
        referrer_id = args[1]
        data = load_data()
        if referrer_id != str(user_id):
            if str(user_id) not in data["orders"]:
                if data["users"].get(str(user_id)) and data["users"][str(user_id)]["referred_by"] is None:
                    data["users"][str(user_id)]["referred_by"] = referrer_id
                    save_data(data)

    await message.answer(
        f"Salom {full_name}! Efootball Coins botiga xush kelibsiz!\nKerakli bo'limni tanlang:",
        reply_markup=get_main_menu(user_id)
    )

# --- AXBOROT BERUVCHI TUGMALAR ---
@dp.message(F.text == "📖 Qo'llanma")
async def cmd_guide(message: types.Message):
    await message.answer(
        "📖 **Coins sotib olish qo'llanmasi:**\n\n"
        "1️⃣ Kerakli bo'limni tanlang (Android yoki Region).\n"
        "2️⃣ O'zingizga ma'qul bo'lgan Coins paketini bosing.\n"
        "3️⃣ Akkauntingiz ma'lumotlarini (Login va Parol) kiriting.\n"
        "4️⃣ Ko'rsatilgan karta raqamiga to'lov qibi, chek skrinshotini yuboring.\n"
        "5️⃣ Admin buyurtmani bajarishini kuting. Coins tushgach sizga xabar boradi!"
    )

@dp.message(F.text == "⭐ Sharhlar")
async def cmd_reviews_info(message: types.Message):
    await message.answer("⭐ Barcha muvaffaqiyatli xaridlar va mijozlarimiz sharhlari avtomatik tarzda rasmiy kanalimizga joylab boriladi!")

@dp.message(F.text == "👨‍💻 Admin / Yordam")
async def cmd_support(message: types.Message):
    await message.answer("👨‍💻 Har qanday savollar yoki muammolar bo'yicha adminga murojaat qiling: @Xusanova_M")

# --- 🛠 ADMIN PANEL TUGMASI ---
@dp.message(F.text == "🛠 Admin Panel")
async def cmd_admin_panel(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return
    data = load_data()
    total_users = len(data.get("users", {}))
    total_orders = len(data.get("orders", {}))
    turnir_count = len(data.get("tournament", []))
    
    await message.answer(
        f"🛠 **ADMIN PANEL STATISTIKASI:**\n\n"
        f"👥 Umumiy foydalanuvchilar: {total_users} ta\n"
        f"📦 Jami buyurtmalar: {total_orders} ta\n"
        f"🏆 Joriy turnirda yig'ilganlar: {turnir_count} / 64 ta"
    )

# --- 🎁 BONUSLARIM TIZIMI ---
@dp.message(F.text == "🎁 Bonuslarim")
async def cmd_bonuses(message: types.Message):
    user_id = message.from_user.id
    init_user(user_id, message.from_user.username, message.from_user.full_name)
    data = load_data()
    user_info = data["users"][str(user_id)]
    
    bot_info = await bot.get_me()
    ref_link = f"https://t.me{bot_info.username}?start={user_id}"
    
    text = (
        f"🎁 **Sizning bonus hamyoningiz:**\n\n"
        f"💰 Balans: {user_info['bonus']} Coins\n"
        f"👥 Taklif qilingan do'stlar: {user_info['referrals_count']} ta\n\n"
        f"🔗 Sizning taklif havolangiz:\n{ref_link}\n\n"
        f"ℹ️ *Har bir taklif qilgan do'stingiz botdan birinchi marta Coins sotib olganda sizga 10 Coins beriladi. "
        f"Shuningdek o'z xaridlaringizdan ham keshbek qo'shiladi (Har 100 ta coinga 1 ta bonus). Minimal yechish: 600 Coins.*"
    )
    
    builder = InlineKeyboardBuilder()
    if user_info['bonus'] >= 600:
        builder.button(text="💰 Yechib olish (600 Coins)", callback_data="withdraw_bonus")
    
    await message.answer(text, reply_markup=builder.as_markup())

@dp.callback_query(F.data == "withdraw_bonus")
async def process_withdraw(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    data = load_data()
    if data["users"][str(user_id)]["bonus"] >= 600:
        data["users"][str(user_id)]["bonus"] -= 600
        save_data(data)
        
        await bot.send_message(
            ADMIN_ID,
            f"🎁 **BONUS YECHISH SO'ROVI**\n\nMijoz: {callback.from_user.mention}\nID: {user_id}\n600 Coins bonus yechishni so'radi."
        )
        await callback.message.answer("✅ So'rov adminga yuborildi. Tez orada siz bilan bog'lanishadi.")
    else:
        await callback.answer("Mablag' yetarli emas!", show_alert=True)
    await callback.answer()

# --- ✍️ TAKLIF QOLDIRISH ---
@dp.message(F.text == "✍️ Taklif qoldirish")
async def cmd_suggestion(message: types.Message, state: FSMContext):
    await state.set_state(BotStates.writing_suggestion)
    await message.answer("Fikr, taklif yoki shikoyatingizni matn ko'rinishida yozib yuboring:")

@dp.message(BotStates.writing_suggestion, F.text)
async def process_suggestion(message: types.Message, state: FSMContext):
    await bot.send_message(
        ADMIN_ID,
        f"✍️ **YANGI TAKLIF/SHIKOYAT**\n\nKimdan: {message.from_user.mention}\nID: {message.from_user.id}\n\nMatn:\n{message.text}"
    )
    await state.clear()
    await message.answer("✅ Taklifingiz muvaffaqiyatli adminga yetkazildi. Rahmat!")

# --- 📦 MENING BUYURTMALARIM (TARIX) ---
@dp.message(F.text == "📦 Mening buyurtmalarim")
async def cmd_my_orders(message: types.Message):
    user_id = message.from_user.id
    data = load_data()
    orders = data.get("orders", {})
    
    user_orders = {k: v for k, v in orders.items() if str(v["user_id"]) == str(user_id)}
    
    if not user_orders:
        await message.answer("Sizda hali xaridlar tarixi mavjud emas.")
        return
        
    text = "📦 **Sizning xaridlar tariqingiz:**\n\n"
    for o_id, o_data in user_orders.items():
        details = o_data["details"]
        status = o_data.get("status", "Kutilmoqda ⏳")
        text += (
            f"🔹 **Buyurtma #{o_id}**\n"
            f"🛒 Turi: {details['platform']}\n"
            f"💰 Paket: {details['packet']}\n"
            f"📊 Holati: {status}\n\n"
        )
    await message.answer(text)

# --- 🏆 TURNIR BO'LIMI ---
@dp.message(F.text == "🏆 Turnir")
async def cmd_tournament(message: types.Message):
    data = load_data()
    participants = data.get("tournament", [])
    count = len(participants)
    
    text = (
        f"🏆 **Katta eFootball Turniri (Slot: {count}/64)**\n\n"
        f"📌 **Qoida:** 5700 va undan yuqori Coins sotib olgan har 64 ta mijoz o'rtasida katta turnir start oladi!\n\n"
        f"💰 **Sovrin jamg'armasi taqsimoti (3 000 000 so'm):**\n"
        f"🥇 1-o'rin: 1 000 000 so'm naqd pul\n"
        f"🥈 2-o'rin: 500 000 so'm naqd pul\n"
        f"🥉 3 va 4-o'rinlar: 250 000 so'mdan\n"
        f"🎁 Qolgan 60 ta ishtirokchiga: Keyingi xarid uchun **16 500 so'mlik kupon (skidka)**!\n\n"
    )
    
    is_in_tournament = any(p["user_id"] == message.from_user.id for p in participants)
    if is_in_tournament:
        text += "✅ Siz muvaffaqiyatli turnir ro'yxatiga kiritilgansiz!"
    else:
        
