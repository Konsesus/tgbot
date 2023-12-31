import telebot

# API для бота
bot_token = telebot.TeleBot('')


# Данные для подключения к локальной БД
sql = (
    r'DRIVER={ODBC Driver 17 for SQL Server};'
    r'SERVER=(local)\SQLEXPRESS;'
    r'DATABASE=Python_Bot;'
    r'Trusted_Connection=yes;'
)
# Куда будут отправляться данные после регистрации пользователя
id_chat = ''

# Запрос SQL для записи данных в БД
query_add_user = '''
Insert Users(
FullName, 
SocialNetworkLink,
City,
Phone,
UserId,
Username
)
Values (?,?,?,?,?,?)
'''

query_add_worker = '''
insert Users(
FullName,
SocialNetworkLink
)
Values(?,?)
'''

query_get_access = '''
Select
User_group_id
from Users
where
UserId = ?
'''

query_get_admins = '''
select
SocialNetworkLink
from Users
where User_group_id = 2
'''

query_get_all_users = '''
select * 
from Users
where 
User_group_id = 0
'''

global admins
admins = ""

global status
status = True
