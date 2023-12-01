import data
import pyodbc
from datetime import date
from telebot import types
import re

user_data = {}

admins_data = {}

bot = data.bot_token

conn_str = data.sql
conn = pyodbc.connect(conn_str)
cursor = conn.cursor()


def get_access(user_id):
    cursor.execute('Select User_group_id from Users where UserId = ?', (user_id))
    result = cursor.fetchone()
    return result


def get_admins():
    cursor.execute(data.query_get_admins)
    rec = cursor.fetchall()
    for row in rec:
        username = row[0]

        admins_data[id] = {
            'username': username
        }

    for key in admins_data:
        data.admins += f"{admins_data[key]['username']} "

def main(commands=['start']):

    def check_full_name(full_name):
        # Определите регулярное выражение для проверки ФИО
        pattern = r'^[А-ЯЁ][а-яё]+ [А-ЯЁ][а-яё]+( [А-ЯЁ][а-яё]+)?$'

        # Используйте функцию search() модуля re для проверки соответствия
        if re.match(pattern, full_name):
            return True
        else:
            return False

    @bot.message_handler()
    # Сохранение ФИО, получение соц.сети
    def save_full_name(message):
        if data.status == True:
            chat_id = message.chat.id
            full_name = message.text
            # Проверяем, соответствует ли ФИО формату
            if not check_full_name(full_name):
                markup = types.InlineKeyboardMarkup()
                markup.add(types.InlineKeyboardButton('Главное меню', callback_data='start_menu'))
                bot.send_message(chat_id, "Неверный формат ФИО. Пожалуйста, введите ФИО в формате 'Иванов Иван Иванович' или без отчества:", reply_markup=markup)
                bot.register_next_step_handler(message, save_full_name)  # Рекурсивно вызываем функцию для повторного ввода ФИО
                return
                
            user_data[chat_id] = {"full_name": full_name}
            user_id = message.from_user.id
            user_data[chat_id]["user_id"] = user_id 
            user_name = message.from_user.username
            user_data[chat_id]["user_name"] = user_name
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton('Главное меню', callback_data='start_menu'))
            bot.send_message(chat_id, "Отлично! Теперь введите ссылку на соц.сеть:", reply_markup=markup)
            data.status = False
            bot.register_next_step_handler(message, save_network)
            return

    # Сохранение ссылки на соц.сеть, получение города
    def save_network(message):
        data.status = True
        if data.status == True:
            chat_id = message.chat.id
            social_networks = message.text
            user_data[chat_id]["social_networks"] = social_networks
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton('Главное меню', callback_data='start_menu'))
            bot.send_message(chat_id, "Пожалуйста, введите номер телефона:", reply_markup=markup)
            bot.register_next_step_handler(message, save_phone)
            data.status = False
            return

    # Функция сохранения номера телефона
    def save_phone(message):
        data.status = True
        if data.status == True:
            chat_id = message.chat.id
            phone_number = message.text
            user_data[chat_id]["phone_number"] = phone_number
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton('Главное меню', callback_data='start_menu'))
            bot.send_message(chat_id, "Пожалуйста, введите город для работы:", reply_markup=markup)
            bot.register_next_step_handler(message, save_city)
            data.status = False
            return

    # Функция сохранение города и отправка данных на обработку
    def save_city(message):
        data.status = True
        if data.status == True:
            try:
                chat_id = message.chat.id
                user_data[chat_id]["city"] = message.text
                markup = types.InlineKeyboardMarkup()
                markup.add(types.InlineKeyboardButton('Главное меню', callback_data='start_menu'))
                yes = types.InlineKeyboardButton('Да', callback_data='send_data')
                no = types.InlineKeyboardButton('Нет', callback_data='not_send_data')
                markup.row(yes, no)
                bot.send_message(chat_id, "Отправить все полученные данные на обработку?", reply_markup=markup)
                data.status = False
            except:
                bot.send_message(message.chat_id, "Пожалуйста, выберите кнопку из меню.")
            return

    # Функция для сохранения номера телефона и отправки данных в чат
    def send_data(chat_id):
            full_name = user_data[chat_id]["full_name"]
            social_networks = user_data[chat_id]["social_networks"]
            city = user_data[chat_id]["city"]
            phone_number = user_data[chat_id]["phone_number"]
            user_id = user_data[chat_id]["user_id"]
            user_name = user_data[chat_id]["user_name"]
            current_date = date.today()
            full_data = f"ФИО: {full_name}\nСсылка на соц.сеть: {social_networks}\nГород: {city}\nДата регистрации по ссылке: {current_date} "
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton('Главное меню', callback_data='start_menu'))
            bot.send_message(data.chat_id, full_data)
            bot.send_message(chat_id, "Ответ записан.", reply_markup=markup)
            cursor.execute(data.query_add, (full_name, social_networks, city, phone_number, user_id, user_name ))
            cursor.commit()
            return


    @bot.callback_query_handler(func=lambda callback: True)

    def callback_message(callback):

        # Если выбрано "Регистрация пользователя, получаем его ФИО"
        if callback.data == "reg_user":
            data.status = True
            chat_id = callback.message.chat.id
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton('Главное меню', callback_data='start_menu'))
            bot.send_message(chat_id, "Пожалуйста, введите ФИО:", reply_markup=markup)
            bot.register_next_step_handler(callback.message, save_full_name)
            
        # Если выбрано "Регистрация воркера", получаем его данные(?)
        elif callback.data == "reg_work":
            data.status = False
            chat_id = callback.message.chat.id
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton('Главное меню', callback_data='start_menu'))
            access = get_access(callback.message.chat.id)
            if access[0] == '2':
                    bot.send_message(chat_id, "Функция в разработке" , reply_markup=markup)
            elif access[0] == '1':
                    bot.send_message(chat_id, "Обратитесь к администраторам для регистрации нового воркера:", reply_markup=markup)
                    get_admins()
                    bot.send_message(chat_id, data.admins)
            else:
                    bot.send_message(chat_id, "У вас недостаточно полномочий !", reply_markup=markup)

        # Если пользователь нажал "Главное меню"
        elif callback.data == "start_menu":
            try:
                data.status = False
                bot.clear_step_handler_by_chat_id(chat_id = callback.message.chat.id)
                markup = types.InlineKeyboardMarkup()
                markup.add(types.InlineKeyboardButton('Регистрация пользователя', callback_data='reg_user'))
                markup.add(types.InlineKeyboardButton('Регистрация воркера', callback_data="reg_work"))
                bot.send_message(callback.message.chat.id, 'Выберите тему вопроса в меню:', reply_markup=markup)
            except:
                bot.send_message(callback.message.chat.id, "Пожалуйста, выберите кнопку из меню.")
            return

        # Если пользователь согласился отправить данные на проверку
        elif callback.data == "send_data":
            chat_id = callback.message.chat.id
            send_data(chat_id)

        # Если пользователь отказался от отправки данных на проверку
        elif callback.data == "not_send_data":
            chat_id = callback.message.chat.id
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton('Главное меню', callback_data='start_menu'))
            bot.send_message(chat_id, "Данные не будут отправлены.", reply_markup=markup)