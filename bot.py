import os
import logging
import asyncio
from datetime import datetime
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

# Bot sozlamalari
API_TOKEN = '8893476065:AAEcYyKoFzFev4t66E6YeX7HolTDhv2oFhc'


ADMIN_ID = 1678146043  
PROOF_CHAT_ID = -1002220302390  

order_counter = 0
total_users = set()
user_bonuses = {}  

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# 📥 ID ORQALI YUKLASH NARXLARI
DIRECT_PACKS = {
    "d_578": {"name": "🪙 578 coins (ID orqali)", "price": "70.000 so'm", "cashback": 5},
    "d_788": {"name": "🪙 788 coins (ID orqali)", "price": "100.000 so'm", "cashback": 7},
    "d_1092": {"name": "🪙 1092 coins (ID orqali)", "price": "135.000 so'm", "cashback": 10},
    "d_2237": {"name": "🪙 2237 coins (ID orqali)", "price": "250.000 so'm", "cashback": 18},
    "d_2815": {"name": "🪙 2815 coins (ID orqali)", "price": "315.000 so'm", "cashback": 22},
    "d_3413": {"name": "🪙 3413 coins (ID orqali)", "price": "370.000 so'm", "cashback": 25},
    "d_4474": {"name": "🪙 4474 coins (ID orqali)", "price": "500.000 so'm", "cashback": 35},
    "d_5985": {"name": "🪙 5985 coins (ID orqali)", "price": "600.000 so'm", "cashback": 45},
    "d_13440": {"name": "🪙 13440 coins (ID orqali)", "price": "1.250.000 so'm", "cashback": 55},
    "d_32200": {"name": "🪙 32200 coins (ID orqali)", "price": "2.800.000 so'm", "cashback": 100}
}

# 📱 AKKOUNTGA KIRIB YUKLASH NARXLARI
LOGIN_PACKS = {
    "a_260": {"name": "🪙 260 coins (Kirib)", "price": "40.000 so'm", "cashback": 2},
    "a_300": {"name": "🪙 300 coins (Kirib)", "price": "45.000 so'm", "cashback": 3},
    "a_390": {"name": "🪙 390 coins (Kirib)", "price": "60.000 so'm", "cashback": 4},
    "a_550": {"name": "🪙 550 coins (Kirib)", "price": "70.000 so'm", "cashback": 5},
    "a_750": {"name": "🪙 750 coins (Kirib)", "price": "95.000 so'm", "cashback": 7},
    "a_1040": {"name": "🪙 1040 coins (Kirib)", "price": "125.000 so'm", "cashback": 10},
    "a_1790": {"name": "🪙 1790 coins (Kirib)", "price": "210.000 so'm", "cashback": 15},
    "a_2130": {"name": "🪙 2130 coins (Kirib)", "price": "240.000 so'm", "cashback": 18},
    "a_2680": {"name": "🪙 2680 coins (Kirib)", "price": "310.000 so'm", "cashback": 22},
    "a_3250": {"name": "🪙 3250 coins (Kirib)", "price": "350.000 so'm", "cashback": 25},
    "a_4000": {"name": "🪙 4000 coins (Kirib)", "price": "440.000 so'm", "cashback": 30},
    "a_5700": {"name": "🪙 5700 coins (Kirib)", "price": "560.000 so'm", "cashback": 40},
    "a_7040": {"name": "🪙 7040 coins (Kirib)", "price": "730.000 so'm", "cashback": 45},
    "a_9990": {"name": "🪙 9990 coins (Kirib)", "price": "1.050.000 so'm", "cashback": 50},
    "a_12800": {"name": "🪙 12.800 coin (Kirib)", "price": "1.190.000 so'm", "cashback": 55}
}

CARD_INFO = "💳 Karta raqam: `9860 3501 0897 5409`\n👤 Ega: XUSANOVA MAQSUDA"

class OrderState(StatesGroup):
    choosing_method = State()
    choosing_pack = State()
    entering_id = State()
    entering_password = State()
    sending_receipt = State()

class WithdrawState(StatesGroup):
    entering_id = State()
    entering_password = State()

class AdminState(StatesGroup):
    waiting_rejection_reason = State()
    waiting_broadcast_msg = State()

def get_main_keyboard():
    return ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="🪙 Coin sotib olish"), KeyboardButton(text="📊 Narxlar va Paketlar")],
        [KeyboardButton(text="💰 Mening Bonuslarim"), KeyboardButton(text="🎁 Bepul Coin yechish")],
        [KeyboardButton(text="ℹ️ Qo'llanma / Qoidalar"), KeyboardButton(text="⭐️ Sharhlar")],
        [KeyboardButton(text="👨‍💻 Aloqa / Admin")]
    ], resize_keyboard=True)

def is_work_time():
    current_hour = datetime.now().hour
    if 1 <= current_hour < 8:
        return False
    return True

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    uid = message.from_user.id
    total_users.add(uid)
    if uid not in user_bonuses:
        user_bonuses[uid] = 0  
    await message.answer(
        f"👋 Assalomu alaykum, {message.from_user.full_name}!\n"
        "eFootball Coin sotuvchi rasmiy botga xush kelibsiz.",
        reply_markup=get_main_keyboard()
    )

@dp.message(Command("panel"))
async def admin_panel(message: types.Message):
    if message.from_user.id == ADMIN_ID:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📢 Reklama tarqatish", callback_data="admin_broadcast")]
        ])
        await message.answer(
            "⚙️ **ADMIN PANEL**\n\n"
            f"👥 Jami a'zolar: **{len(total_users)} ta**\n"
            f"📦 Jami buyurtmalar: **{order_counter} ta**",
            reply_markup=keyboard
        )

@dp.callback_query(F.data == "admin_broadcast")
async def start_broadcast(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer("📢 Reklama xabarini yuboring:")
    await state.set_state(AdminState.waiting_broadcast_msg)
    await callback.answer()

@dp.message(AdminState.waiting_broadcast_msg)
async def process_broadcast(message: types.Message, state: FSMContext):
    await message.answer("🚀 Reklama yuborilmoqda...")
    count = 0
    for uid in total_users:
        try:
            if message.photo:
                await bot.send_photo(chat_id=uid, photo=message.photo[-1].file_id, caption=message.caption)
            else:
                await bot.send_message(chat_id=uid, text=message.text)
            count += 1
        except:
            pass
    await message.answer(f"✅ Reklama yakunlandi: **{count} ta** odamga bordi.")
    await state.clear()

@dp.message(F.text == "💰 Mening Bonuslarim")
async def show_bonus(message: types.Message):
    bonus = user_bonuses.get(message.from_user.id, 0)
    await message.answer(
        f"💰 **Sizning hamyoningiz:**\n\nSizda hozir: **{bonus} ta bonus Coin** bor.\n\n"
        f"⚠️ *Balansingiz 550 coinga yetganda uni tekinga o'yin hisobingizga chiqarib olishingiz mumkin!*"
    )

@dp.message(F.text == "🎁 Bepul Coin yechish")
async def withdraw_bonus(message: types.Message, state: FSMContext):
    if not is_work_time():
        await message.answer("🕒 **Do'konimiz yopiq!**\nIsh vaqti: 08:00 dan 01:00 gacha.")
        return
    bonus = user_bonuses.get(message.from_user.id, 0)
    if bonus < 550:
        await message.answer(f"❌ **Bonuslar yetarli emas!**\nSizda hozir: **{bonus} coin** bor.\nMinimal yechish: **550 coin**.")
    else:
        await message.answer("🎁 **Bonuslaringiz etarli.**\n\n📧 Konami ID (Email) kiriting:")
        await state.set_state(WithdrawState.entering_id)

@dp.message(WithdrawState.entering_id)
async def withdraw_id(message: types.Message, state: FSMContext):
    if "@" not in message.text or "." not in message.text:
        await message.answer("⚠️ Noto'g'ri email! Qaytadan kiriting:")
        return
    await state.update_data(konami_id=message.text)
    await message.answer("🔑 Konami parolingizni kiriting:")
    await state.set_state(WithdrawState.entering_password)

@dp.message(WithdrawState.entering_password)
async def withdraw_pass(message: types.Message, state: FSMContext):
    global order_counter
    order_counter += 1
    uid = message.from_user.id
    user_data = await state.get_data()
    user_bonuses[uid] -= 550  
    
    admin_markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Bonus Coin tashladim", callback_data=f"done_{uid}_{order_counter}"),
         InlineKeyboardButton(text="❌ Rad etish", callback_data=f"reject_{uid}_{order_counter}")]
    ])
    admin_text = (
        f"🎁 **TEKIN COIN YECHISH!**\n🆔 **Buyurtma raqami:** #{order_counter}\n"
        f"👤 **Mijoz:** @{message.from_user.username or 'Yashirin'} (ID: {uid})\n\n"
        f"🔥 **Miqdor:** 550 Tekin Coin\n📧 **Konami ID:** `{user_data['konami_id']}`\n🔑 **Parol:** `{message.text}`"
    )
    await bot.send_message(chat_id=ADMIN_ID, text=admin_text, reply_markup=admin_markup, parse_mode="Markdown")
    await message.answer(f"✅ **Arizangiz yuborildi!**\nBuyurtma raqamingiz: **#{order_counter}**", reply_markup=get_main_keyboard())
    await state.clear()

@dp.message(F.text == "📊 Narxlar va Paketlar")
async def show_prices(message: types.Message):
    text = "📋 **Bizdagi mavjud coin paketlari va narxlari:**\n\n📥 **ID orqali (Akkountga kirmasdan):**\n"
    for pack in DIRECT_PACKS.values():
        text += f"▪️ {pack['name']} — {pack['price']} (+{pack['cashback']} bonus)\n"
    text += "\n📱 **Akkountga kirib yuklash (Android & iOS):**\n"
    for pack in LOGIN_PACKS.values():
        text += f"▪️ {pack['name']} — {pack['price']} (+{pack['cashback']} bonus)\n"
    await message.answer(text, parse_mode="Markdown")

@dp.message(F.text == "ℹ️ Qo'llanma / Qoidalar")
async def show_guide(message: types.Message):
    await message.answer("ℹ️ **Ish vaqti:** 08:00 dan 01:00 gacha.\n\nCard raqamga pul o'tkazib chek yuboring. Ikkala usulda ham xavfsizlik uchun ID va parol so'raladi!")

@dp.message(F.text == "⭐️ Sharhlar")
async def show_reviews(message: types.Message):
    await message.answer("⭐️ **Mijozlarimiz fikrlari va barcha isbotlar shu yerda:**\nhttps://t.me")

@dp.message(F.text == "👨‍💻 Aloqa / Admin")
async def show_contact(message: types.Message):
    await message.answer("👨‍💻 Muammolar bo'lsa admin bilan bog'laning: @Jocker_7005")

# 🪙 COIN SOTIB OLISH BOSQICHLARI
@dp.message(F.text == "🪙 Coin sotib olish")
async def start_order(message: types.Message, state: FSMContext):
    if not is_work_time():
        await message.answer("🕒 **Do'konimiz yopiq!**\nIsh vaqti: 08:00 dan 01:00 gacha.")
        return{added_bonus} bonus qo'shildi!", reply_markup=get_main_keyboard())await state.clear()@dp.callback_query(F.data.startswith("done_"))async def process_admin_done(callback: types.CallbackQuery):, user_id, order_id = callback.data.split("")try:await bot.send_message(chat_id=int(user_id), text=f"🎉 Xushxabar!\nSizning #{order_id} raqamli buyurtmangiz muvaffaqiyatli bajarildi! ✅")caption_text = f"✅ MUVAFFAQIYATLI XARID!\n\n🆔 Buyurtma raqami: #{order_id}\n⚡️ Status: Muvaffaqiyatli yakunlandi\n⭐️ Bizni tanlaganingiz uchun rahmat!"if callback.message.photo:await bot.send_photo(chat_id=PROOF_CHAT_ID, photo=callback.message.photo[-1].file_id, caption=caption_text)else:await bot.send_message(chat_id=PROOF_CHAT_ID, text=caption_text)await callback.message.edit_reply_markup(reply_markup=None)await callback.message.answer(f"🟢 #{order_id}-buyurtma bajarildi va isbot guruhiga joylandi.")except Exception as e:await callback.answer(f"Xato: {e}")@dp.callback_query(F.data.startswith("reject_"))async def process_admin_reject(callback: types.CallbackQuery, state: FSMContext):, user_id, order_id = callback.data.split("")await state.update_data(reject_user_id=user_id, reject_order_id=order_id, reject_msg=callback.message)await callback.message.answer(f"❌ #{order_id} buyurtmaning rad etish sababini shu yerga yozib yuboring:")await state.set_state(AdminState.waiting_rejection_reason)await callback.answer()@dp.message(AdminState.waiting_rejection_reason)async def get_rejection_reason(message: types.Message, state: FSMContext):user_data = await state.get_data()uid = int(user_data['reject_user_id'])oid = user_data['reject_order_id']admin_msg = user_data['reject_msg']try:await bot.send_message(chat_id=uid, text=f"❌ Sizning #{oid} raqamli buyurtmangiz rad etildi!\n\n⚠️ Sababi: {message.text}")await admin_msg.edit_reply_markup(reply_markup=None)await message.answer(f"🔴 #{oid}-buyurtma rad etildi.")except:await message.answer("❌ Mijozga xabar yuborishda xatolik.")await state.clear()async def main():port = int(os.environ.get("PORT", 10000))server = await asyncio.start_server(lambda r, w: None, '0.0.0.0', port)await dp.start_polling(bot)if name == 'main':asyncio.run(main())
