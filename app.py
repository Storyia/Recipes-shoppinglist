from flask import Flask, g, request, render_template, redirect, url_for, flash, session, jsonify
'''# g - объект для хранения данных, которые будут доступны в течение одного запроса.
# request - объект для доступа к данным запроса.
# render_template - функция для рендеринга HTML шаблонов.
# redirect - функция для перенаправления пользователя на другой URL.
# url_for - функция для генерации URL-адресов для функций.
# flash - функция для отображения временных сообщений пользователю.
# session - объект для работы с сессиями пользователей.
# jsonify - функция для преобразования данных в формат JSON.'''
from functools import wraps            #Импортируем функцию wraps из модуля functools для создания декораторов.
import logging                         #модуль logging для логирования событий и ошибок.
from Recipe_Recommender import RecipeRecommender                 #класс RecipeRecommender из модуля Recipe_Recommender для работы с рекомендациями рецептов.
import helper_functions                              # Импортируем вспомогательные функции из модуля helper_functions.
from passlib.context import CryptContext                 #класс CryptContext из модуля passlib.context для работы с хэшированием паролей.
from database import connect_db                         #connect_db из модуля database для подключения к базе данных.
import cx_Oracle                                        #модуль cx_Oracle для работы с базами данных Oracle.

# Настройка контекста для хэширования паролей
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
# Создаем контекст для хэширования паролей с использованием алгоритма bcrypt.
# Параметр deprecated="auto" указывает на автоматическое устаревание устаревших схем.

logging.basicConfig(level=logging.INFO)     # Настройка логирования

app = Flask(__name__)     # Создаем экземпляр приложения Flask.

app.secret_key = b',\x1f\xe3\xbd\x80\x8e\xdb.\xb5\x13,\xc6-\xb1\xb1!'
# Устанавливаем секретный ключ для приложения Flask.
# Этот ключ используется для подписи данных сессии и защиты от подделки.

tfidf_model_path = 'tfidf_model.pkl'    # Указываем путь к файлу с моделью TF-IDF.

# Создание экземпляра рекомендателя
try:
    db_connection = connect_db()  # Подключение к базе данных
    if not db_connection:
        raise Exception("Failed to connect to the database.")
    recommender = RecipeRecommender(tfidf_model_path, db_connection)  # Инициализация рекомендателя
    logging.info("Models and database connection initialized successfully.")
except Exception as e:
    logging.critical(f"Error initializing models or database connection: {e}")

def convert_lobs_to_strings(data):
    """Преобразует LOB-объекты базы данных в строки."""
    if isinstance(data, cx_Oracle.LOB):
        # Если данные являются объектом LOB (Large Object Binary) из базы данных Oracle,
        # то читаем содержимое LOB и преобразуем его в строку.
        return data.read()
    elif isinstance(data, dict):
        # Если данные являются словарем, то рекурсивно применяем функцию convert_lobs_to_strings
        # ко всем значениям словаря.
        return {key: convert_lobs_to_strings(value) for key, value in data.items()}
    elif isinstance(data, list):
        # Если данные являются списком, то рекурсивно применяем функцию convert_lobs_to_strings
        # ко всем элементам списка.
        return [convert_lobs_to_strings(item) for item in data]
    # Если данные не являются ни LOB, ни словарем, ни списком, возвращаем их без изменений.
    return data

def process_input(data):
    """Обрабатывает вводимые данные, удаляя пробелы и разделяя по запятым."""
    # Разделяем строку на подстроки по запятым, удаляем пробелы вокруг подстрок,
    # фильтруем пустые строки и возвращаем список обработанных строк.
    processed_data = [item.strip() for item in data.split(',') if item.strip()]
    return processed_data

@app.before_request
def pre_process_all_requests():
    """Обрабатывает все запросы перед их выполнением. Проверяет, авторизован ли пользователь."""
    # Получаем идентификатор пользователя из сессии.
    user_id = session.get('user_id')
    if user_id:
        # Если идентификатор пользователя существует, получаем информацию о пользователе.
        user = helper_functions.get_user_by_id(user_id)
        if user:
            # Если пользователь найден, сохраняем информацию о текущем пользователе и помечаем, что пользователь вошел в систему.
            g.current_user = user
            g.logged_in = True
        else:
            # Если пользователь не найден, удаляем идентификатор пользователя из сессии и помечаем, что пользователь не вошел в систему.
            session.pop('user_id', None)
            g.logged_in = False
            g.current_user = None
    else:
        # Если идентификатор пользователя не существует, помечаем, что пользователь не вошел в систему.
        g.logged_in = False
        g.current_user = None


def login_required(f):
    """Декоратор для защиты маршрутов, требующих аутентификации."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Проверяем, есть ли текущий пользователь
        if g.current_user is None:
            # Если пользователь не авторизован, перенаправляем его на главную страницу
            # и сохраняем URL, на который он пытался попасть, для последующего редиректа
            return redirect(url_for('display_homepage', next=request.url))
        # Если пользователь авторизован, выполняем целевую функцию
        return f(*args, **kwargs)
    return decorated_function

@app.route("/", methods=['GET', 'POST'])
def display_homepage():
    """Отображает главную страницу. При POST-запросе перенаправляет на домашнюю страницу."""
    if request.method == 'POST':
        # Если запрос POST, перенаправляем пользователя на домашнюю страницу
        return redirect(url_for('home'))
    # Если запрос GET, отображаем HTML шаблон главной страницы
    return render_template("homepage.html")

@app.route("/login", methods=['POST'])
def validate_login_info():
    """Обрабатывает данные формы входа, проверяет учетные данные и перенаправляет пользователя."""
    username = request.form["username"]  # Получаем имя пользователя из формы
    password = request.form["password"]  # Получаем пароль из формы
    hash = pwd_context.hash(password)  # Хэшируем введенный пароль для последующей проверки
    verified = pwd_context.verify(password, hash)  # Проверяем введенный пароль с хэшом
    existing_user = helper_functions.check_if_user_exists(username)  # Проверяем, существует ли пользователь с таким именем
    if not existing_user or not verified:
        # Если пользователь не найден или пароль неверный, показываем сообщение об ошибке
        flash("Invalid username or password.")
        return redirect("/")  # Перенаправляем пользователя на главную страницу
    session["user_id"] = existing_user.user_id  # Сохраняем идентификатор пользователя в сессии
    return redirect("/dashboard")  # Перенаправляем пользователя на страницу панели управления

@app.route("/logout")
def logout_user():
    """Выход пользователя из системы."""
    # Удаляем идентификатор пользователя из сессии.
    session.pop('user_id', None)
    # Отображаем сообщение о выходе из системы.
    flash("Вы вышли из системы. До скорой встречи!")
    # Перенаправляем пользователя на главную страницу.
    return redirect("/")

@app.route("/register", methods=['POST'])
def process_registration_form():
    """Добавляет информацию о пользователе в базу данных. При успешной регистрации выполняет вход и перенаправляет на страницу панели управления."""
    # Получаем данные из формы регистрации.
    username = request.form["username"]
    email = request.form["email"]
    password = request.form["password"]

    # Проверка, занят ли уже логин.
    username_exists = helper_functions.check_if_user_exists(username)

    if username_exists:
        # Если имя пользователя уже занято, отображаем сообщение и перенаправляем на главную страницу.
        flash("{} уже занято. Попробуй еще раз!".format(username))
        return redirect("/")

    # Добавление нового пользователя.
    new_user = helper_functions.add_user(username, email, password)
    # Отображаем сообщение о успешной регистрации.
    flash("Спасибо за регистрацию {}!".format(username))
    # Сохраняем идентификатор нового пользователя в сессии.
    session["user_id"] = new_user.user_id

    # Перенаправляем пользователя на страницу панели управления.
    return redirect("/dashboard")

@app.route("/my-profile")
@login_required
def display_profile():
    """Отображает профиль пользователя с его именем, электронной почтой и сохраненными рецептами."""
    if 'username' in g.current_user and 'email' in g.current_user:
        # Если информация о пользователе доступна, отображаем профиль пользователя.
        return render_template("user_profile.html",
                               username=g.current_user['username'],
                               email=g.current_user['email'])
    else:
        # Если информация о пользователе недоступна, отображаем сообщение об ошибке и перенаправляем на главную страницу.
        flash("Ошибка загрузки пользователя.")
        return redirect(url_for('display_homepage'))


@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def home():
    """Отображает домашнюю страницу с рекомендациями рецептов."""
    user_id = g.current_user.get('user_id')  # Получаем идентификатор текущего пользователя
    if user_id:
        # Если пользователь авторизован, получаем списки пользователя
        user_lists = helper_functions.get_user_lists(user_id)
    else:
        # Если пользователь не авторизован, создаем пустой список
        user_lists = []

    if request.method == 'GET':
        # Если запрос GET, удаляем из сессии предыдущие рекомендации и сообщения
        session.pop('recommendations', None)
        session.pop('message', None)

    # Получаем рекомендации и сообщения из сессии, если они есть
    recommendations = session.get('recommendations', [])
    message = session.get('message', "Введите ингредиенты для поиска рецептов")

    if request.method == 'POST':
        # Если запрос POST, обрабатываем входные данные
        ingredients_input = request.form['hidden-ingredients']  # Получаем ингредиенты из формы
        allergies_input = request.form.get('hidden-allergies', '')  # Получаем аллергены из формы, если есть

        # Обрабатываем входные данные
        processed_ingredients = process_input(ingredients_input)
        processed_allergies = process_input(allergies_input)

        # Сохраняем обработанные ингредиенты в сессии
        session['user_ingredients'] = processed_ingredients

        # Получаем рекомендации рецептов на основе ингредиентов и аллергенов
        recommendations, message = recommender.recommend_recipes(processed_ingredients, processed_allergies)
        if recommendations:
            # Если есть рекомендации, сохраняем их в сессии
            recommendations = [(convert_lobs_to_strings(rec), sim) for rec, sim in recommendations]
            session['recommendations'] = recommendations
            session['message'] = message
        else:
            # Если рекомендаций нет, удаляем их из сессии и устанавливаем сообщение
            message = "Рекомендации не найдены."
            session.pop('recommendations', None)
            session.pop('message', None)

    # Рендерим шаблон dashboard.html с рекомендациями, списками пользователя и сообщением
    return render_template('dashboard.html', recommendations=recommendations, user_lists=user_lists, message=message)


@app.route("/displayNewList", methods=['POST'])
@login_required
def process_new_list():
    """Обрабатывает создание нового списка покупок."""
    # Получаем название нового списка из формы.
    new_list_name = request.form["new_list_name"]
    # Получаем идентификатор текущего пользователя.
    user_id = g.current_user.get('user_id')

    # Проверяем, что название списка не пустое.
    if not new_list_name.strip():
        flash("Введите название списка покупок.")
        return redirect("/dashboard")

    # Если пользователь авторизован.
    if user_id:
        # Проверяем, существует ли уже список с таким названием у текущего пользователя.
        list_exists = helper_functions.check_if_list_exists(user_id, new_list_name)
        if not list_exists:
            # Если список не существует, создаем новый список.
            helper_functions.add_new_list(user_id, new_list_name)
            flash("Новый список успешно создан.")
        else:
            # Если список уже существует, отображаем сообщение об ошибке
            flash("Такой список уже существует. Попробуй другое название.")

        # Восстанавливаем рекомендации и сообщение из сессии.
        recommendations = session.get('recommendations', [])
        message = session.get('message', "Введите ингредиенты для поиска рецептов.")
        # Перенаправляем пользователя на домашнюю страницу.
        return redirect(url_for('home', recommendations=recommendations, message=message))
    else:
        # Если пользователь не авторизован, отображаем сообщение об ошибке
        flash("Пользователь не авторизован")
        return redirect("/")

@app.route('/get-list-contents', methods=['POST'])
@login_required
def get_list_contents():
    """Возвращает содержимое списка покупок в формате JSON"""
    # Получаем идентификатор списка из формы.
    list_id = request.form['list_id']
    # Получаем содержимое списка с помощью вспомогательной функции.
    list_contents = helper_functions.get_list_contents(list_id)
    # Возвращаем содержимое списка в формате JSON.
    return jsonify(list_contents)

@app.route('/add-to-list', methods=['POST'])
@login_required
def add_recipe_to_list():
    """Добавляет ингредиенты рецепта в список покупок."""
    # Получаем идентификатор пользователя, рецепт и список из формы
    user_id = g.current_user['user_id']
    recipe_id = request.form['recipe_id']
    list_id = request.form['list_id']

    # Получаем детали рецепта с помощью вспомогательной функции.
    recipe_details = helper_functions.find_recipe_by_id(recipe_id)
    if recipe_details:
        # Если рецепт найден, добавляем ингредиенты в список покупок.
        helper_functions.add_ingredients_to_list(list_id, recipe_details['INGREDIENTS'], recipe_details['RECIPE_ID'])
        flash('Ингредиенты успешно добавлены в список покупок.')
    else:
        # Если рецепт не найден, отображаем сообщение об ошибке
        flash('Ошибка поиска рецепта по ID.')

    # Возвращаем статус успеха в формате JSON
    return jsonify({'status': 'success'})

if __name__ == '__main__':
    # Запуск приложения Flask
    app.run(debug=True)

