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
    current_id = data.get("last_id", 0)
    
    if current_id == 0 and data.get("orders"):
        try:
            current_id = max(int(k) for k in data["orders"].keys())
        except Exception:
            current_id = 0
            
    new_id = int(current_id) + 1
    data["last_id"] = new_id
    save_data(data)
    return int(new_id)

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
    builder.row(types.KeyboardButton(text="🎯 Kunlik Viktorina"))
    if user_id == ADMIN_ID:
        builder.row(types.KeyboardButton(text="🛠 Admin Panel"))
    return builder.as_markup(resize_keyboard=True)

# --- START KOMANDASI ---
@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    user_id = message.from_user.id
    username = message.from_user.username
    init_user(user_id, username)
    
    args = message.text.split()
    if len(args) > 1:
        referrer_id = args[0]
        data = load_data()
        if str(referrer_id) != str(user_id):
            if data["users"].get(str(user_id)) and data["users"][str(user_id)]["referred_by"] is None:
                data["users"][str(user_id)]["referred_by"] = referrer_id
                save_data(data)

    await message.answer(
        f"Salom {message.from_user.full_name}! Efootball Coins botiga xush kelibsiz!\nKerakli bo'limni tanlang:",
        reply_markup=get_main_menu(user_id)
            )
# --- AXBOROT TUGMALARI ---
@dp.message(F.text == "📖 Qo'llanma")
async def cmd_guide(message: types.Message):
    await message.answer(
        "📖 <b>Coins sotib olish qo'llanmasi:</b>\n\n"
        "1️⃣ Kerakli bo'limni tanlang (Android yoki Region).\n"
        "2️⃣ O'zingizga ma'qul bo'lgan Coins paketini bosing.\n"
        "3️⃣ Akkauntingiz ma'lumotlarini (Login va Parol) kiriting.\n"
        "4️⃣ Ko'rsatilgan karta raqamiga to'lov qibly, chek skrinshotini yuboring.\n"
        "5️⃣ Admin buyurtmani bajiishini kuting. Coins tushgach sizga xabar boradi!",
        parse_mode="HTML"
    )

@dp.message(F.text == "⭐ Sharhlar")
async def cmd_reviews_info(message: types.Message):
    await message.answer(f"⭐ Barcha muvaffaqiyatli xaridlar va mijozlarimiz sharhlari avtomatik tarzda rasmiy guruhimizga joylab boriladi: {MAIN_CHANNEL}")

@dp.message(F.text == "👨‍💻 Admin / Yordam")
async def cmd_support(message: types.Message):
    await message.answer("👨‍💻 Har qanday savollar yoki muammolar bo'yicha adminga murojaat qiling: @jocker7005")

@dp.message(F.text == "🎁 Bonuslarim")
async def cmd_bonuses(message: types.Message):
    user_id = message.from_user.id
    init_user(user_id, message.from_user.username)
    data = load_data()
    user_info = data["users"][str(user_id)]
    
    bot_info = await bot.get_me()
    ref_link = f"https://t.me/{bot_info.username}?start={user_id}"
    
    text = (
        f"🎁 <b>Sizning bonus hamyoningiz:</b>\n\n"
        f"💰 Balans: {user_info['bonus']} Coins\n"
        f"👥 Taklif qilingan do'stlar: {user_info['referrals_count']} ta\n\n"
        f"🔗 Sizning taklif havolangiz:\n{ref_link}\n\n"
        f"ℹ️ <i>Har bir taklif qilgan do'st xaridi uchun 50 Coins. Minimal yechish: 600 Coins.</i>"
    )
    builder = InlineKeyboardBuilder()
    if user_info['bonus'] >= 600:
        builder.button(text="💰 Yechib olish (600 Coins)", callback_data="withdraw_bonus")
    await message.answer(text, reply_markup=builder.as_markup(), parse_mode="HTML")

@dp.callback_query(F.data == "withdraw_bonus")
async def process_withdraw(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    data = load_data()
    if data["users"][str(user_id)]["bonus"] >= 600:
        data["users"][str(user_id)]["bonus"] -= 600
        save_data(data)
        await bot.send_message(chat_id=ADMIN_ID, text=f"🎁 <b>BONUS YECHISH</b>\nMijoz: {callback.from_user.full_name}\nID: {user_id}", parse_mode="HTML")
        await callback.message.answer("✅ So'rov adminga yuborildi.")
    else:
        await callback.answer("Mablag' yetarli emas!", show_alert=True)
    await callback.answer()

@dp.message(F.text == "📦 Mening buyurtmalarim")
async def cmd_my_orders(message: types.Message):
    user_id = message.from_user.id
    data = load_data()
    user_orders = {k: v for k, v in data.get("orders", {}).items() if str(v["user_id"]) == str(user_id)}
    if not user_orders:
        await message.answer("Sizda hali xaridlar tarixi mavjud emas.")
        return
    text = "📦 <b>Sizning xaridlar tariqingiz:</b>\n\n"
    for o_id, o_data in user_orders.items():
        text += f"🔹 <b>Buyurtma #N{o_id}</b>\n🛒 Paket: {o_data['details'].get('packet', 'Coins')}\n📊 Holati: {o_data.get('status', '⏳')}\n\n"
    await message.answer(text, parse_mode="HTML")

# --- 🏆 TURNIR BO'LIMI ---
@dp.message(F.text == "🏆 Turnir")
async def cmd_tournament(message: types.Message):
    data = load_data()
    count = len(data.get("tournament", []))
    tournament_text = f"🏆 <b>GRAND eFOOTBALL MOBILE TURNIRI!</b> 🏆\n\n" \
                      f"🔥 <b>Siz ham kiberfutbol turnirida qatnashib pul mukofotini yutishni xohlaysizmi?</b>\n\n" \
                      f"📊 <b>Turnir holati:</b>\n" \
                      f"🔹 Jami slot: <b>64 ta</b>\n" \
                      f"🔹 Ro'yxatdan o'tganlar: <b>{count} / 64</b> 👥\n\n" \
                      f"💰 <b>MUKOFOT JAMG'ARMASI — 3 000 000 SO'M!</b>\n" \
                      f"🥇 1-O'rin: <b>1 500 000 so'm</b>\n" \
                      f"🥈 2-O'rin: <b>1 000 000 so'm</b>\n" \
                      f"🥉 3-O'rin: <b>500 000 so'm</b>\n\n" \
                      f"📌 <b>Qatnashish Sharti (Mutlaqo Tekin):</b>\n" \
                      f"Botimiz orqali <b>5700 Coins</b> va undan yuqori paket sotib olgan har bir xaridor turnir setkasiga avtomatik razvda <b>TEKIN</b> qo'shiladi!\n\n" \
                      f"🔗 <b>Jonli turnir setkasini ko'rish:</b> {MAIN_CHANNEL}"
    builder = InlineKeyboardBuilder()
    builder.button(text="📊 Turnir Setkasini Ko'rish", url="https://t.me/levelGroup_eFHub")
    try:
        await message.answer_photo(
            photo="https://unsplash.com",
            caption=tournament_text,
            reply_markup=builder.as_markup(),
            parse_mode="HTML"
        )
    except Exception:
        await message.answer(text=tournament_text, reply_markup=builder.as_markup(), parse_mode="HTML")

# --- 🎯 KUNLIK FUTBOL VIKTORINASI ---
@dp.message(F.text == "🎯 Kunlik Viktorina")
async def cmd_quiz(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "🚀 <b>KATTA BONUS TIZIMI — TEZ KUNDA!</b>\n\n"
        "⏳ Hozirda ushbu boʻlimda yangi aksiya va texnik sozlash ishlari ketmoqda.\n"
        "Yaqin kunlarda yirik Coins sovgʻalari va mutlaqo yangi bonuslar bilan ushbu boʻlim toʻliq ishga tushadi! 🔥\n\n"
        "🔔 Yangiliklarni oʻtkazib yubormaslik uchun rasmiy kanalimizni kuzatib boring: https://t.me/levelGroup_eFHub",
        parse_mode="HTML"
    )
# --- ✍️ TAKLIF QOLDIRISH ---
@dp.message(F.text == "✍️ Taklif qoldirish")
async def cmd_suggestion(message: types.Message, state: FSMContext):
    await state.clear()
    await state.set_state(BotStates.writing_suggestion)
    await message.answer("Taklif yoki shikoyatingizni yozib yuboring:")

@dp.message(BotStates.writing_suggestion, F.text)
async def process_suggestion(message: types.Message, state: FSMContext):
    if message.text in ["🛒 Android Coins", "🌍 Regionlar uchun Coins", "🏆 Turnir", "🎁 Bonuslarim", "📖 Qo'llanma", "📦 Mening buyurtmalarim", "⭐ Sharhlar", "✍️ Taklif qoldirish", "👨‍💻 Admin / Yordam", "🎯 Kunlik Viktorina"]:
        await state.clear()
        return await dp.feed_message(bot, message)
    admin_msg = f"✍️ <b>YANGI TAKLIF</b>\n\nKimdan: {message.from_user.full_name}\nID: <code>{message.from_user.id}</code>\n\n\"{message.text}\""
    try:
        await bot.send_message(chat_id=ADMIN_ID, text=admin_msg, parse_mode="HTML")
        await message.answer("✅ Taklifingiz adminga yetkazildi!")
    except Exception:
        await message.answer("✅ Qabul qilindi!")
    await state.clear()

# --- XARID BOSQICHLARI ---
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
    await message.answer("Android paketini tanlang:", reply_markup=builder.as_markup())

@dp.callback_query(F.data.startswith("and_p:"), BotStates.choosing_android_coins)
async def process_android_choice(callback: types.CallbackQuery, state: FSMContext):
    packet = callback.data.split(":", 1)[-1]
    raw_coin = "".join(filter(str.isdigit, packet.split("->")[0]))
    coin_amount = int(raw_coin) if raw_coin else 0
    await state.update_data(platform="Android", packet=packet, region="O'yin ichidan (Android)", coin_amount=coin_amount)
    await callback.message.delete()
    await state.set_state(BotStates.entering_credentials)
    await callback.message.answer("Konami ID va Parolni yuboring (Misol: email / parol):")
    await callback.answer()

@dp.message(F.text == "🌍 Regionlar uchun Coins")
async def cmd_region_coins(message: types.Message, state: FSMContext):
    await state.clear()
    regions = [
    "Япония 🇯🇵",
    "ОАЭ 🇦🇪",
    "Египет 🇪🇬",
    "Канада 🇨🇦",
    "Мексика 🇲🇽",
    "США 🇺🇸",
    "Турция 🇹🇷",
    "Саудовская Аравия 🇸🇦",
    "Австралия 🇦🇺",
    "Швеция 🇸🇪",
    "Швейцария 🇨🇭",
    "Великобритания 🇬🇧",
    "Индонезия 🇮🇩",
    "Малайзия 🇲🇾"
    ]
    builder = InlineKeyboardBuilder()
    for reg in regions:
        builder.button(text=reg, callback_data=f"reg_set:{reg}")
    builder.adjust(2)
    await state.set_state(BotStates.choosing_region)
    await message.answer("Akkauntingiz regionini tanlang:", reply_markup=builder.as_markup())

@dp.callback_query(F.data.startswith("reg_set:"), BotStates.choosing_region)
async def process_region_choice(callback: types.CallbackQuery, state: FSMContext):
    region = callback.data.split(":", 1)[-1]
    await state.update_data(region=region, platform="Region")
    if "Япония" in region:
        prices = [
            "578 coins -> 70.000 so'm",
            "788 coins -> 100.000 so'm",
            "1092 coins -> 135.000 so'm",
            "2237 coins -> 250.000 so'm",
            "2815 coins -> 315.000 so'm",
            "3413 coins -> 370.000 so'm",
            "4474 coins -> 500.000 so'm",
            "5985 coins -> 600.000 so'm",
            "13440 coins -> 1.250.000 so'm",
            "32200 coins -> 2.800.000 so'm",
            "🔥 [AKSIYA] 650 coins (1 marta) -> 50.000 so'm",
            "🔥 [AKSIYA] 2600 coins (4 marta limit) -> 190.000 so'm"
        ]
    else:
        prices = [
            "578 coins -> 70.000 so'm",
            "788 coins -> 100.000 so'm",
            "1092 coins -> 135.000 so'm",
            "2237 coins -> 250.000 so'm",
            "2815 coins -> 315.000 so'm",
            "3413 coins -> 370.000 so'm",
            "4474 coins -> 500.000 so'm",
            "5985 coins -> 600.000 so'm",
            "13440 coins -> 1.250.000 so'm",
            "32200 coins -> 2.800.000 so'm"
        ]

    builder = InlineKeyboardBuilder()
    for p in prices:
        builder.button(text=p, callback_data=f"reg_p:{p}")
    builder.adjust(1)
    await state.set_state(BotStates.choosing_region_coins)
    await callback.message.edit_text(f"Region: {region}\nPaketni tanlang:", reply_markup=builder.as_markup())
    await callback.answer()

@dp.callback_query(F.data.startswith("reg_p:"), BotStates.choosing_region_coins)
async def process_region_packet(callback: types.CallbackQuery, state: FSMContext):
    packet = callback.data.split(":", 1)[-1]
    raw_coin = "".join(filter(str.isdigit, packet.split("->")[0]))
    coin_amount = int(raw_coin) if raw_coin else 0
    await state.update_data(packet=packet, coin_amount=coin_amount)
    await callback.message.delete()
    await state.set_state(BotStates.entering_credentials)
    await callback.message.answer("Email va Parolni kiriting:")
    await callback.answer()

@dp.message(BotStates.entering_credentials)
async def process_credentials(message: types.Message, state: FSMContext):
    await state.update_data(credentials=message.text)
    await state.set_state(BotStates.sending_receipt)
    await message.answer(f"To'lovni amalga oshiring:\n💳 Karta: <code>{KARTA}</code>\n\nChek rasmini shu yerga yuboring.", parse_mode="HTML")

@dp.message(BotStates.sending_receipt, F.photo)
@dp.message(BotStates.sending_receipt, F.photo)
async def process_receipt(message: types.Message, state: FSMContext):
    data = load_data()
    order_id = get_next_order_id()
    fsm_data = await state.get_data()
    
    data["orders"][str(order_id)] = {"user_id": message.from_user.id, "details": fsm_data, "status": "Kutilmoqda ⏳"}
    save_data(data)
    
    await message.answer(f"✅ Qabul qilindi. Buyurtma raqamingiz: #N{order_id}")
    
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Tasdiqlash", callback_data=f"adm_pay_ok:{str(order_id)}")
    builder.button(text="❌ Rad etish", callback_data=f"adm_rej:{str(order_id)}")
    builder.adjust(2)
    
    platforma = fsm_data.get('platform', 'Android')
    region_nomi = fsm_data.get('region', "O'yin ichidan")
    paket_nomi = fsm_data.get('packet', 'Coins')
    login_parol = fsm_data.get('credentials', 'Kiritilmagan')
    
    # Ismdagi maxsus belgilar xato bermasligi uchun HTML formatiga to'g'ri o'tkazildi!
    if message.from_user.username:
        mijoz_link = f"@{message.from_user.username}"
    else:
        toza_ism = message.from_user.full_name.replace("<", "&lt;").replace(">", "&gt;")
        mijoz_link = f'<a href="tg://user?id={message.from_user.id}">{toza_ism}</a>'
    
    admin_text = f"🚨 <b>YANGI BUYURTMA #N{order_id}</b>\n\n" \
                 f"👤 Mijoz: {mijoz_link} (ID: <code>{message.from_user.id}</code>)\n" \
                 f"📱 Platforma: {platforma}\n" \
                 f"🌍 Region: {region_nomi}\n" \
                 f"📦 Paket: {paket_nomi}\n" \
                 f"🔑 Ma'lumotlar: <code>{login_parol}</code>"
    try:
        await bot.send_photo(chat_id=ADMIN_ID, photo=message.photo[-1].file_id, caption=admin_text, reply_markup=builder.as_markup(), parse_mode="HTML")
    except Exception:
        pass
    await state.clear()


# --- ADMIN CALLBACK PROCESS ---
@dp.callback_query(F.data.startswith("adm_pay_ok:"))
async def admin_payment_ok(callback: types.CallbackQuery):
    if callback.from_user.id != ADMIN_ID: return
    order_id = str(callback.data.split(":")[-1]).strip()
    
    builder = InlineKeyboardBuilder()
    builder.button(text="🎉 Buyurtma bajarildi", callback_data=f"adm_done:{order_id}")
    builder.button(text="❌ Rad etish", callback_data=f"adm_rej:{order_id}")
    builder.adjust(1)
    
    try:
        # Xabar tahrirlashda parse_mode olib tashlandi, shunda bot har qanday belgida qotmaydi!
        await callback.message.edit_caption(
            caption=str(callback.message.caption or "") + f"\n\n💰 To'lov tasdiqlandi. Coin yuklangach 'Bajarildi' tugmasini bosing.", 
            reply_markup=builder.as_markup(),
            parse_mode=None
        )
    except Exception:
        await callback.message.reply(text=f"💰 #N{order_id} To'lov tasdiqlandi. Coin yuklangach quyidagi tugmalarni bosing:", reply_markup=builder.as_markup())
        
    await callback.answer()

@dp.callback_query(F.data.startswith("adm_done:"))
async def admin_order_done(callback: types.CallbackQuery):
    order_id = str(callback.data.split(":")[-1]).strip()
    data = load_data()
    order = data["orders"].get(str(order_id))
    
    if order and order["status"] != "Bajarildi ✅":
        order["status"] = "Bajarildi ✅"
        user_id = order["user_id"]
        
        mijoz_user = f"@{callback.from_user.username}" if callback.from_user.username else f"Mijoz_{user_id}"
        details = order.get("details", {})
        coin_amount = details.get("coin_amount", 0)
        paket_nomi = details.get("packet", "Coins")
        
        if coin_amount >= 5700 or "5700" in str(paket_nomi):
            if "tournament" not in data: data["tournament"] = []
            if mijoz_user not in data["tournament"] and len(data["tournament"]) < 64:
                data["tournament"].append(mijoz_user)
                try:
                    yangi_count = len(data["tournament"])
                    await bot.send_message(MAIN_CHANNEL, f"🔥 <b>TURNIRGA YANGI ISHTIROKCHI!</b>\n\n👤 O'yinchi: {mijoz_user}\n📊 Slot: <code>{yangi_count} / 64</code> o'yinchi", parse_mode="HTML")
                except Exception: pass

        cashback = coin_amount // 100
        init_user(user_id)
        data["users"][str(user_id)]["bonus"] += cashback
        
        if not data["users"][str(user_id)]["has_purchased"]:
            data["users"][str(user_id)]["has_purchased"] = True
            referrer_id = data["users"][str(user_id)]["referred_by"]
            if referrer_id and str(referrer_id) in data["users"]:
                data["users"][str(referrer_id)]["bonus"] += 50
                data["users"][str(referrer_id)]["referrals_count"] += 1
        save_data(data)
        
        builder = InlineKeyboardBuilder()
        builder.button(text="✍️ Sharh (Otziv) qoldirish", callback_data=f"write_review:{order_id}")
        await bot.send_message(chat_id=user_id, text=f"🎉 <b>Buyurtmangiz #N{order_id} bajarildi!</b>\nCoins yuklandi.\n\nIltimos, quyidagi tugma orqali sharh qoldiring 👇", reply_markup=builder.as_markup(), parse_mode="HTML")
        try:
            await callback.message.edit_caption(caption=callback.message.caption + f"\n\n🟢 STATUS: BAJARILDI", parse_mode="HTML")
        except Exception:
            await callback.message.reply(text=f"🟢 STATUS: #N{order_id} BAJARILDI")
    await callback.answer()

@dp.callback_query(F.data.startswith("adm_rej:"))
async def admin_order_reject(callback: types.CallbackQuery):
    order_id = str(callback.data.split(":")[-1]).strip()
    data = load_data()
    order = data["orders"].get(str(order_id))
    
    if order:
        order["status"] = "Rad etildi ❌"
        save_data(data)
        
        builder = InlineKeyboardBuilder()
        builder.button(text="👨‍💻 Admin bilan bog'lanish", url="https://t.me/jocker7005")

        await bot.send_message(
            chat_id=order["user_id"], 
            text=f"❌ Kechirasiz, sizning #N{order_id} raqamli buyurtmangiz rad etildi.\n\nℹ️ Muammoni hal qilish uchun admin bilan bog'laning 👇",
            reply_markup=builder.as_markup()
        )
        try:
            await callback.message.edit_caption(caption=callback.message.caption + f"\n\n🔴 STATUS: RAD ETILDI", parse_mode="HTML")
        except Exception:
            await callback.message.reply(text=f"🔴 STATUS: #N{order_id} RAD ETILDI")
    await callback.answer()

# --- SHARHLAR ---
@dp.callback_query(F.data.startswith("write_review:"))
async def start_review(callback: types.CallbackQuery, state: FSMContext):
    order_id = str(callback.data.split(":")[-1]).strip()
    await state.set_state(BotStates.writing_review)
    await state.update_data(order_id=order_id)
    await callback.message.answer("Xizmatimiz haqidagi fikringizni (sharhingizni) yozib yuboring:")
    await callback.answer()

@dp.message(BotStates.writing_review, F.text)
async def process_review(message: types.Message, state: FSMContext):
    if message.text in ["🛒 Android Coins", "🌍 Regionlar uchun Coins", "🏆 Turnir", "🎁 Bonuslarim", "📖 Qo'llanma", "📦 Mening buyurtmalarim", "⭐ Sharhlar", "✍️ Taklif qoldirish", "👨‍💻 Admin / Yordam", "🎯 Kunlik Viktorina"]:
        await state.clear()
        return await dp.feed_message(bot, message)
    fsm_data = await state.get_data()
    order_id = fsm_data.get("order_id")
    data = load_data()
    order = data["orders"].get(str(order_id))
    mijoz_user = f"@{message.from_user.username}" if message.from_user.username else message.from_user.full_name
    if order:
        order["review"] = message.text
        save_data(data)
        details = order.get("details", {})
        plat, reg, pak = details.get('platform', 'Android'), details.get('region', 'Global'), details.get('packet', 'Coins')
    else:
        plat, reg, pak = "Android", "Global", "Coins"
    
    bot_info = await bot.get_me()
    channel_msg = f"🎉 XARID VA SHARH MUVAFFAQIYATLI YAKUNLANDI!\n\n📦 Buyurtma raqami: #N{order_id}\n👤 Mijoz: {mijoz_user}\n📱 Platforma: {plat}\n🌍 Region: {reg}\n💰 Paket: {pak}\n\n💬 Sharh:\n\"{message.text}\"\n\n🤖 @{bot_info.username}"
    try:
        await bot.send_message(chat_id=MAIN_CHANNEL, text=channel_msg)
        await message.answer("✅ Rahmat! Sharhingiz guruhimizga joylashtirildi. 🤝")
    except Exception:
        await message.answer("Sharh uchun rahmat!")
    await state.clear()

@dp.message(F.text == "🛠 Admin Panel")
async def cmd_admin_panel(message: types.Message):
    if message.from_user.id in ADMINS:
        data = load_data()
        await message.answer(f"🛠 <b>Admin Panel</b>\n\n👥 Foydalanuvchilar: {len(data.get('users', {}))}\n📦 Buyurtmalar: {len(data.get('orders', {}))}", parse_mode="HTML")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
