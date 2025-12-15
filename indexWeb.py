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
import psutil, os, signal
from PIL import Image, ImageDraw, ImageFont
import textwrap
import os
import telebot
# markup = InlineKeyboardMarkup()
#                 markup.add(InlineKeyboardButton("MENU", callback_data=f"adminMenu"))
#                 used_lects = []
#                 types_ = ['(ПР)', '(А)'  '(ЛК)']
#                 data, isit = webside(wId=True, id=chat_id, raw=True)
#                 for i in data:
#                     del i[0]
#                     for j, lecture in enumerate(i):
#                         lecture_data = lecture.split('\n')
#                         lecture = lecture_data[0]
#                         if True in [True if i == lecture_data[0] else False for i in types_]:
#                             lecture = f'{lecture_data[1]} {lecture_data[0]}'
#                         if not lecture in used_lects:
#                             used_lects.append(lecture)
#                             markup.add(InlineKeyboardButton(lecture, callback_data=f"del_l_{lecture}"))
def get_pairs_without_deleted(id , data , fullWeek = False):
    try:
        types_ = ['(ПР)', '(А)' , '(ЛК)' , "(КТ)" , "(КС)"]
        deleted_lect = get_deleted_lectures(id)
        if fullWeek:
            for i , row in enumerate(data):
                for j  , element in enumerate(row):
                    lecture_data = element.split('\n')
                    lecture = lecture_data[0]
                    if True in [True if i == lecture_data[0] else False for i in types_]:
                        lecture = f'{lecture_data[1]} {lecture_data[0]}'
                    if lecture in deleted_lect:
                        data[i][j] == 'Вы удалили данный предмет.'
        else:
            for j, element in enumerate(data):
                print("что" , element)
                lecture_data = element[0].split('\n')
                lecture = lecture_data
                print([True if lecture_data in i[0] else False for i in deleted_lect])
                if True in [lecture_data in i[0] for i in deleted_lect]:
                    lecture = f'{lecture_data[1]} {lecture_data[0]}'
                # print(lecture)
                if lecture in deleted_lect:
                    data[j] == ' Вы удалили данный предмет.'
        return data
    except Exception as e:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        tb_list = traceback.extract_tb(exc_traceback)
        last_frame = tb_list[-1]
        file_name = last_frame.filename
        line_number = last_frame.lineno
        function_name = last_frame.name
        message = f'У пользователя {id} произошла ошибка :  {e}'
        message = f'{message}\nОшибка {exc_type.__name__}\nНа строке {line_number} ,в функции {function_name} файла {file_name} '
        print(message)
def get_schedule_week(title, schedule_data):
    WIDTH, HEIGHT = 2400, 1500
    BG_COLOR = (0, 0, 0)
    TEXT_COLOR = (255, 255, 255)
    GRID_COLOR = (90, 90, 90)
    TITLE = title
    WATERMARK = "©TELEGRAM @schedule_tpu_bot "
    CELL_FONT_SIZE = 18
    MIN_ROW_HEIGHT = 90
    img = Image.new('RGB', (WIDTH, HEIGHT), BG_COLOR)
    draw = ImageDraw.Draw(img)
    def get_font(size):
        candidates = [
            "/System/Library/Fonts/Arial.ttf",
            "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
            "C:/Windows/Fonts/arial.ttf",
            "DejaVuSans.ttf",
            "arial.ttf"
        ]
        for path in candidates:
            if os.path.exists(path):
                try:
                    font = ImageFont.truetype(path, size)
                    # Проверка: поддерживает ли кириллицу
                    if draw.textbbox((0, 0), "Тест", font=font)[2] > 10:
                        return font
                except:
                    continue
        # Fallback
        print("Используется fallback шрифт (без кириллицы)")
        return ImageFont.load_default(size=size)

    title_font = get_font(68)
    cell_font = get_font(CELL_FONT_SIZE)
    watermark_font = get_font(30)

    # === РАЗМЕРЫ ===
    margin = 140
    table_top = 220
    table_width = WIDTH - 2 * margin
    cols = len(schedule_data[0])
    cell_width = table_width // cols
    line_height = draw.textbbox((0, 0), "А", font=cell_font)[3] - draw.textbbox((0, 0), "А", font=cell_font)[1] + 5
    padding = 22

    # === ВЫЧИСЛЯЕМ ВЫСОТУ СТРОК ===
    row_heights = []
    for i in range(len(schedule_data)):
        max_lines = 1
        for j in range(cols):
            text = schedule_data[i][j].strip()
            if not text: continue
            lines = text.split('\n')
            count = 0
            for line in lines:
                if draw.textbbox((0, 0), line, font=cell_font)[2] > cell_width - 2 * padding:
                    wrapped = textwrap.wrap(line, width=int((cell_width - 2 * padding) / (CELL_FONT_SIZE * 0.52)))
                    count += len(wrapped)
                else:
                    count += 1
            max_lines = max(max_lines, count)
        height = max(MIN_ROW_HEIGHT, max_lines * line_height + 2 * padding)
        row_heights.append(height)

    # === РИСУЕМ ЗАГОЛОВОК ===
    title_bbox = draw.textbbox((0, 0), TITLE, font=title_font)
    title_w = title_bbox[2] - title_bbox[0]
    draw.text(((WIDTH - title_w) // 2, 80), TITLE, font=title_font, fill=TEXT_COLOR)

    # === РИСУЕМ ТАБЛИЦУ ===
    y = table_top
    for i, row_h in enumerate(row_heights):
        for j in range(cols):
            x1 = margin + j * cell_width
            y1 = y
            x2 = x1 + cell_width
            y2 = y + row_h

            # Сетка
            draw.rectangle([x1, y1, x2, y2], outline=GRID_COLOR, width=1)

            text = schedule_data[i][j].strip()
            if not text:
                continue

            # Перенос
            lines = text.split('\n')
            wrapped = []
            for line in lines:
                if draw.textbbox((0, 0), line, font=cell_font)[2] > cell_width - 2 * padding:
                    wrapped.extend(textwrap.wrap(line, width=int((cell_width - 2 * padding) / (CELL_FONT_SIZE * 0.52))))
                else:
                    wrapped.append(line)

            # Вертикальное центрирование
            total_h = len(wrapped) * line_height
            start_y = y1 + (row_h - total_h) // 2

            for line in wrapped:
                bbox = draw.textbbox((0, 0), line, font=cell_font)
                w = bbox[2] - bbox[0]
                draw.text((x1 + (cell_width - w) // 2, start_y), line, font=cell_font, fill=TEXT_COLOR)
                start_y += line_height

        y += row_h
    wm_bbox = draw.textbbox((0, 0), WATERMARK, font=watermark_font)
    wm_w = wm_bbox[2] - wm_bbox[0]
    wm_h = wm_bbox[3] - wm_bbox[1]
    draw.text((WIDTH - wm_w - 50, HEIGHT - wm_h - 40), WATERMARK, font=watermark_font, fill=(140, 140, 140))

    return img

def kill_chrome_processes():
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:

            name = proc.info['name']
            if name in ('chrome', 'chromedriver' , 'chrome_crashpad'):
                cmdline = proc.info['cmdline']
                if cmdline and ('--headless' in ' '.join(cmdline) or 'chromedriver' in name.lower()):
                    print(f"process killed: {name} (PID: {proc.info['pid']})")
                    proc.terminate()
                    try:
                        proc.wait(timeout=3)
                    except psutil.TimeoutExpired:
                        proc.kill()
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
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
    chrome_options.add_argument('--headless=new')
    chrome_options.add_argument('--no-sandbox')
    # chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')

    chrome_options.add_argument('--disable-crash-reporter')
    chrome_options.add_argument('--no-crash-upload')
    chrome_options.add_argument('--no-report-upload')
    chrome_options.add_argument('--disable-breakpad')
    chrome_options.add_argument('--disable-features=CrashReporting')
    chrome_options.add_argument('--disable-logging')

    chrome_options.add_argument('--no-zygote')
    chrome_options.add_argument('--single-process')
    chrome_options.add_argument('--disable-background-timer-throttling')

    driver = webdriver.Chrome(
        options=chrome_options
    )

    return driver
def webside(day_index = 5 , group = "4А52"  , school = 'ИШНПТ' , course = 1 , wId = False , id = None , forFriend = False , optionsOn = None , allweek = False , raw = False):
    try:
        if wId:
            if id != None:
                id, username, course, school, group, sub = getUserInfo(id)
        day_index = 0 if day_index == 6 else day_index
        driver = get_driver()

        try:
            driver.get('https://ro-rasp.tpu.ru/')
        except Exception as e:
            print(e)
            return f"К сожалению , сейчас невозможно получить информацию с сайта ТПУ😰\nЭта ошибка обычно единичная и больше не повторяется , попробуйте еще раз!" , False

        try:
            try:
                group = group.upper()
            except Exception as e:
                print(e)
                pass
            driver.find_element(By.XPATH , str(findSchoolXPatch(school=school))).click()
            driver.find_element(By.XPATH, f"//*[contains(text(), '{course} курс')]").click()
            driver.find_element(By.XPATH, f"//*[contains(text(), '{group}')]").click()
            speciality = driver.find_element(By.XPATH , '/html/body/div[2]/div/div/div[2]/div[1]/div[2]/div/div[1]/div[2]/ul/li[1]/a').text
            week = driver.find_element(By.XPATH , '/html/body/div[2]/div/div/div[2]/h4').text
            schedule = driver.find_element(By.XPATH , '/html/body/div[2]/div/div/div[2]/div[3]/table')
            rows = schedule.find_elements(By.TAG_NAME, 'tr')
        except Exception as e:
            print(e)
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
        if allweek:
            try:
                return get_schedule_week(title= week , schedule_data=data)
            except Exception:
                return f"К сожалению , сейчас невозможно получить информацию с сайта ТПУ😰\nЭта ошибка обычно единичная и больше не повторяется , попробуйте еще раз!", False
        dataspec = getSpecificDay(data , day_index)
        if True:
            if wId:
                dataspec = get_pairs_without_deleted(id , dataspec)
        # except Exception as e:
        #     print('ошибочка ')
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
        sleep(0.1)
        kill_chrome_processes()
        if raw:
            return data , True
        return to_return , True

    except Exception as e:
        print(e)
        try:
            driver.quit()
            kill_chrome_processes()
            print(e)
        except:
            pass
        try:
            e = str(e).split('\n')[0]
        except: 
            pass
        return f'Скорее всего произошла независящая от вас ошибка , вы можете написать автору и уточнить это. (Ошибка - {e})' , False

if __name__ == "__main__":
    pass