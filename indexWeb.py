from selenium import common
from selenium import webdriver
from selenium.webdriver.common.by import By
from time import sleep
from schoolsXpathes import findSchoolXPatch
import datetime
from dbmanager import *
# from indexTelegram import send_to_logger
def send_to_logger(e):
    pass
daysOfWeek = ['Понедельник' , "Вторник" , "Среда" , "Четверг" , "Пятница" , "Понедельник"]

def getSpecificDay(data , dayIndex = 0):
    returnData = []
    for index in range(len(data)):
        time = data[index][0]
        lesson = data[index][dayIndex + 1]
        returnData.append([time , lesson])
    return returnData

def isNextPairs(index , element):
        for i in range(6):
            try:
                if element[index + i][1] != '':
                    return True
            except Exception as e:
                pass
        return False


def isBackPairs(index , element):
        for i in range(6):
            try:
                if element[index - i][1] != '' and index - i >= 0:
                    return True
            except Exception as e:
                pass
        return False



def webside(day_index = 0 , group = "4А52" , optionsOn = True , school = 'ИШНПТ' , course = 1 , wId = False , id = None):
    if wId:
        if id != None:
            id , username , course , school , group , sub = getUserInfo(id)
    try:
        day_index = 0 if day_index == 6 else day_index
        options = webdriver.ChromeOptions()
        if optionsOn:
            options.add_argument("-headless=new")
            options.add_argument('--no-sandbox') 
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-blink-features=AutomationControlled')  
            options.add_experimental_option("excludeSwitches", ["enable-automation"]) 
            options.add_experimental_option('useAutomationExtension', False)
            options.add_argument('--window-size=1920,1080')  
            options.add_argument('--disable-gpu')  
        

        #Парсинг
        try:
            driver = webdriver.Chrome(options= options)
            driver.get('https://ro-rasp.tpu.ru/')
        except Exception as e:
            return f"К сожалению , сейчас невозможно получить информацию с сайта ТПУ😰" , False

        try:
            driver.find_element(By.XPATH , str(findSchoolXPatch(school=school))).click()
            sleep(1)
            driver.find_element(By.XPATH, f"//*[contains(text(), '{course} курс')]").click()
            sleep(1)
            driver.find_element(By.XPATH, f"//*[contains(text(), '{group.upper()}')]").click()
            speciality = driver.find_element(By.XPATH , '/html/body/div[2]/div/div/div[2]/div[1]/div[2]/div/div[1]/div[2]/ul/li[1]/a').text
            schedule = driver.find_element(By.XPATH , '/html/body/div[2]/div/div/div[2]/div[3]/table')
            rows = schedule.find_elements(By.TAG_NAME, 'tr')
        except Exception as e:
            return "Вы ввели неправильные данные при регистрации. Свои данные вы можете просмотреть командой /profile , или пройти повторную регестрацию коммандой /start" , False


        #Сортировка данных
        data = []
        for row in rows:
            cells = row.find_elements(By.TAG_NAME, 'td')
            if cells:
                cell_texts = [cell.text for cell in cells]
                data.append(cell_texts)
        now = datetime.datetime.now()
        #Форматирование инфы
        dataspec = getSpecificDay(data , day_index)
        count = 0
        to_return = '' + "Специальность : " + speciality + '.'  + '\n' + daysOfWeek[day_index] + '\n'
        for i in range(len(dataspec)):
            count += 1
            time = dataspec[i][0]
            subj = dataspec[i][1]
            if isNextPairs(i , dataspec) and subj == '' and isBackPairs(i , dataspec):
                to_return += f'{count}.{time.replace('\n' , '-')} - Окно' + '\n'
            elif subj == '':
                to_return += '\n'
            else:
                to_return += f'{count}. {time.replace('\n' , '-')} - {subj}' + '\n'
            to_return += '\n'
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
        return f'Скорее всего произошла независящая от ваш ошибка , вы можете написать автору и уточнить это. (Ошибка - {e})' , False
if __name__ == "__main__":
    #место для проверки функций
    pass