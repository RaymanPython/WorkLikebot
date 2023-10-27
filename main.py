import telebot
import sqlite3
import threading
import time
import zlib
import requests

from load import *
import embedding

model_for_search = {
    "дальше" :  "search",
    "Найти с помощью модели embdings" : "search_emb",
    "Найти с помощью модели ChatGpt3" : "search_em"
}
# добавляем обработчик для всех сообщений, чтобы отслеживать статистику
# @bot.message_handler(func=lambda message: True)
def track_message(message):
    # формируем URL запроса к Botan.io с параметрами
    url = 'https://api.botan.io/track'
    headers = {'Content-type': 'application/json'}
    data = {
        'token': token,  # замените 'YOUR_TOKEN' на токен вашего Botan.io аккаунта
        'uid': message.from_user.id,
        'message_text': message.text,
        'message_id': message.message_id,
        'chat_id': message.chat.id,
        'platform': 'Telegram',
    }
    response = requests.post(url, headers=headers, json=data)  # отправляем запрос


def update_tgname(chat_id, name):
    conn = sqlite3.connect(data_base_name)

    # Создаем курсор для выполнения запросов
    c = conn.cursor()

    with lock:
        c.execute("UPDATE users SET tgname=? WHERE chat_id=?", (name, chat_id))
        conn.commit()

    # Закрываем соединение с базой данных
    conn.close()


@bot.message_handler(commands=['start'])
def start_message(message):
    # Создаем соединение с базой данных
    conn = sqlite3.connect(data_base_name)

    # Создаем курсор для выполнения запросов
    c = conn.cursor()

    # Сохраняем chat_id и ник пользователя в базу данных
    chat_id = message.chat.id
    username = message.chat.username
    description = ""
    # description = message.from_user.about or "Описание отсутствует"
    with lock:
        c.execute("INSERT OR REPLACE INTO users (chat_id, name, tgname, tg_about) VALUES (?, ?, ?, ?)",
                  (chat_id, username, username, description))
        conn.commit()

    # Отправляем сообщение с просьбой ввести имя
    bot.send_message(chat_id, "Привет! Как тебя зовут?")

    # Устанавливаем следующий шаг - ожидание ответа с именем пользователя
    bot.register_next_step_handler(message, get_name)

    # Закрываем соединение с базой данных
    conn.close()


def get_name(message):
    # Создаем соединение с базой данных
    conn = sqlite3.connect(data_base_name)

    # Создаем курсор для выполнения запросов
    c = conn.cursor()

    # Сохраняем имя пользователя в базу данных
    name = message.text
    chat_id = message.chat.id
    username = message.chat.username
    with lock:
        c.execute("UPDATE users SET name=?, tgname=? WHERE chat_id=?", (name, username, chat_id))
        conn.commit()

    # Отправляем сообщение с кнопками "Я парень" и "Я девушка"
    keyboard = telebot.types.ReplyKeyboardMarkup(row_width=2)
    male_button = telebot.types.KeyboardButton(text="Я парень")
    female_button = telebot.types.KeyboardButton(text="Я девушка")
    keyboard.add(male_button, female_button)
    bot.send_message(chat_id, "Выбери свой пол", reply_markup=keyboard)

    # Устанавливаем следующий шаг - ожидание ответа с полом пользователя
    bot.register_next_step_handler(message, get_gender)

    # Закрываем соединение с базой данных
    conn.close()


def get_gender(message):
    # Создаем соединение с базой данных
    conn = sqlite3.connect(data_base_name)

    # Создаем курсор для выполнения запросов
    c = conn.cursor()

    # Сохраняем пол пользователя в базу данных
    chat_id = message.chat.id
    gender = 1 if message.text == "Я парень" else 0
    with lock:
        c.execute("UPDATE users SET gender=? WHERE chat_id=?", (gender, chat_id))
        conn.commit()

    # Отправляем сообщение с кнопками "Парня" и "Девушку"
    keyboard = telebot.types.ReplyKeyboardMarkup(row_width=2)
    male_button = telebot.types.KeyboardButton(text="Парня")
    female_button = telebot.types.KeyboardButton(text="Девушку")
    keyboard.add(male_button, female_button)
    bot.send_message(chat_id, "Кого ты хочешь найти?", reply_markup=keyboard)

    # Устанавливаем следующий шаг - ожидание ответа с полом, которого ищет пользователь
    bot.register_next_step_handler(message, get_search_gender)

    # Закрываем соединение с базой данных
    conn.close()


def get_search_gender(message):
    # Создаем соединение с базой данных
    conn = sqlite3.connect(data_base_name)

    # Создаем курсор для выполнения запросов
    c = conn.cursor()

    # Сохраняем пол, которого ищет пользователь, в базу данных
    chat_id = message.chat.id
    search_gender = 1 if message.text == "Парня" else 0
    username = message.chat.username
    # description = message.from_user.about
    with lock:
        c.execute("UPDATE users SET search_gender=?, tgname=?, left_key=?, right_key=? WHERE chat_id=?",
                  (search_gender, username, 1000000000, -1, chat_id))
        conn.commit()

    # Отправляем сообщение с просьбой ввести город
    bot.send_message(chat_id, "В каком городе ты живешь?", reply_markup=telebot.types.ReplyKeyboardRemove())

    # Устанавливаем следующий шаг - ожидание ответа с городом пользователя
    bot.register_next_step_handler(message, get_city)

    # Закрываем соединение с базой данных
    conn.close()


def get_city(message):
    # Создаем соединение с базой данных
    conn = sqlite3.connect(data_base_name)

    # Создаем курсор для выполнения запросов
    c = conn.cursor()
    # Сохраняем город пользователя в базу данных
    chat_id = message.chat.id
    city = message.text
    with lock:
        c.execute("UPDATE users SET city=? WHERE chat_id=?", (city, chat_id))
        conn.commit()

    # Отправляем сообщение с просьбой рассказать о себе и цели поиска
    bot.send_message(chat_id, "Расскажи немного о себе и своей цели поиска")

    # Устанавливаем следующий шаг - ожидание ответа с информацией о пользователе
    bot.register_next_step_handler(message, get_about)

    # Закрываем соединение с базой данных
    conn.close()


def get_about(message):
    # Создаем соединение с базой данных
    conn = sqlite3.connect(data_base_name)

    # Создаем курсор для выполнения запросов
    c = conn.cursor()

    # Сохраняем информацию о пользователе в базу данных
    chat_id = message.chat.id
    about = message.text
    with lock:
        c.execute("UPDATE users SET about=? WHERE chat_id=?", (about, chat_id))
        conn.commit()

    # Отправляем сообщение с просьбой добавить фото
    bot.send_message(chat_id, "Добавьте свою фотографию")

    # Устанавливаем следующий шаг - ожидание фото от пользователя
    bot.register_next_step_handler(message, save_photo)

    # Закрываем соединение с базой данных
    conn.close()


def save_photo(message):
    # Создаем соединение с базой данных
    conn = sqlite3.connect(data_base_name)

    # Создаем курсор для выполнения запросов
    c = conn.cursor()

    # Сохраняем фото пользователя в базу данных
    chat_id = message.chat.id
    if message.photo == None:
        bot.send_message(chat_id,
                         "Добавьте пожалуйста фотографию, если не хотите себя, то можете мультяшного героя похожего чем то на Вас!")
        bot.register_next_step_handler(message, save_photo)
        return
    photo_file_id = message.photo[-1].file_id

    with lock:
        c.execute("UPDATE users SET photo_file_id=? WHERE chat_id=?", (photo_file_id, chat_id))
        conn.commit()

    # Отправляем сообщение об успешной регистрации
    keyboard = telebot.types.InlineKeyboardMarkup()
    command_button = telebot.types.InlineKeyboardButton(text='Посмотреть мою анкету', callback_data='my')
    keyboard.add(command_button)
    bot.send_message(chat_id, "Ваша анкета выглядит0 так", reply_markup=keyboard)

    # Закрываем соединение с базой данных
    conn.close()


# Функция для отправки сообщения с информацией о пользователе
def send_user_info(message_chat_id, chat_id, xod=0, tgname=None):
    # Создаем соединение с базой данных
    conn = sqlite3.connect(data_base_name)
    # Создаем курсор для выполнения запросов
    c = conn.cursor()
    # Выполняем запрос на получение информации о пользователе по его chat_id
    c.execute("SELECT * FROM users WHERE chat_id=?", (chat_id,))
    user_info = c.fetchone()
    # Закрываем соединение с базой данных
    conn.close()

    # Если пользователь не найден, отправляем сообщение об ошибке
    if not user_info:
        bot.send_message(message_chat_id, 'Пользователь не найден')
        return

    # Распаковываем информацию о пользователе из кортежа
    chat_id, name, tgname, gender, search_gender, city, about, photo_file_id, _, _, *_ = user_info
    # Отправляем сообщение об успешной регистрации
    keyboard = telebot.types.InlineKeyboardMarkup()
    if message_chat_id == chat_id:
        command_button = telebot.types.InlineKeyboardButton(text='Вы можете посмотреть другие анкеты',
                                                            callback_data='search')
        keyboard.add(command_button)
    else:
        if xod != 3:
            command_button = telebot.types.InlineKeyboardButton(text='Лайк',
                                                                callback_data='like' + str(xod + 1) + str(chat_id))
            keyboard.add(command_button)
        else:
            button = telebot.types.InlineKeyboardButton(text="Перейти в чат",
                                                        url=f"https://t.me/{tgname}")
            keyboard.add(button)
        for i, j in model_for_search.items():

            command_button = telebot.types.InlineKeyboardButton(text=i,
                                                                callback_data=j)
            keyboard.add(command_button)


    # Отправляем сообщение с информацией о пользователе
    bot.send_photo(message_chat_id, photo_file_id)
    pols = ["Девушка", "Парень"]
    pols_search = ["Девушку", "Парня"]
    text = f'Имя: {name}\nПол: {pols[gender]}\nИщу: {pols_search[search_gender]}\nГород: {city}\nО себе: {about}'
    if xod == 1:
        text = "Вас кто то лайкнул\n" + text
    elif xod == 3:
        text = "Взаимный лайк\n" + text

    bot.send_message(message_chat_id, text, reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: call.data == 'my')
def command(call):
    send_user_info(call.message.chat.id, call.message.chat.id)


@bot.message_handler(commands=['find1'])
def find_message(message):
    # Создаем соединение с базой данных
    # conn = sqlite3.connect(data_base_name)

    # Создаем курсор для выполнения запросов

    # Сохраняем chat_id и ник пользователя в базу данных
    chat_id = message.chat.id
    username = message.chat.username

    # Отправляем сообщение с просьбой ввести имя
    send_user_info(chat_id, chat_id)


# @bot.message_handler(commands=['search1'])
@bot.message_handler(commands=['search'])
def search_user(message):
    # Получаем chat_id пользователя, который написал в бота
    chat_id = message.chat.id

    # Создаем соединение с базой данных
    conn = sqlite3.connect(data_base_name)
    c = conn.cursor()
    # Выполняем запрос на получение информации о пользователе по его chat_id
    c.execute("SELECT * FROM users WHERE chat_id=?", (chat_id,))
    user_info = c.fetchone()
    # Закрываем соединение с базой данных
    conn.close()

    # Если пользователь не найден, отправляем сообщение об ошибке
    if not user_info:
        bot.send_message(chat_id, 'Вы не зарегистирированы')
        return

    # Распаковываем информацию о пользователе из кортеж
    # print(len(user_info))
    chat_id, name, tgname, gender, search_gender, city, about, photo_file_id, _, lkey, rkey, *_ = user_info

    # Создаем курсор для выполнения запросов
    conn = sqlite3.connect(data_base_name)
    c = conn.cursor()
    # print(5)
    # Выполняем запрос на поиск пользователя по полю search_gender равному полю gender текущего пользователя
    if lkey == None:
        l1 = 10000000000
        r1 = -10000000000
    else:
        l1 = lkey
        r1 = rkey
    # c.execute("SELECT chat_id, uskey FROM users WHERE search_gender=? AND gender=? AND chat_id<>? AND photo_file_id IS NOT NULL AND (uskey > ? OR uskey < ?)", /
    # gender, search_gender, chat_id, r1, l1, ))
    # c.execute(
    #     "SELECT chat_id, uskey FROM users WHERE search_gender=? AND gender=? AND chat_id<>? AND photo_file_id IS NOT NULL  ORDER BY RANDOM() LIMIT 1",
    #     (gender, search_gender, chat_id,))
    c.execute(
        "SELECT chat_id, uskey FROM users WHERE search_gender=? AND gender=? AND chat_id<>? AND photo_file_id IS NOT NULL ORDER BY RANDOM() LIMIT 1",
        (gender, search_gender, chat_id,))

    # Получаем результаты запроса
    result = c.fetchone()
    # print(result)

    # Закрываем соединение с базой данных
    conn.close()

    # Если пользователь найден, отправляем его tgname, иначе сообщаем об ошибке
    if result:
        # bot.send_message(chat_id, f"Найден пользователь: {result[0]}")
        uskey = result[1]
        if lkey == None or rkey == None:
            lkey = uskey
            rkey = uskey
        else:
            rkey = max(rkey, uskey)
            lkey = min(lkey, uskey)
        send_user_info(chat_id, result[0])
    else:
        bot.send_message(chat_id, "Пользователь не найден!")
        lkey = 100000000
        rkey = -1
    conn = sqlite3.connect(data_base_name)
    c = conn.cursor()
    with lock:

        c.execute("UPDATE users SET left_key=?, right_key=? WHERE chat_id=?", (lkey, rkey, chat_id,))
        conn.commit()

    conn.close()


@bot.callback_query_handler(func=lambda call: call.data == 'search')
def command(call):
    search_user(call.message)


@bot.message_handler(commands=['search_emb'])
def search_user_emb(message):
    # Получаем chat_id пользователя, который написал в бота
    chat_id = message.chat.id

    # Создаем соединение с базой данных
    conn = sqlite3.connect(data_base_name)
    c = conn.cursor()
    # Выполняем запрос на получение информации о пользователе по его chat_id
    c.execute("SELECT * FROM users WHERE chat_id=?", (chat_id,))
    user_info = c.fetchone()
    # Закрываем соединение с базой данных
    conn.close()

    # Если пользователь не найден, отправляем сообщение об ошибке
    if not user_info:
        bot.send_message(chat_id, 'Вы не зарегистирированы')
        return

    # Распаковываем информацию о пользователе из кортеж
    # print(len(user_info))
    chat_id, name, tgname, gender, search_gender, city, about, photo_file_id, _, lkey, rkey, _, tgabout, emb = user_info

    # Создаем курсор для выполнения запросов
    # conn = sqlite3.connect(data_base_name)
    # c = conn.cursor()
    # print(5)

    # c.execute("SELECT chat_id, uskey FROM users WHERE search_gender=? AND gender=? AND chat_id<>? AND photo_file_id IS NOT NULL AND (uskey > ? OR uskey < ?)", /
    # gender, search_gender, chat_id, r1, l1, ))
    # c.execute(
    #     "SELECT chat_id, uskey FROM users WHERE search_gender=? AND gender=? AND chat_id<>? AND photo_file_id IS NOT NULL  ORDER BY RANDOM() LIMIT 1",
    #     (gender, search_gender, chat_id,))
    # c.execute(
    #     "SELECT chat_id, uskey FROM users WHERE search_gender=? AND gender=? AND chat_id<>? AND photo_file_id IS NOT NULL ORDER BY emb <-> ? LIMIT 1",
    #     (gender, search_gender, chat_id, emb, ))

    # Получаем результаты запроса
    # result = c.fetchone()
    # print(result)

    # Закрываем соединение с базой данных
    # conn.close()
    # Если пользователь найден, отправляем его tgname, иначе сообщаем об ошибке
    result = embedding.find_best_ticket(str(tgabout) + str(about))
    if result:
        send_user_info(chat_id, result)
    else:
        bot.send_message(chat_id, "Пользователь не найден!")


@bot.callback_query_handler(func=lambda call: call.data == 'search_emb')
def command_emb(call):
    search_user_emb(call.message)


# Определяем функцию-обработчик события нажатия на кнопку
@bot.callback_query_handler(func=lambda call: call.data[:4] == 'like')
def handle_query(call):
    message_chat_id = call.message.chat.id
    chat_id = call.data[5:]
    xod = int(call.data[4])
    if xod == 2:
        conn = sqlite3.connect(data_base_name)
        c = conn.cursor()
        # Выполняем запрос на получение информации о пользователе по его chat_id
        c.execute("SELECT tgname FROM users WHERE chat_id=?", (chat_id,))
        user_info = c.fetchone()
        # Закрываем соединение с базой данных
        conn.close()

        # Если пользователь не найден, отправляем сообщение об ошибке
        if not user_info:
            bot.send_message(chat_id, 'Пользователя нет')
            return

        # Распаковываем информацию о пользователе из кортежа
        tgname = user_info[0]
        send_user_info(chat_id, message_chat_id, 3, tgname=tgname)
        # bot.send_message(message_chat_id, tgname)
        conn = sqlite3.connect(data_base_name)
        c = conn.cursor()
        # Выполняем запрос на получение информации о пользователе по его chat_id
        c.execute("SELECT tgname FROM users WHERE chat_id=?", (message_chat_id,))
        user_info = c.fetchone()
        # Закрываем соединение с базой данных
        conn.close()
        tgname = user_info[0]
        send_user_info(message_chat_id, chat_id, 3, tgname=tgname)
        # bot.send_message(chat_id, tgname)
    else:
        send_user_info(chat_id, message_chat_id, xod)


@bot.message_handler(commands=['my'])
def search_my(message):
    send_user_info(message.chat.id, message.chat.id)


@bot.message_handler(commands=['find'])
def find(message):
    if len(message.text.split()) == 2:
        param = message.text.split()[1]
        # Добавьте свой код для поиска по параметру
        # Создаем соединение с базой данных
        conn = sqlite3.connect(data_base_name)

        # Создаем курсор для выполнения запросов
        c = conn.cursor()

        # Задаем параметр для поиск

        # Выполняем запрос и получаем результат
        c.execute('SELECT chat_id, name FROM users WHERE name LIKE "%" || ? || "%"', (param,))
        result = c.fetchall()

        # Выводим результат
        # print(result)

        # Закрываем соединение с базой данных
        conn.close()
        if len(result) == 0:
            bot.reply_to(message, f"Не нашлось ничего по запросу: {param}")
            return
        bot.reply_to(message, f"Вы искали по параметру: {param}")
        send_user_info(message.chat.id, result[0][0])
    else:
        bot.reply_to(message, "Неправильный формат команды /find. Используйте /find [параметр]")


# Запускаем бота
if debug:
    bot.polling()
else:
    while True:
        # python
        try:
            # код, который может вызвать ошибку
            bot.polling()
        except Exception as e:
            # обработка ошибки
            print(f"Произошла ошибка: {e}")
            print("___________________________________________________________________________________________________")
            time.sleep(50)
            continue
