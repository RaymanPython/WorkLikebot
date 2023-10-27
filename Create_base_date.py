import sqlite3

# Создаем соединение с базой данных
conn = sqlite3.connect('users.db')

# Создаем курсор для выполнения запросов
c = conn.cursor()

# Создаем таблицу users с полями chat_id, name, tgname, gender, search_gender, city, about, photo_file_id, uskey, left_key, right_key
c.execute('''CREATE TABLE IF NOT EXISTS users
             (chat_id INTEGER PRIMARY KEY,
              name TEXT,
              tgname TEXT,
              gender INTEGER,
              search_gender INTEGER,
              city TEXT,
              about TEXT,
              photo_file_id TEXT,
              uskey INTEGER,
              left_key INTEGER,
              right_key INTEGER)''')

# Создаем триггер для автоматического присвоения значения поля uskey при создании пользователя
c.execute('''CREATE TRIGGER IF NOT EXISTS set_uskey_on_insert
             AFTER INSERT ON users
             BEGIN
                 UPDATE users SET uskey = CASE WHEN (SELECT COUNT(*) FROM users) = 1 THEN 1 ELSE (SELECT MAX(uskey) + 1 FROM users) END WHERE chat_id = NEW.chat_id;
             END''')

# Закрываем соединение с базой данных
conn.close()