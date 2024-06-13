from database import connect_db  # Импортируем функцию для подключения к базе данных
import logging  # Импортируем модуль для логирования
from passlib.context import CryptContext  # Импортируем контекст для работы с паролями
import cx_Oracle  # Импортируем модуль для работы с базой данных Oracle
import re  # Импортируем модуль для работы с регулярными выражениями

# Определение класса User
class User:
    def __init__(self, user_id, username, email):
        self.user_id = user_id  # Идентификатор пользователя
        self.username = username  # Имя пользователя
        self.email = email  # Электронная почта пользователя

# Настройка контекста для хэширования паролей
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Пользователи
def check_if_user_exists(username):
    """Проверяет, существует ли пользователь. Возвращает объект User или None."""
    conn = connect_db()  # Подключаемся к базе данных
    if conn:
        cursor = conn.cursor()  # Создаем курсор для выполнения запросов
        try:
            sql = "SELECT user_id, username, email FROM users WHERE username = :username"
            cursor.execute(sql, [username])  # Выполняем SQL-запрос
            row = cursor.fetchone()  # Извлекаем первую строку результата запроса
            if row:
                logging.info(f"User found: {row}")  # Логируем успешное нахождение пользователя
                return User(*row)  # Создаем и возвращаем объект User
        finally:
            cursor.close()  # Закрываем курсор
            conn.close()  # Закрываем соединение с базой данных
    logging.info("User not found.")  # Логируем отсутствие пользователя
    return None  # Возвращаем None, если пользователь не найден

def add_user(username, email, password):
    """Добавляет нового пользователя в базу данных."""
    conn = connect_db()  # Подключаемся к базе данных
    if conn:
        hashed_password = pwd_context.hash(password)  # Хэшируем пароль
        cursor = conn.cursor()  # Создаем курсор для выполнения запросов
        try:
            sql = "INSERT INTO users (username, email, password) VALUES (:username, :email, :password)"
            params = {'username': username, 'email': email, 'password': hashed_password}
            cursor.execute(sql, params)  # Выполняем SQL-запрос для добавления пользователя
            conn.commit()  # Фиксируем изменения
        finally:
            cursor.close()  # Закрываем курсор
            conn.close()  # Закрываем соединение с базой данных

def get_user_by_id(user_id):
    """Получает данные пользователя по его ID."""
    conn = connect_db()  # Подключаемся к базе данных
    if conn:
        cursor = conn.cursor()  # Создаем курсор для выполнения запросов
        try:
            sql = "SELECT user_id, username, email, password FROM users WHERE user_id = :user_id"
            cursor.execute(sql, {'user_id': user_id})  # Выполняем SQL-запрос
            user_data = cursor.fetchone()  # Извлекаем первую строку результата запроса
            if user_data:
                return {'user_id': user_data[0], 'username': user_data[1], 'email': user_data[2]}  # Возвращаем данные пользователя
        except Exception as e:
            logging.error(f"Error fetching user by ID: {e}")  # Логируем ошибку
        finally:
            cursor.close()  # Закрываем курсор
            conn.close()  # Закрываем соединение с базой данных
    return None  # Возвращаем None, если данные пользователя не найдены

# Рецепты
def check_if_list_exists(user_id, list_name):
    """Проверяет, существует ли список по имени и ID пользователя."""
    conn = connect_db()  # Подключаемся к базе данных
    if conn:
        cursor = conn.cursor()  # Создаем курсор для выполнения запросов
        try:
            sql = "SELECT 1 FROM lists WHERE user_id = :user_id AND list_name = :list_name"
            cursor.execute(sql, [user_id, list_name])  # Выполняем SQL-запрос
            return cursor.fetchone() is not None  # Возвращаем True, если список найден
        finally:
            cursor.close()  # Закрываем курсор
            conn.close()  # Закрываем соединение с базой данных

def add_new_list(user_id, list_name):
    """Создает новый список покупок и добавляет его в базу данных."""
    conn = connect_db()  # Подключаемся к базе данных
    if conn:
        cursor = conn.cursor()  # Создаем курсор для выполнения запросов
        try:
            sql = "INSERT INTO lists (user_id, list_name) VALUES (:user_id, :list_name)"
            cursor.execute(sql, [user_id, list_name])  # Выполняем SQL-запрос для добавления списка
            conn.commit()  # Фиксируем изменения
        finally:
            cursor.close()  # Закрываем курсор
            conn.close()  # Закрываем соединение с базой данных

def get_user_lists(user_id):
    """Получение всех списков пользователя по его ID."""
    conn = connect_db()  # Подключаемся к базе данных
    if conn:
        cursor = conn.cursor()  # Создаем курсор для выполнения запросов
        try:
            sql = "SELECT list_id, list_name FROM lists WHERE user_id = :user_id"
            cursor.execute(sql, {'user_id': user_id})  # Выполняем SQL-запрос
            lists = [{'list_id': row[0], 'list_name': row[1]} for row in cursor.fetchall()]  # Формируем список словарей
            return lists  # Возвращаем списки пользователя
        except Exception as e:
            logging.error(f"Error fetching user lists: {e}")  # Логируем ошибку
            return []
        finally:
            cursor.close()  # Закрываем курсор
            conn.close()  # Закрываем соединение с базой данных

def get_list_contents(list_id):
    """Отображение содержимого выбранного списка покупок."""
    conn = connect_db()  # Подключаемся к базе данных
    if conn:
        cursor = conn.cursor()  # Создаем курсор для выполнения запросов
        try:
            sql = "SELECT list_id, INGREDIENTS FROM list_ingredients WHERE list_id = :list_id"
            cursor.execute(sql, {'list_id': list_id})  # Выполняем SQL-запрос
            list_contents = []
            for row in cursor.fetchall():  # Итерируемся по всем строкам результата запроса
                list_contents.append({'INGREDIENTS': row[1]})  # Добавляем ингредиенты в список
            return list_contents  # Возвращаем содержимое списка
        except Exception as e:
            logging.error(f"Error fetching list contents: {e}")  # Логируем ошибку
            return []
        finally:
            cursor.close()  # Закрываем курсор
            conn.close()  # Закрываем соединение с базой данных

def check_if_recipe_exists(recipe_id):
    """Проверяет, существует ли рецепт по ID."""
    conn = connect_db()  # Подключаемся к базе данных
    if conn:
        cursor = conn.cursor()  # Создаем курсор для выполнения запросов
        try:
            sql = "SELECT 1 FROM recipes WHERE recipe_id = :recipe_id"
            cursor.execute(sql, [recipe_id])  # Выполняем SQL-запрос
            return cursor.fetchone() is not None  # Возвращаем True, если рецепт найден
        finally:
            cursor.close()  # Закрываем курсор
            conn.close()  # Закрываем соединение с базой данных

def get_ingredients_to_add_to_list(self, recipe_ingredients):
    """Возвращает список ингредиентов для добавления в список покупок."""
    if isinstance(recipe_ingredients, str):
        recipe_ingredients_list = self.split_ingredients(recipe_ingredients)  # Разделяем строку ингредиентов на список
    else:
        recipe_ingredients_list = recipe_ingredients  # Если ингредиенты уже список, используем его напрямую
    return [ing for ing in recipe_ingredients_list]  # Возвращаем список ингредиентов

def convert_lobs_to_strings(data):
    """Преобразует LOB-объекты в строки."""
    if isinstance(data, cx_Oracle.LOB):
        try:
            return data.read()  # Читаем содержимое LOB
        except Exception as e:
            logging.error(f"Error reading CLOB data: {e}")  # Логируем ошибку
            return None  # Возвращаем None в случае ошибки
    return data  # Возвращаем данные без изменений, если это не LOB

def split_ingredients(ingredients_text):
    """Разделяет текст ингредиентов на отдельные ингредиенты."""
    if not isinstance(ingredients_text, str):
        logging.error(f"Expected string, got {type(ingredients_text).__name__}")  # Логируем ошибку
        return []
    return re.findall(r'([А-Я][^А-Я]*)', ingredients_text)  # Используем регулярное выражение для разделения ингредиентов

def find_recipe_by_id(recipe_id):
    """Находит рецепт по его ID."""
    conn = connect_db()  # Подключаемся к базе данных
    if not conn:
        logging.error("No database connection available.")  # Логируем ошибку
        return None

    try:
        cursor = conn.cursor()  # Создаем курсор для выполнения запросов
        cursor.execute(
            "SELECT RECIPE_ID, NAME, INGREDIENTS, RECIPE FROM recipes WHERE RECIPE_ID = :id",
            {'id': recipe_id})  # Выполняем SQL-запрос
        row = cursor.fetchone()  # Извлекаем первую строку результата запроса
        if row:
            recipe_id, name, ingredients_text, recipe_text = row
            logging.info(f"Recipe found: {name} with ingredients: {ingredients_text}")  # Логируем успешное нахождение рецепта
            ingredients_text = convert_lobs_to_strings(ingredients_text)  # Преобразуем LOB в строку
            if isinstance(ingredients_text, str):
                ingredients = split_ingredients(ingredients_text)  # Разделяем ингредиенты на список
                return {
                    'RECIPE_ID': recipe_id,
                    'NAME': name,
                    'INGREDIENTS': ingredients,
                    'RECIPE': recipe_text
                }
            else:
                logging.error(f"Unexpected type for ingredients_text: {type(ingredients_text)}")  # Логируем ошибку типа данных
        else:
            logging.info(f"No recipe found with ID {recipe_id}")  # Логируем отсутствие рецепта
    except Exception as e:
        logging.error(f"Error fetching recipe by ID: {e}")  # Логируем ошибку
    finally:
        cursor.close()  # Закрываем курсор
        conn.close()  # Закрываем соединение с базой данных

def add_ingredients_to_list(list_id, ingredients, recipe_id):
    """Добавляет ингредиенты в список покупок."""
    conn = connect_db()  # Подключаемся к базе данных
    if conn:
        cursor = conn.cursor()  # Создаем курсор для выполнения запросов
        try:
            for ingredient in ingredients:
                ingredient_str = convert_lobs_to_strings(ingredient)  # Преобразуем LOB в строку
                sql_check = "SELECT 1 FROM list_ingredients WHERE list_id = :list_id AND ingredients = :ingredient AND recipe_id = :recipe_id"
                cursor.execute(sql_check, {'list_id': list_id, 'ingredient': ingredient_str, 'recipe_id': recipe_id})  # Проверяем, существует ли ингредиент
                if not cursor.fetchone():
                    sql_insert = "INSERT INTO list_ingredients (list_id, recipe_id, ingredients) VALUES (:list_id, :recipe_id, :ingredient)"
                    cursor.execute(sql_insert, {'list_id': list_id, 'recipe_id': recipe_id, 'ingredient': ingredient_str})  # Добавляем ингредиент
            conn.commit()  # Фиксируем изменения
        except Exception as e:
            logging.error(f"Error adding ingredients to list: {e}")  # Логируем ошибку
            conn.rollback()  # Откатываем изменения в случае ошибки
        finally:
            cursor.close()  # Закрываем курсор
            conn.close()  # Закрываем соединение с базой данных
