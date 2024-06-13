import pandas as pd  # Импортируем библиотеку для работы с табличными данными
import pickle  # Импортируем модуль для сериализации объектов
import logging  # Импортируем модуль для логирования
import cx_Oracle  # Импортируем модуль для работы с базой данных Oracle
from sklearn.feature_extraction.text import TfidfVectorizer  # Импортируем класс для работы с TF-IDF векторизацией
import pymorphy2  # Импортируем библиотеку для морфологического анализа русского языка
from database import connect_db  # Импортируем функцию для подключения к базе данных

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Инициализация анализатора морфологии для русского языка
morph = pymorphy2.MorphAnalyzer()

# Глобальные переменные
FIT_COLUMN = "LIST_INGRID_LEM"
PREDICT_COLUMN = "RECIPE"

def splinst(inst):
    """ Преобразует текст в строку, нормализуя слова. """
    if isinstance(inst, list):
        inst = " ".join(inst)  # Если это список, объединяем в строку
    elif not isinstance(inst, str):
        inst = str(inst)  # Преобразуем в строку, если это не строка и не список

    result = []
    words = inst.split()  # Разбиваем текст на слова
    for word in words:
        word = word.lower()  # Приводим слово к нижнему регистру
        if len(word) > 2:
            if ord(word[-1]) < 1072 or ord(word[-1]) > 1103:
                word = word[:-1]  # Убираем последний символ, если он не в диапазоне кириллических букв
            if ord(word[0]) < 1072 or ord(word[0]) > 1103:
                word = word[1:]  # Убираем первый символ, если он не в диапазоне кириллических букв
            parsed_word = morph.parse(word)[0]
            result.append(parsed_word.normal_form if parsed_word else "")  # Лемматизируем слово
        else:
            result.append("")  # Добавляем пустую строку для слов длиной 2 или меньше
    return " ".join(result)  # Объединяем слова обратно в строку

def create_text_for_vectorizer(text):
    """ Увеличивает количество вхождений важных слов в текст для векторизации. """
    words = text.split()  # Разбиваем текст на слова
    result = []
    for i, word in enumerate(words):
        result.extend([word] * int(max(6 // (0.5 * i + 1), 1)))  # Увеличиваем количество вхождений слов
    return " ".join(result)  # Объединяем слова обратно в строку

def prepare_dataset(df):
    """ Подготавливает датасет для обучения модели, применяя нормализацию и векторизацию. """

    # Конвертация cx_Oracle LOB в строку
    df['LIST_INGRID_LEM'] = df['LIST_INGRID_LEM'].apply(lambda x: x.read() if isinstance(x, cx_Oracle.LOB) else x)

    # Подготовка текста для векторизации лемматизированных ингредиентов
    df['processed_ingridients'] = df['LIST_INGRID_LEM'].apply(create_text_for_vectorizer)

    # Нормализация текста инструкций
    df['processed_instructions'] = df['RECIPE'].apply(splinst)

    return df

def fit_and_save_model(df):
    """ Обучает модель TF-IDF на всем датасете и сохраняет её. """
    vectorizer = TfidfVectorizer()
    X = vectorizer.fit_transform(df['processed_ingridients'])  # Обучаем модель TF-IDF на лемматизированных ингредиентах

    # Сохранение обученной модели
    with open("tfidf_model.pkl", "wb") as f:
        pickle.dump(vectorizer, f)  # Сериализуем и сохраняем модель в файл
    logging.info("Model trained and saved successfully.")  # Логируем успешное сохранение модели
    return vectorizer

def main():
    conn = connect_db()  # Подключаемся к базе данных
    if conn:  # Проверяем, удалось ли подключиться
        cursor = conn.cursor()  # Создаем курсор для выполнения запросов
        cursor.execute("SELECT recipe_id, name, recipe, list_ingrid_lem FROM recipes")  # Выполняем запрос к базе данных
        data = cursor.fetchall()  # Извлекаем все данные из результата запроса
        df = pd.DataFrame(data, columns=['recipe_id', 'name', 'RECIPE', 'LIST_INGRID_LEM'])  # Создаем DataFrame из полученных данных

        if not df.empty and 'RECIPE' in df and 'LIST_INGRID_LEM' in df:  # Проверяем, что DataFrame не пуст и содержит нужные столбцы
            df_norm = prepare_dataset(df)  # Подготавливаем датасет для обучения модели
            vectorizer = fit_and_save_model(df_norm)  # Обучаем и сохраняем модель TF-IDF

            # Проверка, включено ли слово "тунец" в словарь модели
            if 'тунец' in vectorizer.vocabulary_:
                logging.info("Word 'тунец' is in the model.")  # Логируем, если слово "тунец" присутствует в словаре модели
            else:
                logging.info("Word 'тунец' is not in the model.")  # Логируем, если слово "тунец" отсутствует в словаре модели
        else:
            logging.error("No data to process or missing columns.")  # Логируем ошибку, если данные отсутствуют или не содержат нужных столбцов
    else:
        logging.error("Failed to connect to the database.")  # Логируем ошибку, если не удалось подключиться к базе данных

if __name__ == "__main__":
    main()  # Запускаем основную функцию, если скрипт выполняется напрямую
