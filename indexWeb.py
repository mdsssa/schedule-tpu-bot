from selenium import common
from selenium import webdriver
from selenium.webdriver.common.by import By
from time import sleep
from schoolsXpathes import findSchoolXPatch
import datetime
from dbmanager import *
from selenium.webdriver.chrome.options import Options
import traceback
import sys
# from indexTelegram import send_to_logger
def send_to_logger(e):
    pass
daysOfWeek = ['Понедельник' , "Вторник" , "Среда" , "Четверг" , "Пятница" , 'Суббота' , "Понедельник"]

def getSpecificDay(data , dayIndex = 0):
    try:
        returnData = []
        for index in range(len(data)):
            time = data[index][0]
            lesson = data[index][dayIndex + 1]
            returnData.append([time , lesson])
        return returnData
    except Exception as e:
        print(e)
def isNextPairs(index , element):
        for i in range(6):
            try:
                if element[index + i][1] != '':
                    return True
            except Exception as e:
                pass
        return False
def checkForHolydays(data):
    try:
        holyday = False
        day = 0
        for i , hour in enumerate(data):
            for j , subj in enumerate(hour):
                if "нерабочий" in subj.lower():
                    holyday = True
                    day = j
            if holyday:
                try:
                    data[i+1].insert(day , '')
                except Exception as e:
                    pass

    except Exception as e:
        pass
    return data
def isBackPairs(index , element):
        for i in range(6):
            try:
                if element[index - i][1] != '' and index - i >= 0:
                    return True
            except Exception as e:
                pass
        return False

def get_driver():
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    # chrome_options.add_argument('--disable-dev-shm-usage')
    # chrome_options.add_argument('--no-zygote')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--disable-crash-reporter')
    driver = webdriver.Chrome(
        options=chrome_options
    )
    return driver
def webside(day_index = 5 , group = "4А52"  , school = 'ИШНПТ' , course = 1 , wId = False , id = None , forFriend = False , optionsOn = None):
    try:
        if wId:
            if id != None:
                id, username, course, school, group, sub = getUserInfo(id)
        day_index = 0 if day_index == 6 else day_index
        driver = get_driver()

        try:
            driver.get('https://ro-rasp.tpu.ru/')
        except Exception as e:
            return f"К сожалению , сейчас невозможно получить информацию с сайта ТПУ😰" , False

        try:
            driver.find_element(By.XPATH , str(findSchoolXPatch(school=school))).click()
            driver.find_element(By.XPATH, f"//*[contains(text(), '{course} курс')]").click()
            driver.find_element(By.XPATH, f"//*[contains(text(), '{group.upper()}')]").click()
            speciality = driver.find_element(By.XPATH , '/html/body/div[2]/div/div/div[2]/div[1]/div[2]/div/div[1]/div[2]/ul/li[1]/a').text
            schedule = driver.find_element(By.XPATH , '/html/body/div[2]/div/div/div[2]/div[3]/table')
            rows = schedule.find_elements(By.TAG_NAME, 'tr')
        except Exception as e:
            return ("Вы ввели неправильные данные при регистрации. Свои данные вы можете просмотреть командой /profile , или пройти повторную регестрацию коммандой /registration" , False) if not forFriend else ("Вы ввели неправильные данные при регистрации друга!\nПопробуйте добавить его заново во вкладке «Друзья»" , False)


        #Сортировка данных
        data = []
        for row in rows:
            cells = row.find_elements(By.TAG_NAME, 'td')
            if cells:
                cell_texts = [cell.text for cell in cells]
                data.append(cell_texts)
        now = datetime.datetime.now()

        #Форматирование инфы
        data = checkForHolydays(data)
        dataspec = getSpecificDay(data , day_index)
        count = 0
        to_return = '' + "Специальность : " + speciality + '.'  + '\n' + daysOfWeek[day_index] + '\n'
        text = ''
        for i in range(len(dataspec)):
            count += 1
            time = dataspec[i][0]
            subj = dataspec[i][1]

            if isNextPairs(i , dataspec) and subj == '' and isBackPairs(i , dataspec):
                text += f'{count}.{time.replace('\n' , '-')} - Окно' + '\n'
            elif subj == '':
                text += '\n'
            else:
                text += f'{count}. {time.replace('\n' , '-')} - {subj}' + '\n'

            text += '\n'
        if 'нерабочий праздничный день' in text.lower():
                text = 'Нерабочий праздничный день!\nОтдыхай😴'
        to_return += text

        driver.quit()
        return to_return , True
    except Exception as e:
        try:
            driver.quit()
        except:
            pass
        try:
            e = str(e).split('\n')[0]
        except: 
            pass
        return f'Скорее всего произошла независящая от вас ошибка , вы можете написать автору и уточнить это. (Ошибка - {e})' , False
if __name__ == "__main__":
    print(webside())
    pass