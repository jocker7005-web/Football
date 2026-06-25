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
BOT_TOKEN = "8893476065:AAEXYibg565AuSm7MAxBWuxuAkShWJLrOVg"
ADMIN_ID = 1678146043
KARTA = "9860 3501 0897 5409 (Xusanova M)"
MAIN_CHANNEL = "@coinssharhlar"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

DATA_FILE = "/data/bot_data.json"

# --- MA'LUMOTLAR BAZASI FUNKSIYALARI ---
def load_data():
    if not os.path.exists(DATA_FILE):
        return {"last_id": 0, "orders": {}, "users": {}, "tournament": []}
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return {"last_id": 0, "orders": {}, "users": {}, "tournament": []}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

def init_user(user_id, username=None):
    data = load_data()
    if str(user_id) not in data["users"]:
        data["users"][str(user_id)] = {
            "bonus": 0,
            "referred_by": None,
            "referrals_count": 0,
            "has_purchased": False,
            "username": username or "Mijoz"
        }
        save_data(data)

def get_next_order_id():
    data = load_data()
    orders = data.get("orders", {})
    if orders:
        try:
            existing_ids = [int(x) for x in orders.keys() if x.strip().isdigit()]
            new_id = max(existing_ids) + 1 if existing_ids else len(orders) + 1
        except Exception:
            new_id = len(orders) + 1
    else:
        new_id = 1
    data["last_id"] = new_id
    save_data(data)
    return new_id

# --- FSM HOLATLARI ---
class BotStates(StatesGroup):
    choosing_android_coins = State()
    choosing_region = State()
    choosing_region_coins = State()
    entering_credentials = State()
    sending_receipt = State()
    writing_review = State()
    writing_suggestion = State()
# --- ASOSIY REPLIK MENYULAR ---
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
    init_user(user_id, username)
    
    args = message.text.split()
    if len(args) > 1:
        referrer_id = args
        data = load_data()
        if referrer_id != str(user_id):
            if data["users"].get(str(user_id)) and data["users"][str(user_id)]["referred_by"] is None:
                data["users"][str(user_id)]["referred_by"] = referrer_id
                save_data(data)

    await message.answer(
        f"Salom {message.from_user.full_name}! Efootball Coins botiga xush kelibsiz!\nKerakli bo'limni tanlang:",
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
        "4️⃣ Ko'rsatilgan karta raqamiga to'lov qilib, chek skrinshotini yuboring.\n"
        "5️⃣ Admin buyurtmani bajarishini kuting. Coins tushgach sizga xabar boradi!"
    )

@dp.message(F.text == "⭐ Sharhlar")
async def cmd_reviews_info(message: types.Message):
    await message.answer(f"⭐ Barcha muvaffaqiyatli xaridlar va mijozlarimiz sharhlari avtomatik tarzda rasmiy guruhimizga joylab boriladi: {MAIN_CHANNEL}")

@dp.message(F.text == "👨‍💻 Admin / Yordam")
async def cmd_support(message: types.Message):
    await message.answer("👨‍💻 Har qanday savollar yoki muammolar bo'yicha adminga murojaat qiling: @jocker7005")

# --- 🎁 BONUSLARIM VA REFERAL TIZIMI (50 COINS) ---
@dp.message(F.text == "🎁 Bonuslarim")
async def cmd_bonuses(message: types.Message):
    user_id = message.from_user.id
    init_user(user_id, message.from_user.username)
    data = load_data()
    user_info = data["users"][str(user_id)]
    
    bot_info = await bot.get_me()
    ref_link = f"https://t.me{bot_info.username}?start={user_id}"
    
    text = (
        f"🎁 **Sizning bonus hamyoningiz:**\n\n"
        f"💰 Balans: {user_info['bonus']} Coins\n"
        f"👥 Taklif qilingan do'stlar: {user_info['referrals_count']} ta\n\n"
        f"🔗 Sizning taklif havolangiz:\n{ref_link}\n\n"
        f"ℹ️ *Har bir taklif qilgan do'stingiz botdan birinchi marta Coins sotib olganda sizga 50 Coins beriladi. "
        f"O'z xaridlaringizdan ham keshbek qo'shiladi. Minimal yechish: 600 Coins.*"
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
            chat_id=ADMIN_ID,
            text=f"🎁 **BONUS YECHISH SO'ROVI**\n\nMijoz: {callback.from_user.full_name}\nID: {user_id}\n600 Coins bonus yechishni so'radi."
        )
        await callback.message.answer("✅ So'rov adminga yuborildi. Tez orada siz bilan bog'lanishadi.")
    else:
        await callback.answer("Mablag' yetarli emas!", show_alert=True)
    await callback.answer()

# --- 📦 MENING BUYURTMALARIM (TARIXI) ---
@dp.message(F.text == "📦 Mening buyurtmalarim")
async def cmd_my_orders(message: types.Message):
    user_id = message.from_user.id
    data = load_data()
    user_orders = {k: v for k, v in data.get("orders", {}).items() if str(v["user_id"]) == str(user_id)}
    if not user_orders:
        await message.answer("Sizda hali xaridlar tarixi mavjud emas.")
        return
    text = "📦 **Sizning xaridlar tariqingiz:**\n\n"
    for o_id, o_data in user_orders.items():
        text += f"🔹 **Buyurtma #N{o_id}**\n🛒 Paket: {o_data['details'].get('packet', 'Coins')}\n📊 Holati: {o_data.get('status', '⏳')}\n\n"
    await message.answer(text)

# --- 🏆 TURNIR BO'LIMI ---
@dp.message(F.text == "🏆 Turnir")
async def cmd_tournament(message: types.Message):
    data = load_data()
    count = len(data.get("tournament", []))
    
    tournament_text = f"""🏆 **GRAND eFOOTBALL MOBILE TURNIRI!** 🏆
    
🔥 **Siz ham haqiqiy kiberfutbol turnirida qatnashib pul mukofotini yutib olishni xohlaysizmi?**

📊 **Turnir holati:** 
🔹 Jami slot: **64 ta**
🔹 Ro'yxatdan o'tganlar: **{count} / 64** 👥

💰 **MUKOFOT JAMG'ARMASI — 3 000 000 SO'M!**
🥇 1-O'rin: **1 500 000 so'm**
🥈 2-O'rin: **1 000 000 so'm**
🥉 3-O'rin: **500 000 so'm**

📌 **Qatnashish Sharti (Mutlaqo Tekin):**
Botimiz orqali **5700 Coins** va undan yuqori paket sotib olgan har bir xaridor turnir setkasiga (slotiga) avtomatik ravishda **TEKIN** qo'shiladi!

📉 **Turnir Tizimi:**
1️⃣ Har 64 ta ishtirokchi yig'ilganda turnir setkasi (chizmasi) rasman start oladi.
2️⃣ O'yinlar **1 va 1 (Play-off)** tizimida guruh g'olibi bo'lguncha davom etadi.
3️⃣ Turnir setkalari, jonli natijalar va g'oliblar rasm-isboti bilan guruhimizga joylanadi!

🔗 **Jonli turnir setkasini ko'rish:** {MAIN_CHANNEL}
👉 *Coins sotib oling va o'z slotingizni hoziroq band qiling!*"""

    builder = InlineKeyboardBuilder()
    builder.button(text="📊 Turnir Setkasini Ko'rish", url="https://t.me")
    
    try:
        await message.answer_photo(
            photo="https://unsplash.com",
            caption=tournament_text,
            reply_markup=builder.as_markup(),
            parse_mode="Markdown"
        )
    except Exception:
        await message.answer(text=tournament_text, reply_markup=builder.as_markup(), parse_mode="Markdown")

# --- ✍️ TAKLIF QOLDIRISH ---
@dp.message(F.text == "✍️ Taklif qoldirish")
async def cmd_suggestion(message: types.Message, state: FSMContext):
    await state.clear()
    await state.set_state(BotStates.writing_suggestion)
    await message.answer("Fikr, taklif yoki shikoyatingizni matn ko'rinishida yozib yuboring:")

@dp.message(BotStates.writing_suggestion, F.text)
async def process_suggestion(message: types.Message, state: FSMContext):
    if message.text in ["🛒 Android Coins", "🌍 Regionlar uchun Coins", "🏆 Turnir", "🎁 Bonuslarim", "📖 Qo'llanma", "📦 Mening buyurtmalarim", "⭐ Sharhlar", "✍️ Taklif qoldirish", "👨‍💻 Admin / Yordam"]:
        await state.clear()
        return await dp.feed_message(bot, message)
    admin_msg = f"✍️ **YANGI TAKLIF / SHIKOYAT**\n\n👤 Kimdan: {message.from_user.full_name}\n🆔 ID: `{message.from_user.id}`\n\n📝 Matn:\n\"{message.text}\""
    try:
        await bot.send_message(chat_id=ADMIN_ID, text=admin_msg, parse_mode="Markdown")
        await message.answer("✅ Taklifingiz muvaffaqiyatli adminga yetkazildi. Rahmat!")
    except Exception:
        await message.answer("✅ Taklifingiz qabul qilindi. Rahmat!")
    await state.clear()
# --- 🛒 ANDROID COINS XARID BOSQICHI ---
@dp.message(F.text == "🛒 Android Coins")
async def cmd_android_coins(message: types.Message, state: FSMContext):
    await state.clear()
    prices = [
        "260 coins -> 40.000 so'm", "300 coins -> 45.000 so'm", "390 coins -> 60.000 so'm",
        "550 coins -> 70.000 so'm", "750 coins -> 95.000 so'm", "1040 coins -> 125.000 so'm",
        "1790 coins -> 210.000 so'm", "2130 coins -> 240.000 so'm", "2680 coins -> 310.000 so'm",
        "3250 coins -> 350.000 so'm", "4000 coins -> 440.000 so'm", "5700 coins -> 560.000 so'm",
        "7040 coins -> 730.000 so'm", "9990 coins -> 1.050.000 so'm", "12.800 coin -> 1.190.000 so'm"
    ]
    builder = InlineKeyboardBuilder()
    for p in prices:
        builder.button(text=p, callback_data=f"and_p:{p}")
    builder.adjust(1)
    await state.set_state(BotStates.choosing_android_coins)
    await message.answer("Android uchun kerakli paketni tanlang (O'yinga kirib yuklanadi):", reply_markup=builder.as_markup())

@dp.callback_query(F.data.startswith("and_p:"), BotStates.choosing_android_coins)
async def process_android_choice(callback: types.CallbackQuery, state: FSMContext):
    packet = callback.data.split(":", 1)[1]
    raw_coin = "".join(filter(str.isdigit, packet.split("->")[0]))
    coin_amount = int(raw_coin) if raw_coin else 0

    await state.update_data(platform="Android", packet=packet, region="O'yin ichidan (Android)", coin_amount=coin_amount)
    await callback.message.delete()
    await state.set_state(BotStates.entering_credentials)
    await callback.message.answer("O'yinga kirish uchun Konami ID va Parolni kiriting:\n\n*Misol:* info@gmail.com / parol123")
    await callback.answer()

# --- 🌍 REGIONLAR UCHUN COINS XARID BOSQICHI (BARCHA 13 TA DAVLAT) ---
@dp.message(F.text == "🌍 Regionlar uchun Coins")
async def cmd_region_coins(message: types.Message, state: FSMContext):
    await state.clear()
    regions = [
        "Япония 🇯🇵", "ОАЭ 🇦🇪", "Египет 🇪🇬", "Канада 🇨🇦", 
        "Мексика 🇲🇽", "США 🇺🇸", "Саудовская Аравия 🇸🇦", "Бразилия 🇧🇷", 
        "Турция 🇹🇷", "Аргентина 🇦🇷", "Индия 🇮🇳", "Индонезия 🇮🇩", "Европа 🇪🇺"
    ]
    builder = InlineKeyboardBuilder()
    for reg in regions:
        builder.button(text=reg, callback_data=f"reg_set:{reg}")
    builder.adjust(2)
    await state.set_state(BotStates.choosing_region)
    await message.answer("Iltimos, akkauntingiz ro'yxatdan o'tgan regionni tanlang:", reply_markup=builder.as_markup())

@dp.callback_query(F.data.startswith("reg_set:"), BotStates.choosing_region)
async def process_region_choice(callback: types.CallbackQuery, state: FSMContext):
    region = callback.data.split(":", 1)[1]
    await state.update_data(region=region, platform="Region")
    
    prices = [
        "578 coins -> 70.000 so'm", "788 coins -> 100.000 so'm", "1092 coins -> 135.000 so'm",
        "2237 coins -> 250.000 so'm", "2815 coins -> 315.000 so'm", "3413 coins -> 370.000 so'm",
        "4474 coins -> 500.000 so'm", "5985 coins -> 600.000 so'm", "13440 coins -> 1.250.000 so'm",
        "32200 coins -> 2.800.000 so'm"
    ]
    builder = InlineKeyboardBuilder()
    for p in prices:
        builder.button(text=p, callback_data=f"reg_p:{p}")
    builder.adjust(1)
    await state.set_state(BotStates.choosing_region_coins)
    await callback.message.edit_text(f"Tanlangan region: {region}\nCoins paketini tanlang:", reply_markup=builder.as_markup())
    await callback.answer()

@dp.callback_query(F.data.startswith("reg_p:"), BotStates.choosing_region_coins)
async def process_region_packet(callback: types.CallbackQuery, state: FSMContext):
    packet = callback.data.split(":", 1)[1]
    raw_coin = "".join(filter(str.isdigit, packet.split("->")[0]))
    coin_amount = int(raw_coin) if raw_coin else 0

    await state.update_data(packet=packet, coin_amount=coin_amount)
    await callback.message.delete()
    await state.set_state(BotStates.entering_credentials)
    await callback.message.answer("MyKonami (Region) orqali kirish uchun Email va Parolni yuboring:\n\n*Misol:* email@domain.com / parol123")
    await callback.answer()

# --- ACCOUNT MA'LUMOTLARI VA CHEK QABUL QILISH ---
@dp.message(BotStates.entering_credentials)
async def process_credentials(message: types.Message, state: FSMContext):
    await state.update_data(credentials=message.text)
    await state.set_state(BotStates.sending_receipt)
    await message.answer(
        f"To'lovni amalga oshiring:\n💳 Karta raqam: `{KARTA}`\n\n"
        f"To'lov qilgach, chek (skrinshot) rasmini shu yerga yuboring."
    )
@dp.message(BotStates.sending_receipt, F.photo)
async def process_receipt(message: types.Message, state: FSMContext):
    data = load_data()
    order_id = get_next_order_id()
    fsm_data = await state.get_data()
    
    data["orders"][str(order_id)] = {
        "user_id": message.from_user.id,
        "details": fsm_data,
        "status": "Kutilmoqda ⏳"
    }
    save_data(data)
    
    await message.answer(f"✅ Rahmat! Sizning buyurtmangiz #N{order_id} raqami bilan qabul qilindi. Admin tekshirmoqda.")
    
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ To'lovni tasdiqlash", callback_data=f"adm_pay_ok:{order_id}")
    builder.button(text="❌ Rad etish", callback_data=f"adm_rej:{order_id}")
    builder.adjust(2)
    
    platforma = fsm_data.get('platform', 'Android')
    region_nomi = fsm_data.get('region', "O'yin ichidan")
    paket_nomi = fsm_data.get('packet', 'Coins')
    login_parol = fsm_data.get('credentials', 'Kiritilmagan')
    
    mijoz_link = f"@{message.from_user.username}" if message.from_user.username else f"[{message.from_user.full_name}](tg://user?id={message.from_user.id})"
    admin_text = f"🚨 **YANGI BUYURTMA #N{order_id}**\n\n👤 Mijoz: {mijoz_link} (ID: {message.from_user.id})\n📱 Platforma: {platforma}\n🌍 Region: {region_nomi}\n📦 Paket: {paket_nomi}\n🔑 Ma'lumotlar: `{login_parol}`"

    try:
        # Xavfsizlik ta'minlandi: Maxfiy ma'lumotlar va cheklar faqat shaxsiy adminga keladi!
        await bot.send_photo(chat_id=ADMIN_ID, photo=message.photo[-1].file_id, caption=admin_text, reply_markup=builder.as_markup())
    except Exception:
        pass
    await state.clear()

# --- ADMIN PANEL PROCESS (MAXFIY INLINE TUGMALAR) ---
@dp.callback_query(F.data.startswith("adm_pay_ok:"))
async def admin_payment_ok(callback: types.CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("❌ Siz admin emassiz!", show_alert=True)
        return
    order_id = callback.data.split(":")[-1]
    
    builder = InlineKeyboardBuilder()
    builder.button(text="🎉 Buyurtma bajarildi", callback_data=f"adm_done:{order_id}")
    builder.button(text="❌ Rad etish", callback_data=f"adm_rej:{order_id}")
    builder.adjust(1)
    
    await callback.message.edit_caption(
        caption=callback.message.caption + f"\n\n💰 *To'lov tasdiqlandi. Coin tushirilgandan so'ng 'Buyurtma bajarildi' tugmasini bosing.*",
        reply_markup=builder.as_markup(),
        parse_mode="Markdown"
    )
    await callback.answer()

@dp.callback_query(F.data.startswith("adm_done:"))
async def admin_order_done(callback: types.CallbackQuery):
    if callback.from_user.id != ADMIN_ID: return
    order_id = callback.data.split(":")[-1]
    data = load_data()
    order = data["orders"].get(str(order_id))
    
    if order and order["status"] != "Bajarildi ✅":
        order["status"] = "Bajarildi ✅"
        user_id = order["user_id"]
        
        mijoz_user = f"@{callback.from_user.username}" if callback.from_user.username else callback.from_user.full_name
        if not mijoz_user or mijoz_user == ".":
            mijoz_user = f"Mijoz_{user_id}"

        details = order.get("details", {})
        coin_amount = details.get("coin_amount", 0)
        paket_nomi = details.get("packet", "Coins")
        
        if coin_amount >= 5700 or "5700" in str(paket_nomi) or "13440" in str(paket_nomi) or "32200" in str(paket_nomi):
            if "tournament" not in data:
                data["tournament"] = []
                
            if mijoz_user not in data["tournament"] and len(data["tournament"]) < 64:
                data["tournament"].append(mijoz_user)
                try:
                    yangi_count = len(data["tournament"])
                    await bot.send_message(
                        chat_id=MAIN_CHANNEL,
                        text=f"🔥 **TURNIRGA YANGI ISHTIROKCHI QO'SHILDI!**\n\n"
                             f"👤 **O'yinchi:** {mijoz_user}\n"
                             f"📊 **Turnir sloti:** `{yangi_count} / 64` o'yinchi 🏁\n\n"
                             f"👉 Siz ham 5700+ Coins sotib oling va turnir setkasidan joy oling!"
                    )
                except Exception:
                await callback.answer()

@dp.callback_query(F.data.startswith("adm_rej:"))
async def admin_order_reject(callback: types.CallbackQuery):
    if callback.from_user.id != ADMIN_ID: return
    order_id = callback.data.split(":")[-1]
    data = load_data()
    order = data["orders"].get(str(order_id))
    
    if order:
        order["status"] = "Rad etildi ❌"
        save_data(data)
        
        # Mijoz adminga 1 soniyada yozishi uchun maxsus inline tugma yaratamiz
        builder = InlineKeyboardBuilder()
        builder.button(text="👨‍💻 Admin bilan bog'lanish", url="https://t.me")
        
        await bot.send_message(
            chat_id=order["user_id"], 
            text=f"❌ Kechirasiz, sizning #N{order_id} raqamli buyurtmangiz admin tomonidan **RAD ETILDI**.\n\n"
                 f"ℹ️ Muammoni hal qilish yoki batafsil ma'lumot olish uchun quyidagi tugma orqali admin bilan bog'laning 👇",
            reply_markup=builder.as_markup()
        )
       try:
           await callback.message.edit_caption(caption=callback.message.caption + f"\n\n🔴 STATUS: RAD ETILDI")
       except Exception:
           await callback.message.reply(text=f"🔴 STATUS: #N{order_id} RAD ETILDI")
            
       await callback.answer()

# --- SHARH (OTZIV) JRAYONI ---
@dp.callback_query(F.data.startswith("write_review:"))
async def start_review(callback: types.CallbackQuery, state: FSMContext):
    order_id = callback.data.split(":")[-1]
    await state.set_state(BotStates.writing_review)
    await state.update_data(order_id=order_id)
    await callback.message.answer("Xizmatimiz haqidagi fikringizni (sharhingizni) yozib yuboring:")
    await callback.answer()

@dp.message(BotStates.writing_review, F.text)
async def process_review(message: types.Message, state: FSMContext):
    if message.text in ["🛒 Android Coins", "🌍 Regionlar uchun Coins", "🏆 Turnir", "🎁 Bonuslarim", "📖 Qo'llanma", "📦 Mening buyurtmalarim", "⭐ Sharhlar", "✍️ Taklif qoldirish", "👨‍💻 Admin / Yordam"]:
        await state.clear()
        return await dp.feed_message(bot, message)
    fsm_data = await state.get_data()
    order_id = fsm_data.get("order_id")
    
    data = load_data()
    order = data["orders"].get(str(order_id))
    
    mijoz_user = f"@{message.from_user.username}" if message.from_user.username else message.from_user.full_name
    if not mijoz_user or mijoz_user == ".":
        mijoz_user = f"Mijoz ({message.from_user.id})"

    if order:
        order["review"] = message.text
        save_data(data)
        details = order.get("details", {})
        platforma = details.get('platform', 'Android')
        region_nomi = details.get('region', "O'yin ichidan")
        paket_nomi = details.get('packet', 'Coins')
    else:
        platforma, region_nomi, paket_nomi = "Android", "O'yin ichidan (Android)", "Coins"

    bot_info = await bot.get_me()
    channel_msg = f"🎉 **XARID VA SHARH MUVAFFAQIYATLI YAKUNLANDI!**\n\n📦 **Buyurtma raqami:** #N{order_id}\n👤 **Mijoz:** {mijoz_user}\n📱 **Platforma:** {platforma}\n🌍 **Region:** {region_nomi}\n💰 **Sotib olingan paket:** {paket_nomi}\n\n💬 **Mijoz qoldirgan sharh (Otziv):**\n\"{message.text}\"\n\n🤖 @{bot_info.username}"
    
    try:
        # parse_mode o'chirildi, shunda xabarlar xatosiz va tezkor yetib boradi
        await bot.send_message(chat_id="@coinssharhlar", text=channel_msg)
        await message.answer("✅ Rahmat! Sharhingiz guruhga joylashtirildi. 🤝")

    except Exception:
        await message.answer("Sharh uchun rahmat!")
    await state.clear()

@dp.message(F.text == "🛠 Admin Panel")
async def cmd_admin_panel(message: types.Message):
    if message.from_user.id == ADMIN_ID:
        data = load_data()
        await message.answer(f"🛠 **Admin Panel**\n\n👥 Foydalanuvchilar: {len(data.get('users', {}))}\n📦 Buyurtmalar: {len(data.get('orders', {}))}")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
