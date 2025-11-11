import sqlite3 as sql
import time

from colorama import Fore
import os
#id username course school group sub 
stPatch = './db/info.db'
def r(text):
    print(f'{Fore.RED} {text}{Fore.RESET}')
def g(text):
    print(f'{Fore.GREEN}{text}{Fore.RESET}')
def b(text):
    print(f'{Fore.BLUE}{text}{Fore.RESET}')
tables = {
    'date' : '(date integer)' ,
    'users' : "(id integer , username string , course integer , school string , 'group' string , sub integer)" ,
    'Friends' : "(id integer , friendName string , friendcourse integer , friendschool string , friendgroup string , Friendid integer)" ,
    'todayUsers' : "(uses integer , isUnuque integer)"
}

def update_users(id):
    try:
        db = sql.connect(stPatch)
        cursor = db.cursor()
        cursor.execute('''SELECT * FROM todayUsers WHERE uses = ?''', (id , ))
        user_uses = cursor.fetchall()
        cursor.execute('''INSERT INTO todayUsers VALUES (? , ?)''', (id , 1 if len(user_uses) == 0 else 0))
        db.commit()
        db.close()
    except Exception as e:
        print(e)


def get_unique():
    try:
        db = sql.connect(stPatch)
        cursor = db.cursor()
        cursor.execute('''SELECT * FROM todayUsers WHERE isUnuque = 1''', )
        a = cursor.fetchall()
        db.close()
        return len(a)
    except Exception as e:
        print(e)
        return 0

def get_usersUse():
    try:
        db = sql.connect(stPatch)
        cursor = db.cursor()
        cursor.execute('''SELECT * FROM todayUsers''', )
        a = cursor.fetchall()
        db.close()
        return len(a)
    except Exception as e:
        print(e)
        return 0

def clearUsers():
    try:
        db = sql.connect(stPatch)
        cursor = db.cursor()
        cursor.execute('''DELETE FROM todayUsers''')
        db.commit()
        db.close()
    except Exception as e:
        print(e)
def makeDb():
    try:
        for table in tables:
            db = sql.connect(stPatch)
            db.cursor().execute(f'CREATE TABLE IF NOT EXISTS {table} {tables[table]};')
            db.commit()
            db.close()
    except Exception as e:
        print(e)
def DateManager(datenow:int = 0) -> int:
    try:
        db = sql.connect(stPatch)
        cursor = db.cursor()
        cursor.execute('SELECT * FROM date')
        a = cursor.fetchall()
        a = a[0][0]
        if datenow == a:
            db.close()
            return False
        cursor.execute('DELETE FROM date')
        cursor.execute('INSERT INTO date VALUES (?)' , (datenow ,))
        db.commit()
        db.close()
        g(f'Дата обновлена на {datenow}')
        return True
    except Exception as e:
        r(f"При обновлении даты произошла ошибка: {e}")
        return False
    
def getUserInfo(id):
    try:
        db = sql.connect(stPatch)
        cursor = db.cursor().execute(f'SELECT * FROM users WHERE id = {id}')
        a = cursor.fetchall()[0]
        db.close()
        return a
    except Exception as e:
        r(f"{e}")
def getAllSubscribedUsers() -> list:
    try:
        db = sql.connect(stPatch)
        cursor = db.cursor()
        info = cursor.execute('SELECT * FROM users WHERE sub = 1')
        a = info.fetchall()
        db.close()
        return a
    except Exception as e:
        r(f"При получении всех подписанных пользователей произошла ошибка: {e}")
        return []

def registrate_user(id:int , username:str ,  course:int , school:str , group:str , sub:bool = True) -> None:
    try:
        if not isUserInDb(id):
            db = sql.connect(stPatch)
            cursor = db.cursor()
            cursor.execute('INSERT INTO users VALUES (? , ? , ? , ? , ? , ?)' , (id , username ,course ,school.upper() , group.upper() , int(sub)))
            db.commit()
            db.close()
            g('Юзер зарегистрирован!')
            return f"Вы зарегистрированны , ваши данные : \nКурс - {course} \nШкола - {school} \nГруппа - {group}"
        else:
            r('Юзер уже есть в датабазе!')
            return 'Вы уже есть в датабазе!'
    except Exception as e:
        r(f"При регистрации пользователя произошла ошибка: {e}")
        return f"При регистрации пользователя произошла ошибка: {e}"

def updateUserName(id , username):
    try:
         db = sql.connect(stPatch)
         cursor = db.cursor()
         cursor.execute('UPDATE users SET username = ? WHERE id = ?' , (username , id))
         db.commit()
         db.close()
         g(f'Имя пользователя @{username} обновлено!')
    except Exception as e:
        r(f"При обновлении имени пользователя произошла ошибка: {e}")

def updateUserSub(id , sub):
    try:
        db = sql.connect(stPatch)
        cursor = db.cursor()
        cursor.execute('UPDATE users SET sub = ? WHERE id = ?' , (int(sub) , id))
        db.commit()
        db.close()
        if sub:
            g(f'Подписка пользователя с id {id} активирована!')
        else:
            r(f'Подписка пользователя с id {id} деактивирована')
    except Exception as e:
        r(f"При обновлении подписки пользователя произошла ошибка: {e}")
def isUserInDb(id):
    db = sql.connect(stPatch)
    cursor = db.cursor().execute(f'SELECT * FROM users WHERE id = {id}')
    a = cursor.fetchall()
    db.close()
    return len(a) > 0


def checkUserSub(id):
    try:
        db = sql.connect(stPatch)
        cursor = db.cursor()
        info = cursor.execute(f'SELECT sub FROM users WHERE id = {id}')
        a = info.fetchone()[0]
        db.close()
        return bool(a)
    except Exception as e:
        r(f"При проверке подписки пользователя произошла ошибка: {e}")
def get_users():
    try:
        db = sql.connect(stPatch)
        cursor = db.cursor()
        info = cursor.execute('SELECT * FROM users')
        a = cursor.fetchall()
        db.close()
        return a
    except Exception as e:
        print(e)
def deleteUser(id):
    try:
        db = sql.connect(stPatch)
        cursor = db.cursor()
        cursor.execute(f"DELETE FROM users WHERE id = {id}")
        db.commit()
        db.close()
        r(f'Профиль пользователя {id} удален')
    except Exception as e:
        r(f'Произошла ошибка {e} при удалении профиля пользователя {id}')
def getUserProfile(id , username = None , firstname = None):
    try:
        if not isUserInDb(id):
            return 'У вас нет профиля , пройдите регистрацию коммандой /registration.'
        else:
            db = sql.connect(stPatch)
            cursor = db.cursor()
            info = cursor.execute(f'SELECT * FROM users WHERE id = {id}')
            info = info.fetchone()
            db.close()
            return f'''{"Вы подписанны на рассылку📬" if bool(info[-1]) else "Вы не подписанны на рассылку📭"}
Курс - {info[2]}
Школа - {info[3]}
Группа - {info[4]}'''
    except Exception as e:
        r(f'Произошла ошибка {e} при получении профиля пользователя {id}')
        return r(f'Произошла ошибка {e} при получении профиля')
def getfriends(id):
    try:
        db = sql.connect(stPatch)
        cursor = db.cursor()
        info = cursor.execute(f'SELECT * FROM Friends WHERE id = {id}')
        info = info.fetchall()
        db.close()
        return info
    except Exception as e:
        print(e)
#{'873729188': {'id': 873729188, 'course': '2', 'school': 'ИШПР', 'group': '234', 'name': '234'}}
#'Friends' : "(id integer , friendName string , friendcourse integer , friendschool string , friendgroup string , Friendid integer)"
def addFriends(id , course , school  , group , name):
    try:
        db = sql.connect(stPatch)
        cursor = db.cursor()
        cursor.execute("INSERT INTO Friends VALUES (? , ? , ? , ? , ? , ?)" , (id , name, course, school, group , len(getfriends(id))))
        db.commit()
        db.close()
    except Exception as e:
        print(e)
def deleteFriends(id , index):
    try:
        db = sql.connect(stPatch)
        cursor = db.cursor()
        cursor.execute(f"DELETE FROM Friends WHERE id = {id} AND Friendid = {index}")
        db.commit()
        db.close()
    except Exception as e:
        print(e)

def getFriend(id , index):
    try:
        db = sql.connect(stPatch)
        cursor = db.cursor()
        info = cursor.execute(f'SELECT * FROM Friends WHERE id = ? AND Friendid = ?' , (id , index))
        info = info.fetchall()
        db.close()
        return info

    except Exception as e:
        print(e)
def fixFriendsIds(id):
    try:
        db = sql.connect(stPatch)
        cursor = db.cursor()
        cursor.execute('SELECT * FROM Friends WHERE id = ?', (id,))
        info = cursor.fetchall()
        fixed = []
        db.close()
        for i , friend in enumerate(info):
            fixed.append((friend[0], friend[1] , friend[2] , friend[3] , friend[4] , i))
        db = sql.connect(stPatch)
        cursor = db.cursor()
        cursor.execute('DELETE FROM Friends WHERE id = ?', (id,))
        db.commit()
        for friend in fixed:
            cursor.execute(f"INSERT INTO Friends VALUES {str(friend)}")
        db.commit()
        db.close()
    except Exception as e:
        print(e)
if __name__ == '__main__':
    makeDb()
    print(checkUserSub(873729188))
    for i in range(10):
        update_users(873729188)
    clearUsers()