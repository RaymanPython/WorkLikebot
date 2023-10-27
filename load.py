import telebot
import threading
import os
from dotenv import load_dotenv

data_base_name = 'users.db'
word2vec_model_name = "word2vec.model"
token = '6156683874:AAH3_uy_scIQSfcALGsItsI17hkNN9d3YfE'

# Загрузка переменных окружения из файла .env
load_dotenv()

# Получение значения токена бота
bot_token = os.getenv("BOT_TOKEN")

# получаем название базы файла с базой данных
ata_base_name = os.getenv("DB_NAME")

# Получение значения переменной debug (по умолчанию False)
debug = os.getenv("DEBUG", False)

print("Токен бота:", bot_token)
print("Debug режим:", debug)

# Создаем объект блокировки для доступа к базе данных
lock = threading.Lock()

# Создаем объект бота
bot = telebot.TeleBot(token)

# устанавливаем лимит в 10 сообщений в очереди для каждого chat.id
bot.message_queue = (telebot.util.Queue.Queue(maxsize=5))


# инициализация моделей
def on_startup(_):
    pass


# функция, которая будет вызываться по выключению бота
# сохранение всех данных
def on_shutdown(_):
    pass
