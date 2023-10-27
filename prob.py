import sqlite3
import openai


# Установка ключа API
openai.api_key = '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'


# Подключение к базе данных
conn = sqlite3.connect('users.db')
cursor = conn.cursor()


# Ввод описания через консоль
description = input("Введите описание человека: ")

# Использование OpenAI API для поиска максимально подходящего описания
search_query = f"SELECT * FROM users WHERE description LIKE '%{description}%'"
openai_response = openai.Completion.create(
    engine="text-davinci-003",
    prompt=search_query,
    max_tokens=100,
    n=1,
    stop=None,
    temperature=0.7,
)

# Получение результатов от OpenAI API
search_results = openai_response.choices[0].text.strip().split('\n')

# Вывод результатов
if len(search_results) > 0:
    print("Найдены следующие пользователи:")
    for result in search_results:
        print(result)
        print()
else:
    print("Пользователи с таким описанием не найдены")

# Закрытие соединения с базой данных
conn.close()
