import logging  # Импортируем модуль для логирования

def setup_logging():
    """Функция для настройки логирования."""

    log_filename = 'app.log'  # Имя файла для логов
    log_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    # Создаем форматтер для записи логов в файл. Формат логов включает дату, время, уровень и сообщение

    file_handler = logging.FileHandler(log_filename, mode='a', encoding='utf-8')
    # Создаем обработчик для записи логов в файл с режимом добавления и кодировкой UTF-8
    file_handler.setFormatter(log_formatter)  # Устанавливаем форматтер для обработчика файла
    file_handler.setLevel(logging.DEBUG)  # Устанавливаем уровень логирования для файла на DEBUG

    console_handler = logging.StreamHandler()  # Создаем обработчик для вывода логов в консоль
    console_handler.setLevel(logging.INFO)  # Устанавливаем уровень логирования для консоли на INFO
    console_formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')  # Создаем другой форматтер для консоли
    console_handler.setFormatter(console_formatter)  # Устанавливаем форматтер для консоли

    # Добавляем оба обработчика (файл и консоль) к корневому логгеру
    logging.getLogger('').addHandler(file_handler)
    logging.getLogger('').addHandler(console_handler)
    logging.getLogger('').setLevel(logging.DEBUG)  # Устанавливаем общий уровень логирования на DEBUG
