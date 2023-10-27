import pandas as pd
import numpy as np
import sqlite3
import gensim
from sklearn.metrics.pairwise import cosine_similarity

from load import word2vec_model_name

model = gensim.models.Word2Vec()


# подгрузка модели gensim из файла
def load_model():
    global model
    try:
        model = gensim.models.Word2Vec.load(word2vec_model_name)
    except FileNotFoundError as error:
        print(error)
        model = gensim.models.Word2Vec()


# сохранение модели
def save_model():
    model.save("word2vec.model")


# дообучение модели на новом проекте
def train_model(project: str):
    project_tokens = project.lower().split()
    model.train(project_tokens, total_examples=1, epochs=1)


# Функция, которая превращает строчку в векторное
# представление с помощью модели Word2vec.
def get_query_vector(query):
    query_tokens = query.split()
    print(query)
    if len(query_tokens) == 0:
        query_tokens = ["Я хочу найти товарища"]
    query_vector = None
    for token in query_tokens:
        if token in model.wv.key_to_index:
            if query_vector is None:
                query_vector = np.array(model.wv[token])
            else:
                query_vector += np.array(model.wv[token])
    return query_vector.reshape(1, -1)


# Функция, которая находит в базе билет,
# наиболее подходящий под данный запрос.
def find_best_ticket(query):
    # TODO: в projects должен быть список текстовых описаний всх проектов
    projects = list()
    # Получение данных из таблицы
    # Подключение к базе данных
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    # Получение данных из таблицы
    cursor.execute("SELECT chat_id, tg_about, about FROM users")
    rows = cursor.fetchall()

    # Запись данных в список projects
    for row in rows:
        chat_id, tgabout, about = row
        projects.append((chat_id, str(tgabout) + str(about)))

    # Вывод списка projects
    # for project in projects:
    #     print(project)

    # Закрытие соединения с базой данных
    conn.close()

    query_vector = get_query_vector(query)
    best_project_index = -1
    max_distance = -1

    for i, project in enumerate(projects):
        project_vector = get_query_vector(project[1])
        if len(query_vector) > 0 and len(project_vector) > 0:
            distance = cosine_similarity(query_vector, project_vector)[0][0]
            if distance > max_distance:
                max_distance = distance
                best_project_index = i

    if best_project_index != -1:
        best_project = projects[best_project_index]
        return best_project[0]
    else:
        return None


# сохранение параметров модели обработки текстов
def backup():
    pass
