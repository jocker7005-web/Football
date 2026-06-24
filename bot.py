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
from aiogram.exceptions import TelegramBadRequest

logging.basicConfig(level=logging.INFO)

# --- MAXFIY MA'LUMOTLAR VA KONSTANTALAR ---
BOT_TOKEN = "8893476065:AAHTxgo0fwTnnnU44jwpKLPvk7m5MjVHf0g"
ADMIN_ID = 1678146043
KARTA = "9860 3501 0897 5409 (Xusanova M)"
MAIN_CHANNEL = "@levelGroup_eFHub"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

DATA_FILE = "bot_data.json"

# --- MA'LUMOTLAR BAZASI (JSON) FUNKSIYALARI ---
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
            existing_ids = [int(x) for x in orders.keys() if x.isdigit()]
            if existing_ids:
                new_id = max(existing_ids) + 1
            else:
                new_id = data.get("last_id", 0) + 1
        except Exception:
            new_id = data.get("last_id", 0) + 1
    else:
        new_id = data.get("last_id", 0) + 1
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
# --- MAJBURIY OBUNA TEKSHIRISH FUNKSIYASI ---
async def check_subscription(user_id: int) -> bool:
    if user_id == ADMIN_ID:
        return True
    try:
        member = await bot.get_chat_member(chat_id="@levelGroup_eFHub", user_id=user_id)
        if member.status in ["creator", "administrator", "member"]:
            return True
        return True
    except Exception as e:
        logging.error(f"Obunani tekshirishda xato: {e}")
        return True

# --- MAJBURIY OBUNA INLINE TUGMASI ---
def get_sub_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text="Kanalga a'zo bo'lish 📢", url=f"https://t.me{MAIN_CHANNEL.replace('@', '')}")
    builder.button(text="Tekshirish 🔄", callback_data="sub_check")
    builder.adjust(1)
    return builder.as_markup()

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
    init_user(user_id, username)
    
    args = message.text.split()
    if len(args) > 1:
        referrer_id = args[1]
        data = load_data()
        if referrer_id != str(user_id):
            if data["users"].get(str(user_id)) and data["users"][str(user_id)]["referred_by"] is None:
                data["users"][str(user_id)]["referred_by"] = referrer_id
                save_data(data)

    await message.answer(
        f"Salom {message.from_user.full_name}! Efootball Coins botiga xush kelibsiz!\nKerakli bo'limni tanlang:",
        reply_markup=get_main_menu(user_id)
    )

# --- INLINE OBUNA TEKSHIRISH CALLBACK ---
@dp.callback_query(F.data == "sub_check")
async def process_sub_check(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    if await check_subscription(user_id):
        await callback.message.delete()
        await callback.message.answer(
            "✅ Rahmat! Obuna tasdiqlandi. Botdan to'liq foydalanishingiz mumkin:",
            reply_markup=get_main_menu(user_id)
        )
    else:
        await callback.answer("❌ Siz hali kanalga a'zo bo'lmadingiz!", show_alert=True)
# --- AXBOROT BERUVCHI TUGMALAR ---
@dp.message(F.text == "📖 Qo'llanma")
async def cmd_guide(message: types.Message):
    if not await check_subscription(message.from_user.id):
        await message.answer("❌ Avval kanalimizga a'zo bo'ling!", reply_markup=get_sub_keyboard())
        return
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
    if not await check_subscription(message.from_user.id):
        await message.answer("❌ Avval kanalimizga a'zo bo'ling!", reply_markup=get_sub_keyboard())
        return
    await message.answer(f"⭐ Barcha muvaffaqiyatli xaridlar va mijozlarimiz sharhlari avtomatik tarzda rasmiy kanalimizga joylab boriladi: {MAIN_CHANNEL}")

@dp.message(F.text == "👨‍💻 Admin / Yordam")
async def cmd_support(message: types.Message):
    if not await check_subscription(message.from_user.id):
        await message.answer("❌ Avval kanalimizga a'zo bo'ling!", reply_markup=get_sub_keyboard())
        return
    await message.answer("👨‍💻 Har qanday savollar yoki muammolar bo'yicha adminga murojaat qiling: @jocker7005")

# --- 🎁 BONUSLARIM VA REFERAL TIZIMI (50 COINS) ---
@dp.message(F.text == "🎁 Bonuslarim")
async def cmd_bonuses(message: types.Message):
    user_id = message.from_user.id
    if not await check_subscription(user_id):
        await message.answer("❌ Avval kanalimizga a'zo bo'ling!", reply_markup=get_sub_keyboard())
        return
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
        f"Shuningdek o'z xaridlaringizdan ham keshbek qo'shiladi. Minimal yechish: 600 Coins.*"
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
            text=f"🎁 **BONUS YECHISH SO'ROVI**\n\nMijoz: {callback.from_user.mention}\nID: {user_id}\n600 Coins bonus yechishni so'radi."
        )
        await callback.message.answer("✅ So'rov adminga yuborildi. Tez orada siz bilan bog'lanishadi.")
    else:
        await callback.answer("Mablag' yetarli emas!", show_alert=True)
    await callback.answer()

# --- ✍️ TAKLIF QOLDIRISH ---
@dp.message(F.text == "✍️ Taklif qoldirish")
async def cmd_suggestion(message: types.Message, state: FSMContext):
    if not await check_subscription(message.from_user.id):
        await message.answer("❌ Avval kanalimizga a'zo bo'ling!", reply_markup=get_sub_keyboard())
        return
    await state.set_state(BotStates.writing_suggestion)
    await message.answer("Fikr, taklif yoki shikoyatingizni matn ko'rinishida yozib yuboring:")

@dp.message(BotStates.writing_suggestion, F.text)
async def process_suggestion(message: types.Message, state: FSMContext):
    await bot.send_message(
        chat_id=ADMIN_ID,
        text=f"✍️ **YANGI TAKLIF/SHIKOYAT**\n\nKimdan: {message.from_user.mention}\nID: {message.from_user.id}\n\nMatn:\n{message.text}"
    )
    await state.clear()
    await message.answer("✅ Taklifingiz muvaffaqiyatli adminga yetkazildi. Rahmat!")

# --- 📦 MENING BUYURTMALARIM (TARIXI) ---
@dp.message(F.text == "📦 Mening buyurtmalarim")
async def cmd_my_orders(message: types.Message):
    user_id = message.from_user.id
    if not await check_subscription(user_id):
        await message.answer("❌ Avval kanalimizga a'zo bo'ling!", reply_markup=get_sub_keyboard())
        return
    data = load_data()
    orders = data.get("orders", {})
    
    user_orders = {k: v for k, v in orders.items() if str(v["user_id"]) == str(user_id)}
    
    if not user_orders:
        await message.answer("Sizda hali xaridlar tarixi mavjud emas.")
        return
        
    text = "📦 **Sizning xaridlar tariqingiz:**\n\n"
    for o_id, o_data in user_orders.items():
        details = o_data.get("details", {})
        status = o_data.get("status", "Kutilmoqda ⏳")
        text += (
            f"🔹 **Buyurtma #N{o_id}**\n"
            f"🛒 Turi: {details.get('platform', 'Nomalum')}\n"
            f"💰 Paket: {details.get('packet', 'Nomalum')}\n"
            f"📊 Holati: {status}\n\n"
        )
    await message.answer(text)

# --- 🏆 TURNIR BO'LIMI ---
@dp.message(F.text == "🏆 Turnir")
async def cmd_tournament(message: types.Message):
    if not await check_subscription(message.from_user.id):
        await message.answer("❌ Avval kanalimizga a'zo bo'ling!", reply_markup=get_sub_keyboard())
        return
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
    if message.from_user.id in participants:
        text += "✅ Siz muvaffaqiyatli turnir ro'yxatiga kiritilgansiz!"
    else:
        text += "🛒 Qatnashish uchun 5700 va undan baland paket xarid qiling."
        
    await message.answer(text)

# --- 🛒 ANDROID COINS XARID BOSQICHI ---
@dp.message(F.text == "🛒 Android Coins")
async def cmd_android_coins(message: types.Message, state: FSMContext):

    prices = [
        "260 coins -> 40.000 so'm", "300 coins -> 45.000 so'm", "390 coins -> 60.000 so'm",
        "550 coins -> 70.000 so'm", "750 coins -> 95.000 so'm", "1040 coins -> 125.000 so'm",
        "1790 coins -> 210.000 so'm", "2130 coins -> 240.000 so'm", "2680 coins -> 310.000 so'm",
        "3250 coins -> 350.000 so'm", "4000 coins -> 440.000 so'm", "5700 coins -> 560.000 so'm",
        "7040 coins -> 730.000 so'm", "9990 coins -> 1.050.000 so'm", "12.800 coin -> 1.190.000 so'm"
    ]
    builder = InlineKeyboardBuilder()
    for p in prices:
        coin_num = p.split()[0]
        builder.button(text=p, callback_data=f"and_p:{coin_num}:{p}")
    builder.adjust(1)
    await state.set_state(BotStates.choosing_android_coins)
    await message.answer("Android uchun kerakli paketni tanlang (O'yinga kirib yuklanadi):", reply_markup=builder.as_markup())

@dp.callback_query(F.data.startswith("and_p:"), BotStates.choosing_android_coins)
async def process_android_choice(callback: types.CallbackQuery, state: FSMContext):
    parts = callback.data.split(":", 2)
    coin_amount = int(parts[1])
    packet = parts[2]

    await state.update_data(platform="Android", packet=packet, region="O'yin ichidan (Android)", coin_amount=coin_amount)
    await callback.message.delete()
    await state.set_state(BotStates.entering_credentials)
    await callback.message.answer("O'yinga kirish uchun Konami ID va Parolni kiriting:\n\n*Misol:* info@gmail.com / parol123")
    await callback.answer()
# --- 🌍 REGIONLAR UCHUN COINS XARID BOSQICHI (BARCHA 13 TA DAVLAT) ---
@dp.message(F.text == "🌍 Regionlar uchun Coins")
async def cmd_region_coins(message: types.Message, state: FSMContext):
    if not await check_subscription(message.from_user.id):
        await message.answer("❌ Avval kanalimizga a'zo bo'ling!", reply_markup=get_sub_keyboard())
        return
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
    await state.update_data(region=region, platform="Region (Android/iOS)")
    
    prices = [
        "578 coins -> 70.000 so'm", "788 coins -> 100.000 so'm", "1092 coins -> 135.000 so'm",
        "2237 coins -> 250.000 so'm", "2815 coins -> 315.000 so'm", "3413 coins -> 370.000 so'm",
        "4474 coins -> 500.000 so'm", "5985 coins -> 600.000 so'm", "13440 coins -> 1.250.000 so'm",
        "32200 coins -> 2.800.000 so'm"
    ]
    builder = InlineKeyboardBuilder()
    for p in prices:
        coin_num = p.split()[0]
        builder.button(text=p, callback_data=f"reg_p:{coin_num}:{p}")
    builder.adjust(1)
    await state.set_state(BotStates.choosing_region_coins)
    await callback.message.edit_text(f"Tanlangan region: {region}\nCoins paketini tanlang:", reply_markup=builder.as_markup())
    await callback.answer()

@dp.callback_query(F.data.startswith("reg_p:"), BotStates.choosing_region_coins)
async def process_region_packet(callback: types.CallbackQuery, state: FSMContext):
    parts = callback.data.split(":", 2)
    coin_amount = int(parts[1])
    packet = parts[2]

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
    
    admin_text = f"""🚨 **YANGI BUYURTMA #N{order_id}**

👤 Mijoz: {message.from_user.full_name} (ID: {message.from_user.id})
📱 Platforma: {platforma}
🌍 Region: {region_nomi}
📦 Paket: {paket_nomi}
🔑 Ma'lumotlar: `{login_parol}`"""
    
    try:
        # Barcha buyurtma maxfiy ma'lumotlari faqat ushbu kanalga yuboriladi
        await bot.send_photo(
            chat_id=MAIN_CHANNEL,
            photo=message.photo[-1].file_id,
            caption=admin_text,
            reply_markup=builder.as_markup()
        )
    except Exception as e:
        logging.error(f"Kanalga buyurtma yuborishda xato: {e}")
        
    await state.clear()

# --- ADMIN PROCESS ---
@dp.callback_query(F.data.startswith("adm_pay_ok:"))
async def admin_payment_ok(callback: types.CallbackQuery):
    order_id = callback.data.split(":", 1)[1]
    
    builder = InlineKeyboardBuilder()
    builder.button(text="🎉 Buyurtma bajarildi", callback_data=f"adm_done:{order_id}")
    builder.button(text="❌ Rad etish", callback_data=f"adm_rej:{order_id}")
    builder.adjust(1)
    
    await callback.message.edit_caption(
        caption=callback.message.caption + f"\n\n💰 *To'lov tasdiqlandi. Coin #N{order_id} buyurtmaga tashlangandan so'ng 'Buyurtma bajarildi' tugmasini bosing.*",
        reply_markup=builder.as_markup(),
        parse_mode="Markdown"
    )
    await callback.answer()

@dp.callback_query(F.data.startswith("adm_done:"))
async def admin_order_done(callback: types.CallbackQuery):
    order_id = callback.data.split(":", 1)[1]
    data = load_data()
    order = data["orders"].get(str(order_id))
    
    if order and order["status"] != "Bajarildi ✅":
        order["status"] = "Bajarildi ✅"
        user_id = order["user_id"]
        coin_amount = order["details"].get("coin_amount", 0)
        
        cashback = coin_amount // 100
        init_user(user_id)
        data["users"][str(user_id)]["bonus"] += cashback
        
        if not data["users"][str(user_id)]["has_purchased"]:
            data["users"][str(user_id)]["has_purchased"] = True
            referrer_id = data["users"][str(user_id)]["referred_by"]
            if referrer_id and str(referrer_id) in data["users"]:
                data["users"][str(referrer_id)]["bonus"] += 50 # 50 Coins referal bonus
                data["users"][str(referrer_id)]["referrals_count"] += 1
                try:
                    await bot.send_message(chat_id=int(referrer_id), text="🎁 Do'stingiz xarid qildi! Sizga +50 Coins bonus berildi.")
                except Exception:
                    pass
                    
        if coin_amount >= 5700:
            if user_id not in data["tournament"]:
                data["tournament"].append(user_id)
                if len(data["tournament"]) == 64:
                    await bot.send_message(chat_id=ADMIN_ID, text="🏆 DIQQAT! Turnir ishtirokchilari 64 taga yetdi, setkani shakllantiring.")
                    data["tournament"] = []
        
        save_data(data)
        
        builder = InlineKeyboardBuilder()
        builder.button(text="✍️ Sharh (Otziv) qoldirish", callback_data=f"write_review:{order_id}")
        
        await bot.send_message(
            chat_id=user_id,
            text=f"🎉 **Buyurtmangiz #N{order_id} muvaffaqiyatli bajarildi!**\nCoins akkauntingizga yuklandi.\n"
                 f"Xarid uchun +{cashback} bonus coin hamyoningizga qo'shildi.\n\n"
                 f"Iltimos, quyidagi tugma orqali xizmatimiz haqida sharh qoldiring 👇",
            reply_markup=builder.as_markup()
        )
        
        await callback.message.edit_caption(caption=callback.message.caption + f"\n\n🟢 **STATUS: #N{order_id} BAJARILDI VA MIJOZGA XABAR BORDI**")
    await callback.answer()

@dp.callback_query(F.data.startswith("adm_rej:"))
async def admin_order_reject(callback: types.CallbackQuery):
    order_id = callback.data.split(":", 1)[1]
    data = load_data()
    order = data["orders"].get(str(order_id))
    
    if order:
        order["status"] = "Rad etildi ❌"
        save_data(data)
        await bot.send_message(
            chat_id=order["user_id"],
            text=f"❌ Kechirasiz, sizning #N{order_id} raqamli buyurtmangiz admin tomonidan **RAD ETILDI**.\nTo'lov yoki ma'lumotlarni qayta tekshirib adminga murojaat qiling."
        )
        await callback.message.edit_caption(caption=callback.message.caption + f"\n\n🔴 **STATUS: #N{order_id} RAD ETILDI**")
    await callback.answer()

# --- SHARH QOBUL QILISH VA KANALGA JOYLASHTIRISH ---
@dp.callback_query(F.data.startswith("write_review:"))
async def start_review(callback: types.CallbackQuery, state: FSMContext):
    order_id = callback.data.split(":", 1)[1]
    await state.update_data(review_order_id=order_id)
    await state.set_state(BotStates.writing_review)
    await callback.message.answer("Xizmatimiz haqidagi fikringizni (sharhingizni) yozib yuboring:")
    await callback.answer()

@dp.message(BotStates.writing_review, F.text)
async def process_review(message: types.Message, state: FSMContext):
    fsm_data = await state.get_data()
    order_id = fsm_data.get("review_order_id")
    
    bot_info = await bot.get_me()
    channel_msg = f"""🌟 **YANGI SHARH (OTZIV)**

📦 **Buyurtma raqami:** #N{order_id}
👤 **Mijoz:** {message.from_user.mention}
💬 **Sharh:** "{message.text}"

🤖 @{bot_info.username}"""
    
    try:
        # Sharhlar ham to'g'ridan-to'g'ri o'sha yagona kanalga boradi
        await bot.send_message(
            chat_id=MAIN_CHANNEL, 
            text=channel_msg,
            parse_mode="Markdown"
        )
        await message.answer("✅ Rahmat! Sharhingiz buyurtma raqamingiz bilan bir xil tartibda rasmiy kanalimizga joylashtirildi. 🤝")
    except Exception:
        await message.answer("Sharh uchun rahmat! (Botni kanalga admin qilib tayinlashni unutmang)")
        
    await state.clear()

@dp.message(F.text == "🛠 Admin Panel")
async def cmd_admin_panel(message: types.Message):
    if message.from_user.id != 1678146043: return

    data = load_data()
    total_users = len(data.get("users", {}))
    total_orders = len(data.get("orders", {}))
    await message.answer(f"🛠 **Admin Panel**\n\n👥 Jami foydalanuvchilar: {total_users}\n📦 Jami buyurtmalar: {total_orders}")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
