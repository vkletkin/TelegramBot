from .StateUsers import OrderMessClient
from aiogram import types
from aiogram.dispatcher import FSMContext
from config import dp, db
from datetime import datetime
from aiogram.dispatcher.filters import Text

actions_for_clietn = ["Заказать откачку ямы", "Скидки и акции", "Связаться с нами", "О нас"]

@dp.message_handler(Text(equals="Назад", ignore_case=True), state=OrderMessClient.wait_show_command)
@dp.message_handler(Text(equals="Меню", ignore_case=True), state=OrderMessClient.wait_show_command)
async def show_command_Clietn(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for act in actions_for_clietn:
        keyboard.add(types.KeyboardButton(act))
    keyboard.add(types.KeyboardButton("Отмена"))
    await message.answer("Выбирете что хотите выбрать:", reply_markup=keyboard)
    await OrderMessClient.wait_choose_command.set()

@dp.message_handler(content_types=types.ContentTypes.TEXT, state=OrderMessClient.wait_choose_command)
async def choose_command_Clietn(message: types.Message):

    if message.text not in actions_for_clietn:
        await message.reply("Пожалуйста, выберите используя клавиатуру ниже.")
        return

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    if message.text == actions_for_clietn[0]:
        #keyboard.add(types.KeyboardButton('Отправить своё местоположение 🗺️', request_location=True))
        keyboard.add(types.KeyboardButton("Отмена"))
        await message.answer("Напишите адресс", reply_markup=keyboard)
        await OrderMessClient.wait_address.set()

    elif message.text == actions_for_clietn[1]:
        keyboard.add(types.KeyboardButton("Назад"))
        await message.answer("Здесь информация о скидках и акциях", reply_markup=keyboard)
        await OrderMessClient.wait_show_command.set()

    elif message.text == actions_for_clietn[2]:
        keyboard.add(types.KeyboardButton("Назад"))
        await message.answer("Здесь информация о связаться с нами:", reply_markup=keyboard)
        await OrderMessClient.wait_show_command.set()

    elif message.text == actions_for_clietn[3]:
        keyboard.add(types.KeyboardButton("Назад"))
        await message.answer("Здесь информация о О нас:", reply_markup=keyboard)
        await OrderMessClient.wait_show_command.set()

@dp.message_handler(content_types=types.ContentTypes.TEXT, state=OrderMessClient.wait_address)
@dp.message_handler(content_types=types.ContentTypes.LOCATION, state=OrderMessClient.wait_address)
async def address_Client(message: types.Message, state: FSMContext):
    # проверка адреса
    if message.content_type == "text":
        await state.update_data(address=message.text)
    else:
        await state.update_data(address=message.location.lo)



    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(types.KeyboardButton('Отправить свой контакт ☎️', request_contact=True))
    keyboard.add(types.KeyboardButton("Отмена"))

    await message.answer("Напишите номер телефона или подеилитесь нажав ниже:", reply_markup=keyboard)
    await OrderMessClient.wait_tel_num.set()

@dp.message_handler(content_types=types.ContentTypes.TEXT, state=OrderMessClient.wait_tel_num)
@dp.message_handler(content_types=types.ContentTypes.CONTACT, state=OrderMessClient.wait_tel_num)
async def tel_num_Client(message: types.Message, state: FSMContext):

    if message.content_type == "text":
        #cдесь можно еще проверку  на телефон
        await state.update_data(tel_num=message.text)
    else:
        await state.update_data(tel_num=message.contact.phone_number)

    user_data = await state.get_data()
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(types.KeyboardButton("Сохранить заказ"))
    keyboard.add(types.KeyboardButton("Отмена"))
    await message.answer(f"Вы заказали машину \n"
                         f"Адрес: {user_data['address']}\n"
                         f"Номер телефона: {user_data['tel_num']}\n"
                         f"Имя: " + message.from_user.full_name
                         , reply_markup=keyboard)
    await OrderMessClient.wait_ready.set()

@dp.message_handler(Text(equals="Сохранить заказ", ignore_case=True), state=OrderMessClient.wait_ready)
async def ready_Client(message: types.Message, state: FSMContext):

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(types.KeyboardButton("Команды"))
    user_data = await state.get_data()
    #ниже функция при подтверждения заказа
    db.add_order_Client(message.from_user.id, datetime.utcnow(), user_data['address'], message.from_user.full_name, user_data['tel_num'])
    await message.answer(f"Вы успешно сделали заказ, наш консультант перезвонит вам", reply_markup=keyboard)
    await state.finish()
    await OrderMessClient.wait_show_command.set()