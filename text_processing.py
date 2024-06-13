import re  # Импортируем модуль для работы с регулярными выражениями
import nltk  # Импортируем библиотеку для обработки естественного языка
from nltk.tokenize import word_tokenize  # Импортируем функцию для токенизации текста на слова
from nltk.corpus import stopwords  # Импортируем модуль для работы со стоп-словами
import pymorphy2  # Импортируем библиотеку для морфологического анализа русского языка
import cx_Oracle  # Импортируем модуль для работы с базой данных Oracle
import logging  # Импортируем модуль для логирования
from database import connect_db    # Подключение к базе данных

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Загрузка необходимых ресурсов NLTK
nltk.download('punkt')
nltk.download('stopwords')

# Инициализация анализатора морфологии для русского языка
morph = pymorphy2.MorphAnalyzer()


def lemmatize_words(words):
    """Функция для лемматизации списка слов."""
    return [morph.parse(word)[0].normal_form for word in words]  # Лемматизируем каждое слово и возвращаем список

def preprocess_text(text):
    """Функция для предобработки текста: приведение к нижнему регистру, удаление цифр и знаков препинания, удаление стоп-слов, лемматизация."""
    text = text.lower()  # Приводим текст к нижнему регистру
    text = re.sub(r'\d+', '', text)  # Удаляем цифры
    text = re.sub(r'[^\w\s]', '', text)  # Удаляем знаки препинания
    words = word_tokenize(text)  # Токенизируем текст на слова
    words = [word for word in words if word not in stopwords.words('russian')]  # Удаляем стоп-слова
    words = lemmatize_words(words)  # Лемматизируем слова
    return words  # Возвращаем список обработанных слов

# Подключаемся к базе данных
conn = connect_db()
if conn is not None:  # Проверяем, удалось ли подключиться
    cursor = conn.cursor()  # Создаем курсор для выполнения запросов
    try:
        cursor.execute("ALTER TABLE recipes ADD (list_ingrid_lem CLOB)")  # Добавляем новый столбец в таблицу
        conn.commit()  # Фиксируем изменения
    except cx_Oracle.DatabaseError as e:
        print(f"An error occurred while adding the column: {e}")  # Обрабатываем ошибку добавления столбца

    try:
        cursor.execute("SELECT RECIPE_ID, INGREDIENTS FROM recipes")  # Выполняем запрос для получения данных рецептов
        recipes = cursor.fetchall()  # Извлекаем все результаты запроса
        for recipe_id, ingredients in recipes:  # Итерируемся по всем рецептам
            # Преобразование LOB в строку, если необходимо
            if isinstance(ingredients, cx_Oracle.LOB):
                ingredients = ingredients.read()  # Читаем содержимое LOB

            processed_text = preprocess_text(ingredients)  # Обрабатываем текст ингредиентов
            processed_text_str = ' '.join(processed_text)  # Объединяем список слов в строку

            update_sql = "UPDATE recipes SET list_ingrid_lem = :1 WHERE RECIPE_ID = :2"  # SQL-запрос для обновления строки
            cursor.execute(update_sql, [processed_text_str, recipe_id])  # Выполняем запрос с параметрами
        conn.commit()  # Фиксируем изменения
    except cx_Oracle.DatabaseError as e:
        print(f"An error occurred: {e}")  # Обрабатываем ошибку выполнения запроса

# Пример предобработки текста
sample_text = "100 грамм яблок, 30г сахара и 50 грамм муки"
processed_sample = preprocess_text(sample_text)
print(processed_sample)  # Выводим результат предобработки
