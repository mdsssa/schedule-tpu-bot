from PIL import Image, ImageDraw, ImageFont
import textwrap
import os
import telebot


def get_schedule_week(title, schedule_data):
    # === НАСТРОЙКИ ===
    WIDTH, HEIGHT = 2400, 1500
    BG_COLOR = (0, 0, 0)
    TEXT_COLOR = (255, 255, 255)
    GRID_COLOR = (90, 90, 90)
    TITLE = title
    WATERMARK = "©TELEGRAM @schedule_tpu_bot "
    CELL_FONT_SIZE = 18
    MIN_ROW_HEIGHT = 90

    # === ИЗОБРАЖЕНИЕ ===
    img = Image.new('RGB', (WIDTH, HEIGHT), BG_COLOR)
    draw = ImageDraw.Draw(img)

    # === ШРИФТЫ (с гарантией UTF-8) ===
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
        # Fallback     return ImageFont.load_default(size=size)

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
    bot = telebot.TeleBot(token=token)
    # === ВОДЯНОЙ ЗНАК ===
    wm_bbox = draw.textbbox((0, 0), WATERMARK, font=watermark_font)
    wm_w = wm_bbox[2] - wm_bbox[0]
    wm_h = wm_bbox[3] - wm_bbox[1]
    draw.text((WIDTH - wm_w - 50, HEIGHT - wm_h - 40), WATERMARK, font=watermark_font, fill=(140, 140, 140))

    return img