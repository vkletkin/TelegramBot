from aiogram.dispatcher.filters.state import State, StatesGroup

class OrderMessAdmin(StatesGroup):
    #состояния списка и выбора команд
    wait_show_command = State()
    wait_choose_command = State()

    #Команда "Добавить заказ"
    wait_address = State()
    wait_phone_number = State()
    wait_price = State()
    wait_driver = State()
    wait_ready = State()
    wait_confirm_order = State()
    wait_confirm_complite = State()

    # Команда "Подтвердить клиентский заказ"
    wait_confirm_driver= State()
    wait_confirm_price= State()

    # "Посмотреть невыполненые заказы"


class OrderMessDriver(StatesGroup):
    # состояния списка и выбора команд
    wait_show_command = State()
    wait_choose_command = State()

    wait_add_order = State()
    wait_new_address = State()
    wait_new_tel_num = State()
    wait_new_price = State()
    wait_new_driver = State()
    wait_new_ready = State()

class OrderMessClient(StatesGroup):
    wait_show_command = State()
    wait_choose_command = State()

    # Команда "Добавить заказ"
    wait_address = State()
    wait_tel_num = State()
    wait_volume = State()
    wait_driver = State()
    wait_ready = State()
