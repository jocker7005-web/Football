import os
import logging
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

# Bot sozlamalari
API_TOKEN = '8893476065:AAHthRYT2HV-NEWwe7DnT-PSY6C_uL5S-ak'
ADMIN_ID = 1678146043  
order_counter = 0  

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# SKRINSHOTDAGI YANGI COIN PAKETLARI VA NARXLARI
COIN_PACKS = {
    "260_coin": {"name": "🪙 260 coins", "price": "40.000 so'm"},
    "300_coin": {"name": "🪙 300 coins", "price": "45.000 so'm"},
    "390_coin": {"name": "🪙 390 coins", "price": "60.000 so'm"},
    "550_coin": {"name": "🪙 550 coins", "price": "70.000 so'm"},
    "750_coin": {"name": "🪙 750 coins", "price": "95.000 so'm"},
    "1040_coin": {"name": "🪙 1040 coins", "price": "125.000 so'm"},
    "1790_coin": {"name": "🪙 1790 coins", "price": "210.000 so'm"},
    "2130_coin": {"name": "🪙 2130 coins", "price": "240.000 so'm"},
    "2680_coin": {"name": "🪙 2680 coins", "price": "310.000 so'm"},
    "3250_coin": {"name": "🪙 3250 coins", "price": "350.000 so'm"},
    "4000_coin": {"name": "🪙 4000 coins", "price": "440.000 so'm"},
    "5700_coin": {"name": "🪙 5700 coins", "price": "560.000 so'm"},
    "7040_coin": {"name": "🪙 7040 coins", "price": "730.000 so'm"},
    "9990_coin": {"name": "🪙 9990 coins", "price": "1.050.000 so'm"},
    "12800_coin": {"name": "🪙 12.800 coin", "price": "1.190.000 so'm"}
}

CARD_INFO = "💳 Karta raqam: `9860 3501 0897 5409`\n👤 Ega: XUSANOVA MAQSUDA"

class OrderState(StatesGroup):
    choosing_pack = State()
    entering_id = State()
    entering_password = State()
    sending_receipt = State()

def get_main_keyboard():
    return ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="🪙 Coin sotib olish"), KeyboardButton(text="📊 Narxlar va Paketlar")],
        [KeyboardButton(text="ℹ️ Qo'llanma / Qoidalar"), KeyboardButton(text="⭐️ Sharhlar")],
        [KeyboardButton(text="🎁 Aksiyalar"), KeyboardButton(text="👨‍💻 Aloqa / Admin")]
    ], resize_keyboard=True)

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        f"👋 Assalomu alaykum, {message.from_user.full_name}!\n"
        "eFootball Coin sotuvchi rasmiy botimizga xush kelibsiz.\n"
        "Kerakli bo'limni tanlang 👇",
        reply_markup=get_main_keyboard()
    )

@dp.message(F.text == "📊 Narxlar va Paketlar")
async def show_prices(message: types.Message):
    text = "📋 **Bizdagi mavjud coin paketlari va narxlari (Android):**\n\n"
    for pack in COIN_PACKS.values():
        text += f"▪️ {pack['name']} — **{pack['price']}**\n"
    await message.answer(text, parse_mode="Markdown")

@dp.message(F.text == "ℹ️ Qo'llanma / Qoidalar")
async def show_guide(message: types.Message):
    guide_text = (
        "ℹ️ **Coin sotib olish qo'llanmasi:**\n\n"
        "1. 'Coin sotib olish' tugmasini bosing.\n"
        "2. O'zingizga kerakli paketni tanlang.\n"
        "3. Konami ID va parolingizni xatosiz kiriting.\n"
        "4. Ko'rsatilgan hamyonga pul o'tkazib, chekini (skrinshot) yuboring.\n\n"
        "⚠️ **Xavfsizlik:** Sizning ma'lumotlaringiz faqat coin yuklash uchun ishlatiladi va yuklab bo'lingach tizimdan o'chiriladi!"
    )
    await message.answer(guide_text, parse_mode="Markdown")

@dp.message(F.text == "⭐️ Sharhlar")
async def show_reviews(message: types.Message):
    await message.answer(
        "⭐️ **Mijozlarimiz tomonidan qoldirilgan sharhlar:**\n\n"
        "Do'konimiz ishonchli ekanligiga ishonch hosil qilish uchun "
        "mijozlarimizning fikrlari va cheklarini ko'rishingiz mumkin.\n\n"
        "👉 [Sharhlar kanalimizga o'tish](https://t.me)", 
        parse_mode="Markdown",
        disable_web_page_preview=True
    )

@dp.message(F.text == "🎁 Aksiyalar")
async def show_promos(message: types.Message):
    await message.answer(
        "🎁 **Hozirgi mavjud aksiyalar va chegirmalar:**\n\n"
        "🔥 Tez kunda! Doimiy mijozlarimiz uchun maxsus chegirmalar va "
        "bepul coin yutuqli konkurslar tashkil etiladi.\n\n"
        "Yangiliklarni o'tkazib yubormaslik uchun bizni kuzatib boring!"
    )

@dp.message(F.text == "👨‍💻 Aloqa / Admin")
async def show_contact(message: types.Message):
    await message.answer("👨‍💻 Muammolar yoki takliflar bo'lsa admin bilan bog'laning: @Jocker_7005")

@dp.message(F.text == "🪙 Coin sotib olish")
async def start_order(message: types.Message, state: FSMContext):
    # Paketlar juda ko'pligi uchun tugmalarni 2 qatordan chiroyli qilib chiqaramiz
    buttons = []
    temp_row = []
    for k, v in COIN_PACKS.items():
        temp_row.append(InlineKeyboardButton(text=f"{v['name']} ({v['price']})", callback_data=k))
        if len(temp_row) == 2:
            buttons.append(temp_row)
            temp_row = []
    if temp_row:
        buttons.append(temp_row)
        
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
        logging.error(f"Xato: {e}")

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
        await bot.send_message(
            chat_id=int(user_id),
            text=f"🎉 **Xushxabar!**\nSizning **#{order_id}** raqamli buyurtmangiz muvaffaqiyatli bajarildi. eFootball coinlaringiz o'yin hisobingizga tushirildi! ✅"
        )
        await callback.message.edit_caption(
            caption=callback.message.caption + "\n\n🟢 **BAJARILDI!** (Mijozga xabar yuborildi)",
            reply_markup=None,
            parse_mode="Markdown"
        )
    except Exception as e:
        await callback.answer("❌ Mijozga xabar yuborib bo'lmadi.")

async def main():
    port = int(os.environ.get("PORT", 10000))
    server = await asyncio.start_server(lambda r, w: None, '0.0.0.0', port)
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
            
