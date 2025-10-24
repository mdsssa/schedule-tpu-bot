import sqlite3 as sql
from colorama import Fore
#id username course school group sub 
stPatch = './info.db'
def r(text):
    print(f'{Fore.RED}{text}{Fore.RESET}')
def g(text):
    print(f'{Fore.GREEN}{text}{Fore.RESET}')
def b(text):
    print(f'{Fore.BLUE}{text}{Fore.RESET}')
def DateManager(datenow:int = 0) -> int:
    try:
        db = sql.connect(stPatch)
        cursor = db.cursor()
        cursor.execute('SELECT * FROM date')
        a = cursor.fetchall()[0][0]
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
        r(f"При проверке подписки пользователя произошла ошибка: {e}")
def getAllSubscribedUsers() -> list:
    try:
        db = sql.connect(stPatch)
        cursor = db.cursor().execute('SELECT * FROM users WHERE sub = 1')
        a = cursor.fetchall()
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
        cursor = db.cursor().execute(f'SELECT sub FROM users WHERE id = {id}')
        a = cursor.fetchall()[0][0]
        db.close()
        return bool(a)
    except Exception as e:
        r(f"При проверке подписки пользователя произошла ошибка: {e}")

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
def getUserProfile(id , username , firstname):
    try:
        if not isUserInDb(id):
            return 'У вас нет профиля , пройдите регистрацию коммандой /start.'
        else:
            db = sql.connect(stPatch)
            cursor = db.cursor()
            info = cursor.execute(f'SELECT * FROM users WHERE id = {id}')
            info = info.fetchone()
            db.close
            return f'''{firstname} , @{username}
{"Вы подписанны на рассылку📬" if bool(info[-1]) else "Вы не подписанны на рассылку📭"}
Курс - {info[2]}
Школа - {info[3]}
Группа - {info[4]}'''
    except Exception as e:
        r(f'Произошла ошибка {e} при получении профиля пользователя {id}')
        return r(f'Произошла ошибка {e} при получении профиля')
if __name__ == '__main__':
    # db = sql.connect(stPatch)
    # cursor = db.cursor()
    # cursor.execute("CREATE TABLE date (date integer)")
    # db.commit() #5822968635
    # db.close()
    # registrate_user(5822968635 , "spitinmyfaceivegonemad" , 1 , 'ишнпт' , "4а52" , True)

    pass