import sqlite3

class SQLighter:

    def __init__(self, database):
        """Подключаемся к БД и сохраняем курсор соединения"""
        self.connection = sqlite3.connect(database)
        self.cursor = self.connection.cursor()

    def close(self):
        """Закрываем соединение с БД"""
        self.connection.close()

    def get_type_user(self, user_id):
        """Проверка типа юзера"""
        with self.connection:
            result = self.cursor.execute('SELECT `type_user` FROM `users` WHERE `user_id` = ?', (user_id,)).fetchone()
            if result is None:
                return "None"
            else:
                return result[0]

    def add_client(self, user_id, name, datatime_subscription, type_user="client"):
        """Добавляем нового клиента"""
        with self.connection:
            return self.cursor.execute(
                "INSERT INTO `users` (`user_id`, `name`, `datatime_subscription`, `type_user`) VALUES(?,?,?,?)",
                (user_id, name, datatime_subscription, type_user))

    def add_order(self, user_id, name, phone_number, address, price, driver, driver_id, data_time_start, status = "выполняется"):
        """Добавляем нового заказа"""
        with self.connection:
           return self.cursor.execute("INSERT INTO `orders` (`user_id`, `name`, `phone_number`, `address`, `price`, `driver`, `driver_id`, `data_time_start`,`status`) VALUES(?,?,?,?,?,?,?,?,?)",
                                      (user_id, name, phone_number, address, price, driver, driver_id, data_time_start, status))

    def get_orders(self, status1="неподтверждён",status2="неподтверждён"):
        """Получаем все заказы """
        with self.connection:
            return self.cursor.execute('SELECT * FROM `orders` WHERE `status` = ? OR `status` = ?', (status1, status2)).fetchall()


    def get_unexecuted_orders(self, status="выполняется"):
        """Получаем все невыполненные заказы"""
        with self.connection:
            return self.cursor.execute('SELECT `id`, `name`, `phone_number`, `address`, `driver` FROM `orders` WHERE `status` = ?', (status,)).fetchall()


    def get_drivers(self, type_user="driver"):
        """Получаем всех водителей"""
        with self.connection:
            return self.cursor.execute("SELECT `user_id`, `name` FROM `users` WHERE `type_user` = ?", (type_user,)).fetchall()






    def add_order_Client(self, user_id, data_time_start, address, name, tel_number):
        """Добавляем нового заказа"""
        with self.connection:
            return self.cursor.execute("INSERT INTO `orders` (`user_id`, `data_time_start`, `address`, `name`, `tel_number`) VALUES(?,?,?,?,?)",
                                       (user_id, data_time_start, address, name, tel_number))


    def update_status(self, id, status=True):
        """Обновляем статус выполнения заказа"""
        with self.connection:
            return self.cursor.execute("UPDATE `orders` SET `status` = ? WHERE `id` = ?", (status, id))

