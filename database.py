import cx_Oracle  # Импортируем модуль для работы с базой данных Oracle
import logging  # Импортируем модуль для логирования
from logging_config import setup_logging  # Импортируем функцию настройки логирования

setup_logging()  # Настраиваем логирование

def connect_db():
    """Функция для подключения к базе данных."""
    try:
        logging.info("Attempting to connect to the database.")  # Записываем в лог информацию о попытке подключения к базе данных
        connection = cx_Oracle.connect('c##new_admin/12345@localhost:1521/XE', encoding="UTF-8", nencoding="UTF-8")  # Подключаемся к базе данных
        logging.info("Database connection successfully established.")  # Записываем в лог информацию об успешном подключении
        return connection  # Возвращаем объект соединения
    except cx_Oracle.DatabaseError as e:  # Обрабатываем ошибку подключения к базе данных
        error, = e.args  # Извлекаем информацию об ошибке
        logging.error(f"Failed to connect to database: {error.code} {error.message}")  # Записываем в лог информацию об ошибке
        return None  # Возвращаем None в случае ошибки
