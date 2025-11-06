import telebot
if __name__ == '__main__':
    from indexWeb import webside
from schoolsXpathes import schools
from dbmanager import *
from datetime import datetime
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from threading import Thread
import time
import dotenv
import string
import sys
import traceback
import qrcode
from io import BytesIO

donate_link = 'https://dalink.to/medisssa'

if not os.path.exists("./log.txt"):
    with open("./log.txt", "a") as log:
        log.write(
            'LOG')
if not os.path.exists("./db/info.db"):
    makeDb()
menuText = 'Вы в главном меню!\nТут есть все , что вам нужно.'
FriendRegistration = {

}
daysOfWeek = {
    "rus" : ['понедельник' , "вторник" , "среда" , "четверг" , "пятница" , "суббота"] ,
    "eng" : ["monday" , "tuesday" , "wednesday" , "thursday" , "friday" , "saturday"]
    }

checkFrequency = 10 #проверка/минуты
messagesToDelete = []


token = dotenv.dotenv_values('.env').get('TOKEN')
loggerChat = dotenv.dotenv_values('.env').get('LOG_GROUP')
friendsCount = dotenv.dotenv_values('.env').get('MAX_FRIENDS')
admins = dotenv.dotenv_values('.env').get('ADMINSIDS')


menulayout = {"Профиль" : 'profile' ,
              "Друзья" : 'friends' ,
              "Расписание": 'schedule' ,
                }
profileLayout = {
    "Отписаться от рассылки:" : 'unsub'

}
bot = telebot.TeleBot(token= token)
#id username course school group sub
def save_log(ex , id):
    try:
        with open("./log.txt", "a" , encoding= 'utf-8') as log:
            log.write(f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n{id}\n{ex}\n')
    except Exception as e:
        print(e)
def send_to_logger(ex , id = 0 , isntanexeption = False , justInfo = False):
    try:
        if justInfo:
            text =  f'{ex}' if id == 0 else f'{id}\n{ex}'
            bot.send_message(chat_id=loggerChat, text=text)
            return
        if id == 0:
            message = f'Произошла ошибка :{ex}'
        else:
            message = f'У пользователя {id} произошла ошибка :  {ex}'
        if not isntanexeption:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            tb_list = traceback.extract_tb(exc_traceback)
            last_frame = tb_list[-1]
            file_name = last_frame.filename
            line_number = last_frame.lineno
            function_name = last_frame.name
            message = f'{message}\nОшибка {exc_type.__name__}\nНа строке {line_number} ,в функции {function_name} файла {file_name} '
        bot.send_message(chat_id = loggerChat, text=f'{message}')
        save_log(message, id)
    except Exception as e:
        save_log(ex, id)
def makeMarkupWithLayout(layout:dict):
    try:
        markup = InlineKeyboardMarkup()
        markup.row_width = 2
        for i in layout:
            markup.add(InlineKeyboardButton(i, callback_data=f"{menulayout[i]}"))
        return markup
    except Exception as e:
        send_to_logger(e)
def generateMenu(id):
    try:
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton('Расписание на сегодня' , callback_data='schedule_today'))
        profileb = InlineKeyboardButton(text="Профиль", callback_data="profile")
        friendsb = InlineKeyboardButton(text="Друзья", callback_data="friends")
        markup.row(profileb , friendsb)
        markup.add(InlineKeyboardButton("Расписание" , callback_data="schedule"))
        if str(id) in admins:
            markup.add(InlineKeyboardButton('Админское меню' , callback_data="adminMenu"))
        markup.add(InlineKeyboardButton('Больше информации о проекте' , callback_data="extra_info"))
        return markup
    except Exception as e:
        send_to_logger(e , id)
def findUsersWithTheSameSchedule(users) -> dict:
    try:
        groupsandUsers = {}
        for i in range(len(users)):
            if f'{str(users[i][2])}_{users[i][3]}_{users[i][4].upper()}' not in groupsandUsers.keys():
                groupsandUsers[f'{str(users[i][2])}_{users[i][3]}_{users[i][4].upper()}'] = [users[i][0]]
            else:
                groupsandUsers[f'{str(users[i][2])}_{users[i][3]}_{users[i][4].upper()}'].append(users[i][0])
        return groupsandUsers
    except Exception as e:
        send_to_logger(e)

def telegramSide():
    messages = {
        "greeting": 'Привет'
    }

    s = ["Бизнес-школа" , "ИШИнЭс" , "ИШИТР" , "ИШНКБ" , "ИШНПТ" , "ИШПР" , 
            "ИШЭ" , "ИЯТШ" , "ИШФВП" , "ИШХБМТ" , 'УН' , "УОД" , "ШОН"]

    user_data = {}
    def gen_profile_markup(id):
        try:
            markup = InlineKeyboardMarkup()
            markup.row_width = 3
            sub = checkUserSub(id)
            if sub:
                markup.add(InlineKeyboardButton("Отписаться от рассылки", callback_data=f"unsub"))
            else:
                markup.add(InlineKeyboardButton("Подписаться на рассылку", callback_data=f"sub"))
            markup.add(InlineKeyboardButton("Вернуться в меню" , callback_data= "menu"))
            markup.add(InlineKeyboardButton("Удалить это сообщение" , callback_data = 'None'))
            return markup , sub
        except Exception as e:
            send_to_logger(e , id)
    def gen_course_markup(id , is_for_friend = False):
        try:
            markup = InlineKeyboardMarkup()
            if not is_for_friend:
                markup.row_width = 3
                markup.add(
                    InlineKeyboardButton("1 курс", callback_data="course_1"),
                    InlineKeyboardButton("2 курс", callback_data="course_2"),
                    InlineKeyboardButton("3 курс", callback_data="course_3"),
                    InlineKeyboardButton("4 курс", callback_data="course_4"),
                    InlineKeyboardButton("5 курс", callback_data="course_5"),
                    InlineKeyboardButton("6 курс", callback_data="course_6")
                )
            else:
                markup.row_width = 3
                markup.add(
                    InlineKeyboardButton("1 курс", callback_data="Fcourse_1"),
                    InlineKeyboardButton("2 курс", callback_data="Fcourse_2"),
                    InlineKeyboardButton("3 курс", callback_data="Fcourse_3"),
                    InlineKeyboardButton("4 курс", callback_data="Fcourse_4"),
                    InlineKeyboardButton("5 курс", callback_data="Fcourse_5"),
                    InlineKeyboardButton("6 курс", callback_data="Fcourse_6")
                )

            return markup
        except Exception as e:
            send_to_logger(e , id)
    def deleteMessages():
        try:
            for message in messagesToDelete:
                try:
                    id , chat_id = message.split(':')
                    bot.delete_message(chat_id=id , message_id=chat_id)
                except Exception as e:
                    pass
        except Exception as e:
            send_to_logger(e)
        del messagesToDelete[:]
    def manageMessages(id , messageId , isCom = False):
        try:
            # if id not in messagesToDelete.keys():
            #     messagesToDelete[id] = [messageId]
            # else:
            #     messagesToDelete[id] = messagesToDelete[id].append(messageId)
            messagesToDelete.append(f'{id}:{messageId}')
            if isCom:
                messagesToDelete.append(f'{id}:{messageId - 1}')
        except Exception as e:
            send_to_logger(e , id)
    def gen_friends_markup(id , isforDelete = False):
        markup = InlineKeyboardMarkup()
        markup.row_width = 2
        try:
            friends1 = getfriends(id)
            if isforDelete:
                for i , friends in enumerate(friends1):
                    markup.add(InlineKeyboardButton(f'{int(friends[-1]) + 1}.{friends[1]} , {friends[-2]}', callback_data=f"friend_delete_{id}_{friends[-1]}"))
            else:
                if not len(friends1) == 0:
                    for i , friends in enumerate(friends1):
                        markup.row_width = 1
                        markup.add(InlineKeyboardButton(f'{int(friends[-1]) + 1}.{friends[1]} , {friends[-2]}', callback_data=f"friend_{id}_{friends[-1]}"))
                    markup.add(InlineKeyboardButton("Удалить друга" , callback_data=f"friend_delete"))
                if len(friends1) <= int(friendsCount):
                    markup.add(InlineKeyboardButton("Добавить друга" , callback_data=f"friend_add"))
            markup.add(InlineKeyboardButton("Вернуться в меню" , callback_data=f"menu"))
            return markup , len(friends1)
        except Exception as e:
            send_to_logger(e , id)
    def gen_school_markup(isForFriend = False):
        try:
            markup = InlineKeyboardMarkup()
            markup.row_width = 2
            for i, school in enumerate(s):
                markup.add(InlineKeyboardButton(school, callback_data=f"{f"school_{i}" if not isForFriend else f'Fschool_{i}'}"))
            return markup
        except Exception as e:
            send_to_logger(e)

    def genWeekMarkup(forFriend = False , id = 0 , friend_index = 0):
        try:
            markup = InlineKeyboardMarkup()
            markup.row_width = 3
            now = datetime.now().weekday()
            for i, weekDay in enumerate(daysOfWeek["rus"]):
                if i == now:
                    weekDay += ' (Сегодня)'
                markup.add(InlineKeyboardButton(weekDay.capitalize() , callback_data=f"{f"weekDay_{i}" if not forFriend else f'FweekDay_{i}_{id}_{friend_index}'}"))
            markup.add(InlineKeyboardButton('Вернуться в меню' , callback_data=f"menu"))

            return markup
        except Exception as e:
            send_to_logger(e)

    @bot.message_handler(commands=['start' , 'registration'])
    def stop_handler(message):
        try:
            if isUserInDb(message.from_user.id):
                deleteUser(id = message.from_user.id)
            user_id = message.from_user.id
            user_data[user_id] = {"username": message.from_user.username}
            bot.send_message(message.chat.id, 'Выберите ваш курс:', reply_markup=gen_course_markup(message.from_user.id))
            manageMessages(id = message.from_user.id , messageId= message.id -1)
        except Exception as e:
            send_to_logger(e , message.from_user.id)



    @bot.message_handler(commands= ['week'])
    def weekHandler(message):
        try:
            manageMessages(id = message.from_user.id , messageId= message.id + 1)
            bot.send_message(message.from_user.id , "Выберите день недели:" , reply_markup= genWeekMarkup())
        except Exception as e:
            send_to_logger(e , message.from_user.id)
        deleteMessages()

    @bot.callback_query_handler(func=lambda call: True)
    def callback_handler(call):
        try:
            chat_id = call.message.chat.id
            manageMessages(id=chat_id, messageId=call.message.id)
            deleteMessages()
            user_id = call.from_user.id
            data = call.data
            manageMessages(id=chat_id, messageId=call.message.id)
            if data.startswith("course_"):
                course = data.split("_")[1]
                user_data[chat_id]["course"] = course
                bot.send_message(call.message.chat.id, 'Выберите вашу школу:', reply_markup=gen_school_markup())
                bot.answer_callback_query(call.id)
            elif data.startswith("school_"):
                school_index = int(data.split("_")[1])
                school = s[school_index]
                user_data[chat_id]["school"] = school
                bot.send_message(call.message.chat.id, 'Введите вашу группу (например, 4А52)\nБуквы в номере группы - это кириллица:')

                bot.register_next_step_handler(call.message, handle_group_input, user_id)
                bot.answer_callback_query(call.id)
            elif data.startswith('weekDay_'):
                dayIndex = int(data.split("_")[1])
                bot.send_message(chat_id, "Пожалуйста , подождите...")
                manageMessages(id=chat_id, messageId=call.message.id + 1)
                sche = webside(day_index= dayIndex , wId= True , id = call.message.chat.id)
                deleteMessages()
                if not sche[1]:
                    send_to_logger(sche[0] , isntanexeption = True , id = call.message.chat.id)
                markup = InlineKeyboardMarkup()
                markup.add(InlineKeyboardButton('Вернуться в меню' , callback_data='menu'))
                bot.send_message(call.message.chat.id , sche[0] , reply_markup=markup)
            elif data == 'schedule':
                try:
                    bot.send_message(call.message.chat.id, "Выберите день недели:", reply_markup=genWeekMarkup())
                except Exception as e:
                    send_to_logger(e, call.message.chat.id)
            elif data == 'profile':
                markup , sub = gen_profile_markup(call.message.chat.id)
                bot.send_message(call.message.chat.id , getUserProfile(chat_id) , reply_markup= markup)
            elif data == "friends":
                markup , f = gen_friends_markup(call.message.chat.id)
                if f == 0:
                    bot.send_message(call.message.chat.id , f'У вас {f} друзей , но вы всегда можете добавить кого-то :) Максимум - {friendsCount} друзей.', reply_markup=markup)
                else:
                    bot.send_message(call.message.chat.id , f'Кол-во ваших друзей - {f} , максимум - {friendsCount}. А вот и {"они" if f > 1 else "он"}:', reply_markup=markup)
            elif data == "menu":
                text = 'Вы в главном меню.\nВозможные действия:'
                bot.send_message(call.message.chat.id,text=menuText,
                                     reply_markup=generateMenu(chat_id))
            #     markup.add(InlineKeyboardButton("Удалить друга" , callback_data=f"{id}_friend_delete"))
            # markup.add(InlineKeyboardButton("Добавить друга" , callback_data=f"{id}_friend_add"))
            elif data == f"friend_add":
                FriendRegistration[f'{chat_id}'] = {"id" : chat_id}
                bot.send_message(chat_id, "Какой курс у твоего друга?" , reply_markup=gen_course_markup(chat_id , True))
            elif data.startswith("Fcourse_"):
                course = data.split("_")[1]
                FriendRegistration[f'{chat_id}']['course'] = course
                bot.send_message(call.message.chat.id, 'Выберите его школу:', reply_markup=gen_school_markup(isForFriend=True))
                bot.answer_callback_query(call.id , text = "Готово!")
            elif data.startswith("Fschool_"):
                school_index = int(data.split("_")[1])
                school = s[school_index]
                FriendRegistration[f'{chat_id}']["school"] = school
                bot.send_message(call.message.chat.id,
                                 'Введите его группу (например, 4А52)\nБуквы в номере группы - это кириллица:')
                bot.register_next_step_handler(call.message, handle_group_input, chat_id , True)
                bot.answer_callback_query(call.id , "Готово!")
            elif data == 'friend_delete':
                bot.send_message(call.message.chat.id, "Выбери друга для удаления:" , reply_markup=gen_friends_markup(call.message.chat.id , isforDelete=True)[0])
            #markup.add(InlineKeyboardButton(f'{int(friends[-1]) + 1}.{friends[1]} , {friends[-2]}', callback_data=f"friend_delete_{id}_{friends[-1]}"))

            elif data.startswith("friend_delete_"):
                friendId = int(data.split("_")[-1])
                deleteFriends(call.message.chat.id , friendId)
                fixFriendsIds(chat_id)
                markup, f = gen_friends_markup(call.message.chat.id)
                if f == 0:
                    bot.send_message(call.message.chat.id,
                                     f'У вас {f} друзей , но вы всегда можете добавить кого-то :) Максимум - {friendsCount} друзей.',
                                     reply_markup=markup)
                else:
                    bot.send_message(call.message.chat.id,
                                     f'Кол-во ваших друзей - {f} , максимум - {friendsCount}. А вот и {"они" if f > 1 else "он"}:',
                                     reply_markup=markup)
            elif data == "unsub":
                updateUserSub(chat_id , False)
                markup, sub = gen_profile_markup(call.message.chat.id)
                bot.send_message(call.message.chat.id, getUserProfile(chat_id), reply_markup=markup)
            elif data == "sub":
                updateUserSub(chat_id, True)
                markup, sub = gen_profile_markup(call.message.chat.id)
                bot.send_message(call.message.chat.id, getUserProfile(chat_id), reply_markup=markup)
            elif data.startswith(f"friend_{chat_id}"):
                data = data.split("_")
                bot.send_message(chat_id , "Выберете день недели:" , reply_markup=genWeekMarkup(forFriend= True , id= chat_id, friend_index=int(data[-1])))
            elif data.startswith(f"FweekDay_"):
                frId = data.split("_")[-1]
                weekDay = int(data.split("_")[1])
                friend = getFriend(chat_id , int(frId[-1]))[0]
                bot.send_message(chat_id , 'Пожалуйста , подождите...')
                try:
                    manageMessages(chat_id , call.message.id + 1)
                except Exception as e:
                    pass
                sche , ex = webside(day_index=weekDay , course = friend[2] , group= friend[4], school= friend[3] , forFriend= True)
                if not ex:
                    send_to_logger(sche , chat_id)
                markup = InlineKeyboardMarkup()
                markup.add(InlineKeyboardButton("Друзья" , callback_data=f"friends"))
                markup.add(InlineKeyboardButton('Вернуться в меню' , callback_data=f"menu"))
                deleteMessages()
                bot.send_message(chat_id ,  sche , reply_markup=markup)
            elif data == 'adminMenu':
                markup = InlineKeyboardMarkup()
                markup.add(InlineKeyboardButton("LOG", callback_data=f"log"))
                markup.add(InlineKeyboardButton('UPDATE LOG', callback_data=f"updatelog"))
                markup.add(InlineKeyboardButton('GET DB' , callback_data = 'getdb'))
                markup.add(InlineKeyboardButton('BACK TO THE MENU' , callback_data=f"menu"))
                bot.send_message(chat_id , 'ADMIN MENU', reply_markup=markup)
            elif data == 'log':
                markup = InlineKeyboardMarkup()
                markup.add(InlineKeyboardButton("MENU", callback_data=f"adminMenu"))
                try:
                    bot.send_document(call.message.chat.id , open('./log.txt') , reply_markup=markup)
                except Exception as e:
                    bot.send_message(call.message.chat.id , str(e) , reply_markup=markup)
                    send_to_logger(e , chat_id)
            elif data == 'updatelog':
                markup = InlineKeyboardMarkup()
                markup.add(InlineKeyboardButton("MENU", callback_data=f"adminMenu"))
                try:
                    bot.send_document(chat_id , open('./log.txt') , reply_markup=markup , caption='Log was updated! , old log file:')
                    with open('./log.txt' , 'w' , encoding= 'utf-8') as log:
                        log.write('LOG')
                except Exception as e:
                    bot.send_message(chat_id , str(e) , reply_markup=markup)
            elif data == 'getdb':
                markup = InlineKeyboardMarkup()
                markup.add(InlineKeyboardButton("MENU", callback_data=f"adminMenu"))
                try:
                    bot.send_document(chat_id , open('./db/info.db' , 'rb') , reply_markup=markup)
                except Exception as e:
                    bot.send_message(chat_id , str(e) , reply_markup=markup)
            elif data == 'schedule_today':
                now = datetime.now().weekday()
                bot.send_message(chat_id, 'Пожалуйста , подождите...')
                manageMessages(chat_id, call.message.id + 1)
                sche , ex = webside(day_index=now , wId= True , id= chat_id)
                if not ex:
                    send_to_logger(sche , chat_id)
                markup = InlineKeyboardMarkup()
                markup.add(InlineKeyboardButton('Вернуться в меню' , callback_data = 'menu'))
                bot.send_message(chat_id , sche , reply_markup=markup)
                deleteMessages()
            elif data == 'extra_info':
                markup = InlineKeyboardMarkup()
                markup.add(InlineKeyboardButton("Поддержать проект донатом" , callback_data = 'donate_req'))
                markup.add(InlineKeyboardButton('Вернуться в меню', callback_data='menu'))
                bot.send_message(chat_id , "У нас есть канал в телеграме!\nТам выкладываются новости бота , а так же там вы можете оставлять свои идеи по улучшению проекта👨‍💻\n@scheduletpunews" , reply_markup=markup)
            elif data == 'donate_req':
                markup = InlineKeyboardMarkup()
                markup.add(InlineKeyboardButton('Вернуться в меню', callback_data='menu'))
                try:
                    buffer = BytesIO()
                    qr = qrcode.make(donate_link)
                    qr.save(buffer, format='PNG')
                    buffer.seek(0)
                except Exception as e:
                    pass
                # bot.send_photo(chat_id , photo=buffer , caption= f'Вы можете поддержать нас копеечкой по ссылке⬇️ или по QR⬆️\n{donate_link}', reply_markup=markup)
                try:
                    bot.send_photo(chat_id , open('/usr/medissa/schedule.tpu.bot/qr.jpeg' , 'rb') , reply_markup=markup , caption=  f'Вы можете поддержать нас копеечкой по ссылке⬇️ или по QR⬆️\n{donate_link}')
                except Exception as e:
                    send_to_logger(chat_id , e)
                    bot.send_message(chat_id ,  f'Вы можете поддержать нас копеечкой по ссылке⬇️\n{donate_link}' , reply_markup=markup)
        except Exception as e:
            send_to_logger(e , call.message.chat.id)

    def handle_group_input(message, chat_id , isForFriend = False):
        group = message.text.strip()
        if not group:
            bot.send_message(message.chat.id, 'Группа не может быть пустой. Пожалуйста, введите группу еще раз:')
            bot.register_next_step_handler(message, handle_group_input, chat_id)
            return
        manageMessages(id=message.from_user.id, messageId=message.id - 1)
        manageMessages(id=message.from_user.id, messageId=message.id)
        if not isForFriend:
            try:

                user_data[chat_id]["group"] = group
                result = registrate_user(
                    chat_id,
                    user_data[chat_id]["username"],
                    user_data[chat_id]["course"],
                    user_data[chat_id]["school"],
                    user_data[chat_id]["group"],
                    True
                )
                markup = InlineKeyboardMarkup()
                markup.add(InlineKeyboardButton('В главное меню', callback_data='menu'))
                bot.send_message(message.chat.id, result , reply_markup=markup)
            except Exception as e:
                try:
                    send_to_logger(e, chat_id)
                    bot.send_message(message.chat.id, f'Ошибка при регистрации: {e}')
                except Exception as e:
                    pass
            finally:
                if chat_id in user_data:
                    del user_data[chat_id]
            deleteMessages()
        else:
            FriendRegistration[str(chat_id)]["group"] = group
            bot.send_message(chat_id , 'Хорошо , теперь введи его имя :)')


    @bot.message_handler(commands=['subscribe' , 'sub' , 'подписаться'])
    def subscribe_handler(message):
        manageMessages(id=message.from_user.id, messageId=message.id - 1)
        try:
            if not checkUserSub(message.from_user.id):
                user_id = message.from_user.id
                updateUserSub(user_id, True)
                bot.send_message(message.chat.id, 'Вы подписались на рассылку расписания!')
            else:
                bot.send_message(message.chat.id, 'Вы и так были подписанны!')
        except Exception as e:
            bot.send_message(message.chat.id, f'Произошла ошибка при подписке: {e}')
            send_to_logger(e , message.from_user.id)


    @bot.message_handler(commands=['unsubscribe' , 'unsub' , 'отписаться'])
    def unsubscribe_handler(message):
        manageMessages(id=message.from_user.id, messageId=message.id - 1)
        try:
            user_id = message.from_user.id
            if isUserInDb(user_id) and checkUserSub(user_id):
                updateUserSub(user_id, False)
                bot.send_message(message.chat.id, 'Вы отписались от рассылки расписания!')
            else:
                bot.send_message(message.chat.id, 'Вы не были подписаны на рассылку расписания.')
        except Exception as e:
            bot.send_message(message.chat.id, f'Произошла ошибка при отписке: {e}')
            send_to_logger(e , message.from_user.id)
    @bot.message_handler(commands= ['delete'])


    def deleteHandler(message) -> None:
        manageMessages(id=message.from_user.id, messageId=message.id - 1)
        try:
            deleteUser(message.from_user.id)
            bot.send_message(message.from_user.id , 'Ваш профиль удален')
        except Exception as e:
            bot.send_message(message.from_user.id , 'Ошибка при удалении профиля')
            send_to_logger(e , message.from_user.id)
    @bot.message_handler(commands= ['profile'])
    def profileHandler(message:telebot) -> None:
        manageMessages(id=message.from_user.id, messageId=message.id - 1)
        try:
            bot.send_message(message.from_user.id , getUserProfile(id = message.from_user.id , username= message.from_user.username , firstname= message.from_user.first_name) )
        except Exception as e:
            send_to_logger(e , message.from_user.id)

    @bot.message_handler(commands= ['menu'])
    def menu(message:telebot) -> None:
        manageMessages(id=message.from_user.id, messageId=message.id - 1)
        bot.send_message(message.from_user.id , text = menuText  , reply_markup= generateMenu(message.from_user.id))
    @bot.message_handler(commands= daysOfWeek["rus"] + daysOfWeek["eng"])    
    def LastHandler(message) -> None:
        manageMessages(id=message.from_user.id, messageId=message.id - 1)
        def getDayIndex(list_ , element) -> int:
            try:
                for i in range(len(list_)):
                    if list_[i].lower() == element.lower():
                        return i
                return None
            except Exception as e:
                send_to_logger(e , message.from_user.id)
        rus = getDayIndex(daysOfWeek["rus"] , message.text.replace('/' , ''))
        eng = getDayIndex(daysOfWeek["eng"] , message.text.replace('/' , ''))
        try:
            if rus == None and eng == None:
                bot.send_message(message.from_user.id , "Такого дня нет!")
                return
            dayIndex = eng if eng != None else rus
            sche = webside(day_index= dayIndex , id = message.from_user.id , wId= True)
            if not sche[1]:
                send_to_logger(sche[0] , isntanexeption = True , id = message.from_user.id)
            bot.send_message(message.from_user.id , sche[0])
        except Exception as e:
            send_to_logger(e , message.from_user.id)
        deleteMessages()
    @bot.message_handler(content_types= ['photo'])
    def getdonateQr(message):
        if str(message.chat.id) in admins:
            if str(message.caption).lower() == 'qr':
                with open('qr.jpg', 'rb') as f:
                    pass
    @bot.message_handler()
    def getName(message):
        manageMessages(id=message.from_user.id, messageId=message.id - 1)
        manageMessages(id=message.from_user.id, messageId=message.id )
        chat_id = message.chat.id
        #{'873729188': {'id': 873729188, 'course': '2', 'school': 'ИШПР', 'group': '234', 'name': '234'}}
        if str(chat_id) in FriendRegistration.keys():
            FriendRegistration[str(message.chat.id)]['name'] = message.text
            try:
                userdata = FriendRegistration[str(message.chat.id)]
                addFriends(
                    id = userdata['id']
                    ,name = userdata['name']
                    ,school = userdata['school']
                    ,group = userdata['group']
                    ,course = userdata['course']
                )
                markup = InlineKeyboardMarkup()
                markup.row_width = 2
                markup.add(InlineKeyboardButton("Вернуться в меню" , callback_data = 'menu'))
                bot.send_message(message.from_user.id , "Друг добавлен!" , reply_markup= markup)
            except Exception as e:
                try:
                    send_to_logger(e, chat_id)
                    bot.send_message(message.chat.id, f'Ошибка при добавлении: {e}')
                except Exception as e:
                    pass
            finally:
                if str(chat_id) in FriendRegistration.keys():
                    del FriendRegistration[str(chat_id)]
        deleteMessages()
    bot.infinity_polling()
    
    

def distributionSide():
    while True:
        try:
            current_day = datetime.now().day
            if DateManager(datenow= current_day):
                users = getAllSubscribedUsers()
                same_groups = findUsersWithTheSameSchedule(users)
                for users in same_groups:
                    course , school , group = users.split('_')
                    schedule = webside(day_index = datetime.now().weekday() if datetime.weekday != 6 else 0
                                        ,  group = group , school= school , course= int(course))
                    if not schedule[1]:
                        send_to_logger(schedule[0] , isntanexeption = True , id = group)
                    t = f'Отправленно расписание для {school} , {course} курс , группа {group}: {same_groups[users]}'
                    for user in same_groups[users]:
                        markup = InlineKeyboardMarkup()
                        try:
                            markup.add(InlineKeyboardButton("Удалить это сообщение" , callback_data = 'None'))
                        except Exception as e:
                            send_to_logger(e , user.id)
                        try:
                            bot.send_message(user , f'Расписание для {school} , {course} курс , группа {group}:\n\n{schedule[0]}' , reply_markup= markup)
                        except Exception as e:
                            send_to_logger(e , user)
                    send_to_logger(t , justInfo = True)
            time.sleep(60 * checkFrequency)
        except Exception as e:
            send_to_logger(e)
Thread(target = telegramSide).start()
Thread(target = distributionSide).start()
