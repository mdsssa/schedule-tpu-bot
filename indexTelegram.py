import telebot
from indexWeb import webside
from schoolsXpathes import schools
from dbmanager import *
from datetime import datetime
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from threading import Thread
import time
import string
daysOfWeek = {
    "rus" : ['понедельник' , "вторник" , "среда" , "четверг" , "пятница" , "суббота"] ,
    "eng" : ["monday" , "tuesday" , "wednesday" , "thursday" , "friday" , "saturday"]
    }
checkFrequency = 10 #проверка / минуты
messagesToDelete = {

}

bot = telebot.TeleBot(token='TG token')
#id username course school group sub 

def findUsersWithTheSameSchedule(users) -> dict:
    groupsandUsers = {}
    for i in range(len(users)):
        if f'{str(users[i][2])}_{users[i][3]}_{users[i][4].upper()}' not in groupsandUsers.keys():
            groupsandUsers[f'{str(users[i][2])}_{users[i][3]}_{users[i][4].upper()}'] = [users[i][0]]
        else:
            groupsandUsers[f'{str(users[i][2])}_{users[i][3]}_{users[i][4].upper()}'].append(users[i][0])
    return groupsandUsers

def telegramSide():
    messages = {
        "greeting": 'Привет'
    }

    s = ["Бизнес-школа" , "ИШИнЭс" , "ИШИТР" , "ИШНКБ" , "ИШНПТ" , "ИШПР" , 
            "ИШЭ" , "ИЯТШ" , "ИШФВП" , "ИШХБМТ" , 'УН' , "УОД" , "ШОН"]

    user_data = {}

    def gen_course_markup():
        markup = InlineKeyboardMarkup()
        markup.row_width = 3
        markup.add(
            InlineKeyboardButton("1 курс", callback_data="course_1"),
            InlineKeyboardButton("2 курс", callback_data="course_2"),
            InlineKeyboardButton("3 курс", callback_data="course_3"),
            InlineKeyboardButton("4 курс", callback_data="course_4"),
            InlineKeyboardButton("5 курс", callback_data="course_5"),
            InlineKeyboardButton("6 курс", callback_data="course_6")
        )
        return markup
    
    def deleteMessages(chatId:int  , id:int):
        print(messagesToDelete)
        try:
            for i , messageId in enumerate(messagesToDelete[f'{id}']):
                try:
                    bot.delete_message(chat_id= chatId , message_id=messageId)
                    del messagesToDelete[f'{id}'] [i]
                    print(deleteMessages)
                except Exception as e:
                    print(e)
        except Exception as e:
            print(e)
    def manageMesages(id , messageId):
        if f'{id}' not in messagesToDelete.keys():
            messagesToDelete[f'{id}'] = [messageId]
        else:
            messagesToDelete[f'{id}'] = messagesToDelete[f'{id}'].append(messageId)

    def gen_school_markup():
        markup = InlineKeyboardMarkup()
        markup.row_width = 2
        for i, school in enumerate(s):
            markup.add(InlineKeyboardButton(school, callback_data=f"school_{i}"))
        return markup
    
    def genWeekMarkup():
        markup = InlineKeyboardMarkup()
        markup.row_width = 3
        for i, weekDay in enumerate(daysOfWeek["rus"]):
            markup.add(InlineKeyboardButton(weekDay.capitalize() , callback_data=f"weekDay_{i}"))
        return markup


    @bot.message_handler(commands=['start'])
    def stop_handler(message):
        if isUserInDb(message.from_user.id):
            deleteUser(id = message.from_user.id)
        user_id = message.from_user.id
        user_data[user_id] = {"username": message.from_user.username}
        bot.send_message(message.chat.id, 'Выберите ваш курс:', reply_markup=gen_course_markup())
        # manageMesages(id = message.from_user.id , messageId= message.id + 1)



    @bot.message_handler(commands= ['week'])
    def weekHandler(message):
        # manageMesages(id = message.from_user.id , messageId= message.id + 1)
        bot.send_message(message.from_user.id , "Выберете день недели:" , reply_markup= genWeekMarkup())

    @bot.callback_query_handler(func=lambda call: True)
    def callback_handler(call):
        user_id = call.from_user.id
        data = call.data

        if data.startswith("course_"):
            course = data.split("_")[1]
            user_data[user_id]["course"] = course
            # deleteMessages(chatId= call.message.chat.id , id = call.message.chat.id)
            bot.send_message(call.message.chat.id, 'Выберите вашу школу:', reply_markup=gen_school_markup())
            bot.answer_callback_query(call.id)
            # manageMesages(id = call.message.chat.id , messageId= call.message.id + 1)
        elif data.startswith("school_"):
            school_index = int(data.split("_")[1])
            school = s[school_index]
            user_data[user_id]["school"] = school
            bot.send_message(call.message.chat.id, 'Введите вашу группу (например, 4А52)\nБуквы в номере группы - это кириллица:')
            bot.register_next_step_handler(call.message, handle_group_input, user_id)
            bot.answer_callback_query(call.id)
        elif data.startswith('weekDay_'):
            dayIndex = int(data.split("_")[1])
            # deleteMessages(chatId= call.message.chat.id , id = call.message.chat.id)
            bot.send_message(call.message.chat.id , webside(day_index= dayIndex , wId= True , id = call.message.chat.id))
    def handle_group_input(message, user_id):
        group = message.text.strip()
        if not group:
            bot.send_message(message.chat.id, 'Группа не может быть пустой. Пожалуйста, введите группу еще раз:')
            bot.register_next_step_handler(message, handle_group_input, user_id)
            return

        user_data[user_id]["group"] = group
        try:
            result = registrate_user(
                user_id,
                user_data[user_id]["username"],
                user_data[user_id]["course"],
                user_data[user_id]["school"],
                user_data[user_id]["group"],
                True
            )
            bot.send_message(message.chat.id , result)
        except Exception as e:
            bot.send_message(message.chat.id, f'Ошибка при регистрации: {e}')
        finally:
            if user_id in user_data:
                del user_data[user_id]


    @bot.message_handler(commands=['subscribe' , 'sub' , 'подписаться'])
    def subscribe_handler(message):
        try:
            if not checkUserSub(message.from_user.id):
                user_id = message.from_user.id
                username = message.from_user.username
                updateUserSub(user_id, True)
                bot.send_message(message.chat.id, 'Вы подписались на рассылку расписания!')
            else:
                bot.send_message(message.chat.id, 'Вы и так были подписанны!')
        except Exception as e:
            bot.send_message(message.chat.id, f'Произошла ошибка при подписке: {e}')


    @bot.message_handler(commands=['unsubscribe' , 'unsub' , 'отписаться'])
    def unsubscribe_handler(message):
        try:
            user_id = message.from_user.id
            if isUserInDb(user_id) and checkUserSub(user_id):
                updateUserSub(user_id, False)
                bot.send_message(message.chat.id, 'Вы отписались от рассылки расписания!')
            else:
                bot.send_message(message.chat.id, 'Вы не были подписаны на рассылку расписания.')
        except Exception as e:
            bot.send_message(message.chat.id, f'Произошла ошибка при отписке: {e}')
    @bot.message_handler(commands= ['delete'])


    def deleteHandler(message) -> None:
        try:
            deleteUser(message.from_user.id)
            bot.send_message(message.from_user.id , 'Ваш профиль удален')
        except Exception as e:
            bot.send_message(message.from_user.id , 'Профиль удален!')

    @bot.message_handler(commands= ['profile'])
    def profileHandler(message:telebot) -> None:
        bot.send_message(message.from_user.id , getUserProfile(id = message.from_user.id , username= message.from_user.username , firstname= message.from_user.first_name))



    @bot.message_handler(commands= daysOfWeek["rus"] + daysOfWeek["eng"])    
    def LastHandler(message) -> None:
        def getDayIndex(list_ , element) -> int:
            for i in range(len(list_)):
                if list_[i].lower() == element.lower():
                    return i
            return None
        rus = getDayIndex(daysOfWeek["rus"] , message.text.replace('/' , ''))
        eng = getDayIndex(daysOfWeek["eng"] , message.text.replace('/' , ''))
        if rus == None and eng == None:
            bot.send_message(message.from_user.id , "Такого дня нет!")
            return
        dayIndex = eng if eng != None else rus
        bot.send_message(message.from_user.id , webside(day_index= dayIndex , id = message.from_user.id))

    bot.infinity_polling()
    
    

def distributionSide():
    while True:
        current_day = datetime.now().day
        if DateManager(datenow= current_day):
            users = getAllSubscribedUsers()
            same_groups = findUsersWithTheSameSchedule(users)
            for users in same_groups:
                course , school , group = users.split('_')
                # schedule = webside(day_index = datetime.now().weekday() if datetime.weekday != 6 else 0
                #                     ,  group = group , school= school , course= int(course) , optionsOn= True) 
                b(f'Расписание для {school} , {course} курс , группа {group}: ')
                for user in same_groups[users]:
                    g('Отправленно расписание для ' + str(user))
                # bot.send_message(user , f'Расписание для {school} , {course} курс , группа {group}:\n\n{schedule}')
        time.sleep(60 * checkFrequency)

Thread(target = telegramSide).start()
Thread(target = distributionSide).start()