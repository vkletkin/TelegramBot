from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from config import dp, db, bot
from datetime import datetime
from .StateUsers import OrderMessAdmin, OrderMessDriver, OrderMessClient


@dp.message_handler(commands="cancel", state="*")
@dp.message_handler(Text(equals="отмена", ignore_case=True), state="*")
async def cmd_cancel(message: types.Message, state: FSMContext):
    # Сбрасываем текущее состояние пользователя и сохранённые о нём данные
    await state.finish()
    await message.answer("Действие отменено", reply_markup=types.ReplyKeyboardRemove())

@dp.message_handler(commands=["start"], state="*")
@dp.message_handler(Text(equals="старт", ignore_case=True), state="*")
async def cmd_start(message: types.Message, state: FSMContext):
    type_user = db.get_type_user(message.from_user.id)
    if (type_user == "admin"):
        # если пользователь администратор
        await OrderMessAdmin.wait_show_command.set()
    elif (type_user == "driver"):
        # если пользователь водитель
        await OrderMessDriver.wait_show_command.set()
    elif (type_user == "client"):
        # если пользователь клиент
        await OrderMessClient.wait_show_command.set()
    else:
        # если пользователь первый раз
        db.add_client(message.from_user.id, message.from_user.full_name, datetime.utcnow())
        await OrderMessClient.wait_show_command.set()

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(types.KeyboardButton("Меню"))
    await message.answer("👋 Приветсвую Вас," + str(message.from_user.full_name) + "\n" 
                         "Я бот ОТКАЧАЙКА приму любые ваши пожелания и сделаю все неообходимое, чтобы откачать вашу яму),"
                         , reply_markup=keyboard)


@dp.message_handler(commands="set_commands", state="*")
async def cmd_set_commands(message: types.Message):
    if message.from_user.id == 877916659:  # Подставьте сюда свой Telegram ID
        commands = [types.BotCommand(command="/drinks", description="Заказать напитки"),
                    types.BotCommand(command="/food", description="Заказать блюда")]
        await bot.set_my_commands(commands)
        await message.answer("Команды настроены.")
