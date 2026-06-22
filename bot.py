import os
import sqlite3
import random
import asyncio
import logging
from aiogram import Bot, Dispatcher, Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command, StateFilter, CommandStart

# Logging (Serverda xatoliklarni kuzatish uchun)
logging.basicConfig(level=logging.INFO)

# --- ASOSIY SOZLAMALAR ---
BOT_TOKEN = "8893476065:AAFseE8gnPCvfV_GALln-PCvK-tz7Wihn40" ✅ Token joylandi!
ADMIN_ID = 1678146043          # ✅ Sizning Telegram ID raqamingiz
OTZIV_KANAL_ID = "@coinsotziv" # ✅ Otziv kanali

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
router = Router()

# Ma'lumotlar o'chib ketmasligi uchun Amvera /data doimiy xotirasiga o'tkazildi
DB_PATH = "/data/efootball_master.db"

# --- COINS PAKETLARI (ANDROID NARXLARI) ---
COINS_PACKAGES = {
    "pkg_260": {"coins": "🪙 260 coins", "price": "40.000 so'm"},
    "pkg_300": {"coins": "🪙 300 coins", "price": "45.000 so'm"},
    "pkg_390": {"coins": "🪙 390 coins", "price": "60.000 so'm"},
    "pkg_550": {"coins": "⚡️ 550 coins", "price": "70.000 so'm"},
    "pkg_750": {"coins": "🪙 750 coins", "price": "95.000 so'm"},
    "pkg_1040": {"coins": "💎 1040 coins", "price": "125.000 so'm"},
    "pkg_1790": {"coins": "🪙 1790 coins", "price": "210.000 so'm"},
    "pkg_2130": {"coins": "⚡️ 2130 coins", "price": "240.000 so'm"},
    "pkg_2680": {"coins": "🪙 2680 coins", "price": "310.000 so'm"},
    "pkg_3250": {"coins": "🪙 3250 coins", "price": "350.000 so'm"},
    "pkg_4000": {"coins": "💎 4000 coins", "price": "440.000 so'm"},
    "pkg_5700": {"coins": "🪙 5700 coins", "price": "560.000 so'm"},
    "pkg_7040": {"coins": "🪙 7040 coins", "price": "730.000 so'm"},
    "pkg_9990": {"coins": "🔥 9990 coins", "price": "1.050.000 so'm"},
    "pkg_12800": {"coins": "👑 12.800 coin", "price": "1.190.000 so'm"}
}

class OrderState(StatesGroup):
    choosing_package = State()
    sending_receipt = State()
    entering_login = State()
    entering_password = State()

class ReviewState(StatesGroup):
    entering_review_photo = State()
    entering_review_text = State()

class AdminStates(StatesGroup):
    waiting_for_broadcast = State()

# ============================================================
# MA'LUMOTLAR BAZASI TIZIMI (SQLITE)
# ============================================================
def init_all_dbs():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, username TEXT)")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            order_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            package TEXT,
            price TEXT,
            konami_login TEXT,
            konami_password TEXT,
            receipt_file_id TEXT,
            status TEXT DEFAULT 'Kutilmoqda'
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS leaderboard (
            user_id INTEGER PRIMARY KEY, username TEXT, played INTEGER DEFAULT 0,
            wins INTEGER DEFAULT 0, draws INTEGER DEFAULT 0, losses INTEGER DEFAULT 0, points INTEGER DEFAULT 0
        )
    """)
    cursor.execute("CREATE TABLE IF NOT EXISTS tournament_participants (user_id INTEGER PRIMARY KEY, username TEXT)")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS matches (
            match_id INTEGER PRIMARY KEY AUTOINCREMENT, player1_id INTEGER, player1_name TEXT,
            player2_id INTEGER, player2_name TEXT, score TEXT DEFAULT 'VS', status TEXT DEFAULT 'Kutilmoqda'
        )
    """)
    conn.commit()
    conn.close()

def add_user(user_id, username):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO users (user_id, username) VALUES (?, ?)", (user_id, username))
    conn.commit()
    conn.close()

def get_all_users():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM users")
    users = [row[0] for row in cursor.fetchall()]
    conn.close()
    return users

def create_order(user_id, package, price, login, password, receipt_file_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO orders (user_id, package, price, konami_login, konami_password, receipt_file_id) VALUES (?, ?, ?, ?, ?, ?)",
        (user_id, package, price, login, password, receipt_file_id)
    )
    order_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return order_id

def get_stats_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM users")
    total_users = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM orders")
    total_orders = cursor.fetchone()[0]
    conn.close()
    return total_users, total_orders

def register_for_tournament(user_id, username):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO tournament_participants (user_id, username) VALUES (?, ?)", (user_id, username))
        conn.commit()
        success = True
    except sqlite3.IntegrityError:
        success = False
    conn.close()
    return success

def get_participants():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT user_id, username FROM tournament_participants")
    rows = cursor.fetchall()
    conn.close()
    return rows

def save_matches(matches_list):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM matches")
    cursor.executemany("INSERT INTO matches (player1_id, player1_name, player2_id, player2_name) VALUES (?, ?, ?, ?)", matches_list)
    conn.commit()
    conn.close()

def get_current_matches():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT match_id, player1_name, player2_name, score, status FROM matches")
    rows = cursor.fetchall()
    conn.close()
    return rows

def get_leaderboard():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT username, played, wins, draws, losses, points FROM leaderboard ORDER BY points DESC, wins DESC")
    rows = cursor.fetchall()
    conn.close()
    return rows

def update_player_score(user_id, username, result):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO leaderboard (user_id, username) VALUES (?, ?)", (user_id, username))
    if result == "win":
        cursor.execute("UPDATE leaderboard SET played=played+1, wins=wins+1, points=points+3 WHERE user_id=?", (user_id,))
    elif result == "draw":
        cursor.execute("UPDATE leaderboard SET played=played+1, draws=draws+1, points=points+1 WHERE user_id=?", (user_id,))
    elif result == "loss":
        cursor.execute("UPDATE leaderboard SET played=played+1, losses=losses+1 WHERE user_id=?", (user_id,))
    conn.commit()
    conn.close()

def reset_tournament():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tournament_participants")
    cursor.execute("DELETE FROM matches")
    cursor.execute("DELETE FROM leaderboard")
    conn.commit()
    conn.close()

# ============================================================
# TRAFIK VA KLAVIATURALAR (UI)
# ============================================================
def main_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🛒 Coins Sotib Olish (Android)", callback_data="buy_coins")],
        [InlineKeyboardButton(text="📝 Turnirga Ro'yxatdan O'tish", callback_data="reg_tournament")],
        [InlineKeyboardButton(text="📊 O'yinlar Setkasi", callback_data="view_setka"),
         InlineKeyboardButton(text="🏆 Reyting Jadvali", callback_data="view_rating")],
        [InlineKeyboardButton(text="📢 Otziv Kanalimiz", url="https://t.me/coinsotziv")]
    ])

def coins_menu():
    kb = []
    for key, val in COINS_PACKAGES.items():
        kb.append([InlineKeyboardButton(text=f"{val['coins']} — {val['price']}", callback_data=key)])
    kb.append([InlineKeyboardButton(text="⬅️ Ortga", callback_data="back_main")])
    return InlineKeyboardMarkup(inline_keyboard=kb)

# ============================================================
# FOYDALANUVCHI HANDLERLARI
# ============================================================
@router.message(CommandStart())
async def cmd_start(message: Message):
    add_user(message.from_user.id, message.from_user.username)
    await message.answer(
        f"⚽️ Salom, {message.from_user.full_name}!\neFootball Coins sotuvchi va Onlayn Turnirlar botiga xush kelibsiz!",
        reply_markup=main_menu()
    )

@router.callback_query(F.data == "back_main")
async def back_to_main(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("Asosiy menyu:", reply_markup=main_menu())
    await callback.answer()

@router.callback_query(F.data == "buy_coins")
async def process_buy(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text("🤖 Kerakli Android Coins paketini tanlang:", reply_markup=coins_menu())
    await state.set_state(OrderState.choosing_package)
    await callback.answer()

@router.callback_query(StateFilter(OrderState.choosing_package), F.data.startswith("pkg_"))
async def process_package(callback: CallbackQuery, state: FSMContext):
    pkg_id = callback.data
    package_info = COINS_PACKAGES[pkg_id]
    await state.update_data(chosen_pkg=package_info['coins'], chosen_price=package_info['price'])
    await callback.message.answer(
        f"🛒 Siz tanladingiz: *{package_info['coins']}*\n"
        f"💰 To'lov miqdori: *{package_info['price']}*\n\n"
        f"💳 Karta raqami: `9860 3501 0897 5409`\n"
        f"👤 Karta egasi: *Xusanova Maqsuda*\n\n"
        f"📥 Pulni o'tkazib bo'lgach, **to'lov chekini (skrinshotini) rasm ko'rinishida** shu yerga yuboring:",
        parse_mode="Markdown"
    )
    await state.set_state(OrderState.sending_receipt)
    await callback.answer()

@router.message(StateFilter(OrderState.sending_receipt), F.photo)
async def process_receipt(message: Message, state: FSMContext):
    file_id = message.photo[-1].file_id
    await state.update_data(receipt_file_id=file_id)
    await message.answer("✅ Chek rasmi qabul qilindi!\n\n🔑 Endi Android akkauntingizga kirish uchun **MyKonami Login (Email)** manzilini yozing:")
    await state.set_state(OrderState.entering_login)

@router.message(StateFilter(OrderState.entering_login), F.text)
async def process_login(message: Message, state: FSMContext):
    await state.update_data(konami_login=message.text)
    await message.answer("🔒 Endi MyKonami **Parolini** yozing:")
    await state.set_state(OrderState.entering_password)

@router.message(StateFilter(OrderState.entering_password), F.text)
async def process_password(message: Message, state: FSMContext):
    user_data = await state.get_data()
    password = message.text
    login = user_data['konami_login']
    package = user_data['chosen_pkg']
    price = user_data['chosen_price']
    receipt_file_id = user_data['receipt_file_id']
    
    order_id = create_order(message.from_user.id, package, price, login, password, receipt_file_id)
    await message.answer(f"✅ Rahmat! Buyurtmangiz **#{order_id}** raqami bilan qabul qilindi. Admin tekshirib, coinslarni yuklagach sizga xabar boradi!")
    await state.clear()
    
    admin_text = (
        f"🚨 **YANGI BUYURTMA #{order_id}** 🚨\n\n"
        f"👤 **Mijoz:** @{message.from_user.username} (ID: {message.from_user.id})\n"
        f"📦 **Paket:** {package}\n"
        f"💰 **Narxi:** {price}\n\n"
        f"🔑 **Konami Login:** `{login}`\n"
        f"🔒 **Konami Parol:** `{password}`\n\n"
        f"📱 *Android tizimi orqali akkauntga kirib yuklanadi!*"
    )
    admin_kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Bajarildi", callback_data=f"done_{order_id}_{message.from_user.id}")]
    ])
    await bot.send_photo(chat_id=ADMIN_ID, photo=receipt_file_id, caption=admin_text, reply_markup=admin_kb, parse_mode="Markdown")

# ============================================================
# ADMIN TASDIQLASHI VA RASMLI OTZIV TIZIMI
# ============================================================
@router.callback_query(F.data.startswith("done_"))
async def admin_complete_order(callback: CallbackQuery):
    _, order_id, user_id = callback.data.split("_")
    otziv_kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✍️ Otziv (Fikr) Qoldirish", callback_data=f"write_review_{order_id}")]
    ])
    try:
        await bot.send_message(
            chat_id=int(user_id), 
            text=f"🎉 Xushxabar! **#{order_id}** raqamli buyurtmangiz muvaffaqiyatli bajarildi va coinslar yuklandi! ✅\n\n"
                 f"Iltimos, pastdagi tugmani bosib, coins tushgan o'yin ichidagi skrinshot (rasm) va fikringizni qoldiring 👇",
            reply_markup=otziv_kb
        )
        await callback.message.edit_caption(caption=callback.message.caption + "\n\n🟢 **STATUS: BAJARILDI**")
    except Exception as e:
        await callback.message.answer(f"Xatolik: {e}")
    await callback.answer()

@router.callback_query(F.data.startswith("write_review_"))
async def start_review(callback: CallbackQuery, state: FSMContext):
    order_id = callback.data.split("_")[2]
    await state.update_data(review_order_id=order_id)
    await callback.message.answer("🤖 Coins tushganini tasdiqlovchi o'yin ichidagi skrinshotni (rasm) yuboring:")
    await state.set_state(ReviewState.entering_review_photo)
    await callback.answer()

@router.message(StateFilter(ReviewState.entering_review_photo), F.photo)
async def process_review_photo(message: Message, state: FSMContext):
    photo_id = message.photo[-1].file_id
    await state.update_data(review_photo_id=photo_id)
    await message.answer("✍️ Endi jamoamiz haqidagi fikringizni matn ko'rinishida yozib yuboring:")
    await state.set_state(ReviewState.entering_review_text)

@router.message(StateFilter(ReviewState.entering_review_text), F.text)
async def process_review_text(message: Message, state: FSMContext):
    user_data = await state.get_data()
    order_id = user_data['review_order_id']
    photo_id = user_data['review_photo_id']
    review_text = message.text
    username = f"@{message.from_user.username}" if message.from_user.username else "Foydalanuvchi"

    kanal_matni = (
        f"⭐️ **YANGI OTZIV #{order_id}** ⭐️\n\n"
        f"👤 **Mijoz:** {username}\n"
        f"💬 **Fikr:** {review_text}\n\n"
        f"🤝 Xaridingiz uchun rahmat!\n"
        f"🤖 @coinsotziv hamjamiyati"
    )
    try:
        await bot.send_photo(chat_id=OTZIV_KANAL_ID, photo=photo_id, caption=kanal_matni)
        await message.answer("❤️ Katta rahmat! Otzivingiz rasmi va matni bilan birga ochiq @coinsotziv kanalimizga joylandi.")
    except Exception as e:
        await message.answer("⚠️ Otziv kanalga chiqmadi. Bot kanalingizda admin ekanligini tekshiring.")
    await state.clear()

# ============================================================
# TURNIR HANDLING QISMI
# ============================================================
@router.callback_query(F.data == "reg_tournament")
async def register_player(callback: CallbackQuery):
    username = callback.from_user.username if callback.from_user.username else f"id_{callback.from_user.id}"
    success = register_for_tournament(callback.from_user.id, username)
    if success:
        await callback.message.answer("✅ Siz turnir ro'yxatiga muvaffaqiyatli qo'shildingiz!")
    else:
        await callback.message.answer("⚠️ Siz allaqachon turnir ro'yxatida borsiz.")
    await callback.answer()

@router.callback_query(F.data == "view_setka")
async def show_setka(callback: CallbackQuery):
    matches = get_current_matches()
    if not matches:
        await callback.message.answer("📊 Hozircha turnir setkasi bo'sh. Admin qur'a tashlashini kuting.")
        await callback.answer()
        return
    text = "📊 **JORIY TURNIR SETKASI (JUFTLIKLAR)** 📊\n\n"
    for match in matches:
        match_id, p1, p2, score, status = match
        status_emoji = "⏳" if status == "Kutilmoqda" else "✅"
        text += f"🔹 O'yin #{match_id}: @{p1}  {score}  @{p2}  [{status_emoji} {status}]\n"
    await callback.message.answer(text)
    await callback.answer()

@router.callback_query(F.data == "view_rating")
async def show_rating(callback: CallbackQuery):
    players = get_leaderboard()
    if not players:
        await callback.message.answer("🏆 Reyting jadvali hozircha bo'sh.")
        await callback.answer()
        return
    text = "🏆 **EFOOTBALL REYTING JADVALI** 🏆\n\n⏱ O' | G' | D | M | **OCHKO** | O'yinchi\n----------------------------------------\n"
    for index, player in enumerate(players, start=1):
        username, played, wins, draws, losses, points = player
        medal = "🥇" if index == 1 else "🥈" if index == 2 else "🥉" if index == 3 else f"{index}."
        text += f"{medal} {played} | {wins} | {draws} | {losses} | **{points}** | @{username}\n"
    await callback.message.answer(text, parse_mode="Markdown")
    await callback.answer()

# ============================================================
# FAQAT ADMIN UCHUN BUYRUQLAR
# ============================================================
@router.message(Command("stats"), F.from_user.id == ADMIN_ID)
async def admin_stats(message: Message):
    total_users, total_orders = get_stats_db()
    await message.answer(f"📊 **BOT STATISTIKASI:**\n\n👥 Jami a'zolar: {total_users} ta\n📦 Jami tushgan buyurtmalar: {total_orders} ta")

@router.message(Command("broadcast"), F.from_user.id == ADMIN_ID)
async def start_broadcast(message: Message, state: FSMContext):
    await message.answer("📣 Barcha foydalanuvchilarga yuboriladigan xabarni kiriting:")
    await state.set_state(AdminStates.waiting_for_broadcast)

@router.message(AdminStates.waiting_for_broadcast, F.from_user.id == ADMIN_ID)
async def do_broadcast(message: Message, state: FSMContext):
    users = get_all_users()
    success = 0
    for user_id in users:
        try:
            await message.copy_to(chat_id=user_id)
            success += 1
            await asyncio.sleep(0.05)
        except:
            pass
    await message.answer(f"✅ Rassilka yakunlandi!\n🎯 Yuborildi: {success}/{len(users)}")
    await state.clear()

@router.message(Command("start_qura"), F.from_user.id == ADMIN_ID)
async def admin_start_qura(message: Message):
    players = get_participants()
    if len(players) < 2:
        await message.answer("❌ Kamida 2 ta ishtirokchi ro'yxatdan o'tgan bo'lishi kerak!")
        return
    random.shuffle(players)
    matches_to_save = []
    text = "🎲 **AVTOMATIK QUR'A NATIJALARI (SETKA):**\n\n"
    for i in range(0, len(players), 2):
        if i + 1 < len(players):
            matches_to_save.append((players[i][0], players[i][1], players[i+1][0], players[i+1][1]))
            text += f"🎮 @{players[i][1]}  VS  @{players[i+1][1]}\n"
        else:
            matches_to_save.append((players[i][0], players[i][1], 0, "RAQIBSIZ"))
            text += f"🎮 @{players[i][1]}  VS  ❌ RAQIBSIZ (Avto-o'tish)\n"
    save_matches(matches_to_save)
    await message.answer(text + "\n🟢 Turnir setkasi muvaffaqiyatli saqlandi va e'lon qilindi!")

@router.message(Command("score"), F.from_user.id == ADMIN_ID)
async def admin_change_score(message: Message):
    try:
        args = message.text.split()
        user_id, result = int(args[1]), args[2].lower()
        user_chat = await bot.get_chat(user_id)
        update_player_score(user_id, user_chat.username, result)
        await message.answer(f"✅ @{user_chat.username} uchun ochko yangilandi: {result.upper()}")
    except:
        await message.answer("❌ Xato format. To'g'ri format: `/score [us
