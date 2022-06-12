from .StateUsers import OrderMessAdmin
from aiogram import types
from aiogram.dispatcher import FSMContext
from config import dp, db
from datetime import datetime
from aiogram.dispatcher.filters import Text


actions_for_admin=["Добавить новый заказ", "Заказы"]
drivers=[]
orders=[]

@dp.message_handler(Text(equals="Назад", ignore_case=True), state=OrderMessAdmin.wait_show_command)
@dp.message_handler(Text(equals="Меню", ignore_case=True), state=OrderMessAdmin.wait_show_command)
async def show_command_Admin(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for act in actions_for_admin:
        keyboard.add(types.KeyboardButton(act))
    await message.answer("Выбирете из следующего списка команд:", reply_markup=keyboard)
    await OrderMessAdmin.wait_choose_command.set()

@dp.message_handler(content_types=types.ContentTypes.TEXT, state=OrderMessAdmin.wait_choose_command)
async def choose_command_Admin(message: types.Message):
    if message.text not in actions_for_admin:
        await message.reply("Пожалуйста, выберите используя клавиатуру ниже.")
        return

    #"Добавить заказ"
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    if message.text == actions_for_admin[0]:
        keyboard.add(types.KeyboardButton("Назад в Меню"))
        await message.answer("Добавьте адресс:", reply_markup=keyboard)
        await OrderMessAdmin.wait_address.set()

    #"Заказы"
    elif message.text == actions_for_admin[1]:
        orders.extend(db.get_orders())
        for order in orders:
            keyboard.add(types.KeyboardButton(order[0]))
        keyboard.add(types.KeyboardButton("Назад в Меню"))
        await message.answer("Все заказы (" + str(len(orders)) + "):", reply_markup=keyboard)
        for order in orders:
            if order=="неподтверждён":
                await message.answer(str(order[0]) + "  " + order[4] + "  " + "неподтвержден", reply_markup=keyboard)
            else:
                await message.answer(str(order[0]) + "  " + order[4] + "  " + order[6], reply_markup=keyboard)
        await OrderMessAdmin.wait_properties_order.set()


#"добавить новый заказ"
@dp.message_handler(content_types=types.ContentTypes.TEXT, state=OrderMessAdmin.wait_address)
async def address(message: types.Message, state: FSMContext):
    #проверка на адрсс
    await state.update_data(address=message.text)

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(types.KeyboardButton("Отмена"))
    await message.answer("Укажите номер телефона(без +):", reply_markup=keyboard)
    await OrderMessAdmin.wait_phone_number.set()

@dp.message_handler(lambda message: not message.text.isdigit(), state=OrderMessAdmin.wait_phone_number)
async def phone_number(message: types.Message):
    return await message.reply("Введите номеер телефона без '+'")

@dp.message_handler(lambda message: message.text.isdigit(), state=OrderMessAdmin.wait_phone_number)
async def phone_number(message: types.Message, state: FSMContext):
    if not len(str(message.text))== 11:
        await message.reply("Пожалуйста, введите 11 чисел без +.")
        return
    await state.update_data(phone_number=int(message.text))
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(types.KeyboardButton("500"))
    keyboard.add(types.KeyboardButton("450"))
    keyboard.add(types.KeyboardButton("400"))
    keyboard.add(types.KeyboardButton("Отменить заказ"))
    keyboard.add(types.KeyboardButton("Назад"))
    await message.answer("Укажите цену заказа (Руб), указав только число:", reply_markup=keyboard)
    await OrderMessAdmin.wait_price.set()

@dp.message_handler(lambda message: message.text.isdigit(), state=OrderMessAdmin.wait_price)
async def price(message: types.Message, state: FSMContext):
    await state.update_data(price=message.text)
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(types.KeyboardButton("Автоматический выбор"))
    drivers.extend(db.get_drivers())  # имена и id водителей
    for driver in drivers:
        keyboard.add(types.KeyboardButton(driver[1]))
    keyboard.add(types.KeyboardButton("Отменить"))
    await message.answer("Укажите водителя(по желанию)", reply_markup=keyboard)
    await OrderMessAdmin.wait_driver.set()

@dp.message_handler(content_types=types.ContentTypes.TEXT, state=OrderMessAdmin.wait_driver)
async def driver(message: types.Message, state: FSMContext):
    name_drivers = [str(x[1]) for x in drivers]  # имена водителей
    if message.text not in name_drivers and not message.text == "Автоматический выбор":  # сравниваем ответ с именами водителей
        await message.reply("Пожалуйста, выберите используя клавиатуру ниже.")
        return

    if message.text == "Автоматический выбор":
        # cдесь выбираем если автоматический выбор с функцияй определения водителя
        await state.update_data(driver=message.text)  # сохраняем имя водителя
        index_name_drivers = name_drivers.index(message.text)
        await state.update_data(driver_id=drivers[index_name_drivers][0])  # сохраняем id водителя
    else:
        await state.update_data(driver=message.text)  # сохраняем имя водителя
        index_name_drivers = name_drivers.index(message.text)
        await state.update_data(driver_id=drivers[index_name_drivers][0])  # сохраняем id водителя
    drivers.clear()

    user_data = await state.get_data()
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(types.KeyboardButton("Сохранить заказ"))
    keyboard.add(types.KeyboardButton("Отмена"))
    await message.answer(f"Вы заказали машину на адресс: {user_data['address']}\n"
                         f"Номер телефона: {user_data['phone_number']}\n"
                         f"Цена: {user_data['price']}\n"
                         f"Водитель: {user_data['driver']}\n"
                         ,reply_markup=keyboard)
    await OrderMessAdmin.wait_ready.set()

@dp.message_handler(Text(equals="Сохранить заказ", ignore_case=True), state=OrderMessAdmin.wait_ready)
async def ready(message: types.Message, state: FSMContext):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(types.KeyboardButton("Меню"))
    user_data = await state.get_data()
    db.add_order(message.from_user.id, message.from_user.full_name, user_data['phone_number'], user_data['address'], user_data['price'], user_data['driver'], user_data['driver_id'], datetime.utcnow())
    await message.answer(f"Вы успешно сделали заказ", reply_markup=keyboard)
    await OrderMessAdmin.wait_show_command.set()











@dp.message_handler(lambda message: not message.text.isdigit(), state=OrderMessAdmin.wait_properties_order)
async def properties_order(message: types.Message):
    return await message.reply("Введите номеер заказ  '+'")

@dp.message_handler(lambda message: message.text.isdigit(), state=OrderMessAdmin.wait_phone_number)
async def phone_number(message: types.Message, state: FSMContext):
    if not len(str(message.text))== 11:
        await message.reply("Пожалуйста, введите 11 чисел без +.")
        return
    await state.update_data(phone_number=int(message.text))
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(types.KeyboardButton("500"))
    keyboard.add(types.KeyboardButton("450"))
    keyboard.add(types.KeyboardButton("400"))
    keyboard.add(types.KeyboardButton("Отменить заказ"))
    keyboard.add(types.KeyboardButton("Назад"))
    await message.answer("Укажите цену заказа (Руб), указав только число:", reply_markup=keyboard)
    await OrderMessAdmin.wait_price.set()

@dp.message_handler(content_types=types.ContentTypes.TEXT, state=OrderMessAdmin.wait_confirm_order)
async def confirm_order_Admin(message: types.Message, state: FSMContext):

    id_orders = [str(x[0]) for x in unconfirmed_orders] #получаем id всех заказов
    if message.text not in id_orders:
        await message.reply("Пожалуйста, выберите используя клавиатуру ниже.")
        return

    await state.update_data(id_order=message.text)
    index_id_order = id_orders.index(message.text) #получаем индекс id нашего заказа
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(types.KeyboardButton("Продолжить подтверждение заказа"))
    keyboard.add(types.KeyboardButton("Отменить заказ"))
    keyboard.add(types.KeyboardButton("Назад"))
    await message.answer("Перезвоните клиенту и уточните все детали, если клиента что-то не устраивает, то отмените заказ:\n" +
                        unconfirmed_orders[index_id_order][1] + " " + unconfirmed_orders[index_id_order][2]
                         , reply_markup=keyboard)
    await OrderMessAdmin.wait_confirm_complite.set()

@dp.message_handler(Text(equals="Продолжить подтверждение заказа", ignore_case=True), state=OrderMessAdmin.wait_confirm_complite)
async def confirm_complite_Admin(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(types.KeyboardButton("500"))
    keyboard.add(types.KeyboardButton("450"))
    keyboard.add(types.KeyboardButton("400"))
    keyboard.add(types.KeyboardButton("Отменить заказ"))
    keyboard.add(types.KeyboardButton("Назад"))
    await message.answer("Укажите цену заказа:", reply_markup=keyboard)
    await OrderMessAdmin.wait_confirm_price.set()

@dp.message_handler(content_types=types.ContentTypes.TEXT, state=OrderMessAdmin.wait_confirm_price)
async def confirm_price_Admin(message: types.Message, state: FSMContext):
    # сюда проверка на цену того что она в виде числа
    await state.update_data(price=message.text)

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(types.KeyboardButton("Автоматический выбор"))
    drivers.extend(db.get_drivers())    #имена и id водителей
    for driver in drivers:
        keyboard.add(types.KeyboardButton(driver[1]))
    keyboard.add(types.KeyboardButton("Отменить заказ"))
    keyboard.add(types.KeyboardButton("Назад"))
    await message.answer("Укажите водителя(по желанию)", reply_markup=keyboard)
    await OrderMessAdmin.wait_confirm_driver.set()

@dp.message_handler(content_types=types.ContentTypes.TEXT, state=OrderMessAdmin.wait_confirm_driver)
async def confirm_driver(message: types.Message, state: FSMContext):

    name_drivers = [str(x[1]) for x in drivers] #имена водителей

    if message.text not in name_drivers and not message.text == "Автоматический выбор":  #сравниваем ответ с именами водителей
        await message.reply("Пожалуйста, выберите используя клавиатуру ниже.")
        return

    if message.text == "Автоматический выбор":
        #cдесь выбираем если автоматический выбор с функцияй определения водителя
        await state.update_data(driver=message.text)                       #сохраняем имя водителя
        index_name_drivers = name_drivers.index(message.text)
        await state.update_data(driver_id=drivers[index_name_drivers][0])  #сохраняем id водителя
    else:
        await state.update_data(driver=message.text)                       #сохраняем имя водителя
        index_name_drivers = name_drivers.index(message.text)
        await state.update_data(driver_id=drivers[index_name_drivers][0])  #сохраняем id водителя
    drivers.clear()

    user_data = await state.get_data()
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(types.KeyboardButton("Сохранить заказ"))
    keyboard.add(types.KeyboardButton("Назад"))
    await message.answer(f"Вы подтвердили заказ на адресс: {user_data['address']}\n"
                         f"Номер телефона: {user_data['tel_num']}\n"
                         f"Цена: {user_data['price']}\n"
                         f"Водитель: {user_data['driver']}.\n"
                         ,reply_markup=keyboard)
    await OrderMessAdmin.wait_ready.set()





