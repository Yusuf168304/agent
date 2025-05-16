import telegram
from telegram.ext import Application, CommandHandler, MessageHandler, filters
import pyautogui
import cv2
import pyaudio
import wave
import os
import wmi
import psutil
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
import subprocess
import platform
import time
import numpy as np
import logging

# Настройка логирования
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Настройки бота
TOKEN = "7511415912:AAFkEOQdyIwhlDIa7OlflLdu_Lo3C1v5HPE"  # Получите у @BotFather
ALLOWED_USER_ID = 1177054949  # Ваш Telegram ID (узнайте через @userinfobot)

# Проверка авторизации
def check_authorization(update):
    if update.message.from_user.id != ALLOWED_USER_ID:
        update.message.reply_text("Доступ запрещён!")
        return False
    return True

# Команда /start
async def start(update, context):
    await update.message.reply_text("Привет! Я бот для управления ПК. Доступные команды:\n"
                                   "/screenshot - Сделать скриншот\n"
                                   "/selfie - Селфи с веб-камеры\n"
                                   "/record - Записать аудио (30 сек)\n"
                                   "/openyoutube - Открыть YouTube\n"
                                   "/opengoogle - Открыть Google\n"
                                   "/openinstagram - Открыть Instagram\n"
                                   "/openwikipedia - Открыть Wikipedia\n"
                                   "/opengrok - Открыть Grok\n"
                                   "/opentwitter - Открыть Twitter (X)\n"
                                   "/search <запрос> - Поиск в Google\n"
                                   "/recordscreen - Записать экран (10 сек)\n"
                                   "/recordcamera - Записать камеру (10 сек)\n"
                                   "/setvolume <0-100> - Установить громкость\n"
                                   "/setbrightness <0-100> - Установить яркость\n"
                                   "/reboot - Перезагрузить ПК\n"
                                   "/systeminfo - Информация о системе\n"
                                   "/listdir <path> - Список файлов в папке\n"
                                   "/presskey <key> - Нажать клавишу")

# 🌐 Открыть сайты
async def open_youtube(update, context):
    if not check_authorization(update):
        return
    await open_website(update, context, "https://www.youtube.com")

async def open_google(update, context):
    if not check_authorization(update):
        return
    await open_website(update, context, "https://www.google.com")

async def open_instagram(update, context):
    if not check_authorization(update):
        return
    await open_website(update, context, "https://www.instagram.com")

async def open_wikipedia(update, context):
    if not check_authorization(update):
        return
    await open_website(update, context, "https://www.wikipedia.org")

async def open_grok(update, context):
    if not check_authorization(update):
        return
    await open_website(update, context, "https://grok.x.ai")

async def open_twitter(update, context):
    if not check_authorization(update):
        return
    await open_website(update, context, "https://x.com")

async def open_website(update, context, url):
    try:
        logger.info(f"Попытка открыть сайт: {url}")
        chrome_options = Options()
        chrome_options.add_argument("--start-maximized")
        chrome_options.add_argument("--no-sandbox")  # Для стабильности
        chrome_options.add_argument("--disable-dev-shm-usage")  # Для избежания ошибок памяти
        # Укажите путь к chromedriver, если он не в PATH
        # driver = webdriver.Chrome(executable_path="путь/к/chromedriver", options=chrome_options)
        driver = webdriver.Chrome(options=chrome_options)
        driver.get(url)
        logger.info(f"Сайт {url} успешно открыт")
        await update.message.reply_text(f"Открыт сайт: {url}")
        time.sleep(5)  # Держим браузер открытым 5 секунд
        driver.quit()
    except Exception as e:
        logger.error(f"Ошибка при открытии сайта {url}: {str(e)}")
        await update.message.reply_text(f"Ошибка при открытии сайта: {str(e)}\n"
                                       "Проверьте, установлен ли chromedriver и соответствует ли он версии Chrome.")

# 🌐 Поиск в Google (автоматический)
async def search(update, context):
    if not check_authorization(update):
        return

    query = " ".join(context.args) if context.args else "test"
    try:
        logger.info(f"Выполнение поиска: {query}")
        chrome_options = Options()
        chrome_options.add_argument("--start-maximized")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        driver = webdriver.Chrome(options=chrome_options)
        driver.get("https://www.google.com")
        search_box = driver.find_element("name", "q")
        search_box.send_keys(query)
        search_box.send_keys(Keys.RETURN)
        logger.info(f"Поиск выполнен: {query}")
        await update.message.reply_text(f"Выполнен поиск в Google: {query}")
        time.sleep(5)  # Показываем результаты 5 секунд
        driver.quit()
    except Exception as e:
        logger.error(f"Ошибка при поиске: {str(e)}")
        await update.message.reply_text(f"Ошибка при поиске: {str(e)}\n"
                                       "Проверьте chromedriver и соединение с интернетом.")

# 🖥️ Запись экрана (10 секунд)
async def record_screen(update, context):
    if not check_authorization(update):
        return

    duration = 10
    output_file = f"screenrecord_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4"

    # Захват экрана
    screen_size = pyautogui.size()
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(output_file, fourcc, 20.0, (screen_size.width, screen_size.height))

    await update.message.reply_text("Записываю экран (10 сек)...")
    start_time = time.time()
    while time.time() - start_time < duration:
        img = pyautogui.screenshot()
        frame = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
        out.write(frame)

    out.release()

    # Отправка видео
    try:
        with open(output_file, 'rb') as video:
            await context.bot.send_video(chat_id=update.message.chat_id, video=video)
        os.remove(output_file)
        await update.message.reply_text("Запись экрана отправлена!")
    except Exception as e:
        logger.error(f"Ошибка при отправке видео экрана: {str(e)}")
        await update.message.reply_text(f"Ошибка при отправке видео: {str(e)}")

# 📸 Запись с камеры (10 секунд)
async def record_camera(update, context):
    if not check_authorization(update):
        return

    duration = 10
    output_file = f"camerarecord_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4"

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        await update.message.reply_text("Ошибка: не удалось открыть камеру.")
        return

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(output_file, fourcc, 20.0, (640, 480))

    await update.message.reply_text("Записываю камеру (10 сек)...")
    start_time = time.time()
    while time.time() - start_time < duration:
        ret, frame = cap.read()
        if ret:
            out.write(frame)

    cap.release()
    out.release()

    # Отправка видео
    try:
        with open(output_file, 'rb') as video:
            await context.bot.send_video(chat_id=update.message.chat_id, video=video)
        os.remove(output_file)
        await update.message.reply_text("Запись с камеры отправлена!")
    except Exception as e:
        logger.error(f"Ошибка при отправке видео с камеры: {str(e)}")
        await update.message.reply_text(f"Ошибка при отправке видео: {str(e)}")

# Остальные функции
async def selfie(update, context):
    if not check_authorization(update):
        return

    cap = cv2.VideoCapture(0)
    ret, frame = cap.read()
    if ret:
        photo_path = f"selfie_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        cv2.imwrite(photo_path, frame)
        with open(photo_path, 'rb') as photo:
            await context.bot.send_photo(chat_id=update.message.chat_id, photo=photo)
        os.remove(photo_path)
        await update.message.reply_text("Селфи отправлено!")
    else:
        await update.message.reply_text("Ошибка: не удалось получить изображение с камеры.")
    cap.release()

async def record_audio(update, context):
    if not check_authorization(update):
        return

    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 2
    RATE = 44100
    RECORD_SECONDS = 30
    OUTPUT_FILE = f"audio_{datetime.now().strftime('%Y%m%d_%H%M%S')}.wav"

    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)

    await update.message.reply_text("Записываю аудио (30 сек)...")
    frames = []
    for _ in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK)
        frames.append(data)

    stream.stop_stream()
    stream.close()
    p.terminate()

    wf = wave.open(OUTPUT_FILE, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()

    with open(OUTPUT_FILE, 'rb') as audio:
        await context.bot.send_audio(chat_id=update.message.chat_id, audio=audio)
    os.remove(OUTPUT_FILE)
    await update.message.reply_text("Аудио отправлено!")

async def screenshot(update, context):
    if not check_authorization(update):
        return

    screenshot = pyautogui.screenshot()
    screenshot_path = f"screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    screenshot.save(screenshot_path)

    with open(screenshot_path, 'rb') as photo:
        await context.bot.send_photo(chat_id=update.message.chat_id, photo=photo)
    os.remove(screenshot_path)
    await update.message.reply_text("Скриншот отправлен!")

async def set_volume(update, context):
    if not check_authorization(update):
        return

    try:
        volume_level = int(context.args[0]) if context.args else 50
        volume_level = max(0, min(100, volume_level))
        subprocess.run(["nircmd.exe", "setsysvolume", str(int(volume_level * 655.35))])
        await update.message.reply_text(f"Громкость установлена на {volume_level}%")
    except Exception as e:
        logger.error(f"Ошибка при установке громкости: {str(e)}")
        await update.message.reply_text(f"Ошибка: {str(e)}")

async def set_brightness(update, context):
    if not check_authorization(update):
        return

    try:
        brightness = int(context.args[0]) if context.args else 50
        brightness = max(0, min(100, brightness))
        w = wmi.WMI(namespace="wmi")
        methods = w.WmiMonitorBrightnessMethods()[0]
        methods.WmiSetBrightness(brightness, 0)
        await update.message.reply_text(f"Яркость установлена на {brightness}%")
    except Exception as e:
        logger.error(f"Ошибка при установке яркости: {str(e)}")
        await update.message.reply_text(f"Ошибка: {str(e)}")

async def reboot(update, context):
    if not check_authorization(update):
        return

    await update.message.reply_text("Перезагружаю ПК...")
    subprocess.run(["shutdown", "/r", "/t", "0"])

async def system_info(update, context):
    if not check_authorization(update):
        return

    cpu_usage = psutil.cpu_percent(interval=1)
    ram = psutil.virtual_memory()
    ram_usage = f"{ram.used / 1024 / 1024 / 1024:.2f}/{ram.total / 1024 / 1024 / 1024:.2f} GB"
    hostname = platform.node()
    try:
        ip = subprocess.check_output(["ipconfig"]).decode().split("IPv4 Address")[1].split(":")[1].strip().split("\n")[0]
    except:
        ip = "Не удалось получить IP"
    info = (f"CPU: {cpu_usage}%\n"
            f"RAM: {ram_usage}\n"
            f"Hostname: {hostname}\n"
            f"IP: {ip}")
    await update.message.reply_text(info)

async def list_dir(update, context):
    if not check_authorization(update):
        return

    path = " ".join(context.args) or os.getcwd()
    try:
        files = os.listdir(path)
        files_list = "\n".join(files) or "Папка пуста"
        await update.message.reply_text(f"Содержимое {path}:\n{files_list}")
    except Exception as e:
        logger.error(f"Ошибка при просмотре папки: {str(e)}")
        await update.message.reply_text(f"Ошибка: {str(e)}")

async def press_key(update, context):
    if not check_authorization(update):
        return

    key = " ".join(context.args) or "enter"
    try:
        pyautogui.press(key)
        await update.message.reply_text(f"Нажата клавиша: {key}")
    except Exception as e:
        logger.error(f"Ошибка при нажатии клавиши: {str(e)}")
        await update.message.reply_text(f"Ошибка: {str(e)}")

# Главная функция
def main():
    application = Application.builder().token(TOKEN).build()

    # Команды
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("screenshot", screenshot))
    application.add_handler(CommandHandler("selfie", selfie))
    application.add_handler(CommandHandler("record", record_audio))
    application.add_handler(CommandHandler("openyoutube", open_youtube))
    application.add_handler(CommandHandler("opengoogle", open_google))
    application.add_handler(CommandHandler("openinstagram", open_instagram))
    application.add_handler(CommandHandler("opengrok", open_grok))
    application.add_handler(CommandHandler("opentwitter", open_twitter))
    application.add_handler(CommandHandler("search", search))
    application.add_handler(CommandHandler("recordscreen", record_screen))
    application.add_handler(CommandHandler("recordcamera", record_camera))
    application.add_handler(CommandHandler("setvolume", set_volume))
    application.add_handler(CommandHandler("setbrightness", set_brightness))
    application.add_handler(CommandHandler("reboot", reboot))
    application.add_handler(CommandHandler("systeminfo", system_info))
    application.add_handler(CommandHandler("listdir", list_dir))
    application.add_handler(CommandHandler("presskey", press_key))

    print("Бот запущен...")
    application.run_polling()

if __name__ == "__main__":
    main()