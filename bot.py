import logging
import asyncio
from aiogram import Bot, Dispatcher, Router, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.filters import CommandStart

# --- SOZLAMALAR ---
BOT_TOKEN = "8893476065:AAFseE8gnPCvfV_GALln-PCvK-tz7Wihn40"
ADMIN_ID = 1678146043 
CHANNEL_ID = "-1001908315496"

logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)
router = Router()

class OrderStates(StatesGroup):
    waiting_receipt = State()
    waiting_proposal = State()

def get_main_kb(user_id):
    kb_list = [
        [KeyboardButton(text="🛒 Android Coins"), KeyboardButton(text="🌍 Regionlar uchun Coins")],
        [KeyboardButton(text="🏆 Turnir"), KeyboardButton(text="🎁 Bonuslarim")],
        [KeyboardButton(text="📖 Qo'llanma"), KeyboardButton(text="📦 Mening buyurtmalarim")],
        [KeyboardButton(text="⭐ Sharhlar"), KeyboardButton(text="✍️ Taklif qoldirish")],
        [KeyboardButton(text="👨‍💻 Admin / Yordam")]
    ]
    if user_id == ADMIN_ID:
        kb_list.append([KeyboardButton(text="🛠 Admin Panel")])
    return ReplyKeyboardMarkup(keyboard=kb_list, resize_keyboard=True)

# --- START ---
@router.message(CommandStart())
async def start_cmd(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Assalomu alaykum!", reply_markup=get_main_kb(message.from_user.id))

# --- HANDLERLAR (argumentlar aniq yozildi) ---
@router.message(F.text == "🛒 Android Coins")
async def shop_android(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Android paketini tanlang (test):", 
                         reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="260 coins - 40000", callback_data="pkg_android_260")]]))

@router.message(F.text == "🌍 Regionlar uchun Coins")
async def shop_region(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Regionni tanlang:", 
                         reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Япония", callback_data="reg_yapon")]]))

@router.callback_query(F.data.startswith("reg_"))
async def choose_reg(callback: CallbackQuery, state: FSMContext):
    await state.update_data(region=callback.data)
    await callback.message.answer("Paket tanlang:", 
                                  reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="578 coins - 70000", callback_data="pkg_region_578")]]))

@router.callback_query(F.data.startswith("pkg_"))
async def order_start(callback: CallbackQuery, state: FSMContext):
    await state.set_state(OrderStates.waiting_receipt)
    await callback.message.answer("Chekni rasm sifatida yuboring:")

@router.message(OrderStates.waiting_receipt, F.photo)
async def get_receipt(message: Message, state: FSMContext):
    await bot.send_message(ADMIN_ID, "Yangi buyurtma keldi!")
    await message.answer("✅ Chek qabul qilindi.", reply_markup=get_main_kb(message.from_user.id))
    await state.clear()

@router.message(F.text == "✍️ Taklif qoldirish")
async def prop_start(message: Message, state: FSMContext):
    await state.clear()
    await state.set_state(OrderStates.waiting_proposal)
    await message.answer("Taklifingizni yozing:")

@router.message(OrderStates.waiting_proposal)
async def get_prop(message: Message, state: FSMContext):
    await bot.send_message(ADMIN_ID, f"💡 Taklif: {message.text}")
    await message.answer("Rahmat!", reply_markup=get_main_kb(message.from_user.id))
    await state.clear()

# Boshqa tugmalar uchun
@router.message(F.text.in_(["🏆 Turnir", "🎁 Bonuslarim", "📖 Qo'llanma", "📦 Mening buyurtmalarim", "⭐ Sharhlar", "👨‍💻 Admin / Yordam", "🛠 Admin Panel"]))
async def other_stuff(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Bu bo'lim ustida ishlanmoqda.")

async def main():
    dp.include_router(router)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
    
