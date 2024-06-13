from sklearn.neighbors import NearestNeighbors  # Импортируем NearestNeighbors для KNN
import cx_Oracle  # Импортируем cx_Oracle для работы с базой данных Oracle
import logging  # Импортируем logging для логирования
import pickle  # Импортируем pickle для загрузки модели
from logging_config import setup_logging  # Импортируем настройку логирования
from database import connect_db  # Импортируем функцию подключения к базе данных

setup_logging()  # Настраиваем логирование

class RecipeRecommender:
    # Словарь аллергенов и связанных с ними продуктов
    allergen_map = {
        "лактоза": ["молоко", "сметана", "творог", "сыр", "масло", "кефир", "йогурт", "сливки"],
        "глютен": ["пшеница", "рожь", "ячмень", "овес", "манка", "сейтан"],
        "орехи": ["миндаль", "фундук", "грецкий орех", "каштан", "пекан", "фисташки", "арахис"]
    }

    def __init__(self, model_path, connection):
        with open(model_path, 'rb') as f:  # Открываем файл с моделью для чтения в бинарном режиме
            self.model = pickle.load(f)  # Загружаем модель TF-IDF из файла
        logging.info("TF-IDF model loaded.")  # Логируем успешную загрузку модели
        self.connection = connection  # Сохраняем соединение с базой данных
        if self.connection:  # Проверяем, удалось ли установить соединение
            logging.info("Database connection successfully established.")  # Логируем успешное подключение к базе данных
        else:
            logging.error("Database connection failed.")  # Логируем ошибку подключения к базе данных

    def fetch_recipes_data(self):
        if not self.connection:  # Проверяем наличие соединения с базой данных
            logging.error("No database connection available.")  # Логируем ошибку, если нет соединения
            return []  # Возвращаем пустой список
        cursor = self.connection.cursor()  # Создаем курсор для выполнения SQL-запросов
        cursor.execute("SELECT RECIPE_ID, NAME, INGREDIENTS, RECIPE, LIST_INGRID_LEM FROM recipes")  # Выполняем SQL-запрос для получения данных рецептов
        recipes = []  # Инициализируем пустой список для хранения рецептов
        for row in cursor.fetchall():  # Итерируемся по результатам запроса
            recipe_id, name, ingredients_text, recipe_text, list_ingrid_lem = row  # Извлекаем данные рецепта
            if isinstance(list_ingrid_lem, cx_Oracle.LOB):  # Проверяем, является ли список ингредиентов LOB-объектом
                list_ingrid_lem = list_ingrid_lem.read()  # Преобразуем LOB в строку
            if isinstance(ingredients_text, cx_Oracle.LOB):  # Проверяем, является ли текст ингредиентов LOB-объектом
                ingredients_text = ingredients_text.read()  # Преобразуем LOB в строку
            ingredients = list_ingrid_lem if isinstance(list_ingrid_lem, str) else ""  # Если список ингредиентов строка, сохраняем его, иначе пустая строка
            recipes.append({
                'RECIPE_ID': recipe_id,  # ID рецепта
                'NAME': name,  # Название рецепта
                'RECIPE': recipe_text,  # Текст рецепта
                'INGREDIENTS': ingredients_text,  # Ингредиенты рецепта
                'LIST_INGRID_LEM': ingredients.split(' ')  # Список ингредиентов
            })
            logging.debug(f"Recipe {name} fetched successfully")  # Логируем успешное получение рецепта
        cursor.close()  # Закрываем курсор
        logging.info(f"Total {len(recipes)} recipes fetched from the database.")  # Логируем общее количество полученных рецептов
        return recipes  # Возвращаем список рецептов

    def vectorize_ingredients(self, ingredients):
        ingredients_text = ' '.join(ingredients).lower()  # Преобразуем список ингредиентов в строку и приводим к нижнему регистру
        print("Vectorizing:", ingredients_text)  # Выводим информацию о векторизации
        ingredient_vector = self.model.transform([ingredients_text])  # Преобразуем текст ингредиентов в вектор с помощью модели TF-IDF
        print("Vector shape:", ingredient_vector.shape)  # Выводим форму вектора
        print("Non-zero elements:", ingredient_vector.nnz)  # Выводим количество ненулевых элементов в векторе
        return ingredient_vector  # Возвращаем вектор ингредиентов

    def recommend_recipes(self, user_ingredients, allergies=[], top_n=10):
        recipes = self.fetch_recipes_data()  # Получаем данные рецептов из базы данных
        if not recipes:  # Проверяем, есть ли рецепты
            return [], "No recipes found in database."  # Возвращаем пустой список и сообщение, если рецептов нет

        expanded_allergens = []  # Инициализируем список для расширенных аллергенов
        for allergy in allergies:  # Итерируемся по списку аллергий
            if allergy.lower() in RecipeRecommender.allergen_map:  # Проверяем, есть ли аллергия в карте аллергенов
                expanded_allergens.extend(RecipeRecommender.allergen_map[allergy.lower()])  # Добавляем соответствующие продукты в список
            else:
                expanded_allergens.append(allergy)  # Добавляем аллергию в список, если её нет в карте аллергенов

        user_vector = self.vectorize_ingredients(user_ingredients)  # Векторизуем ингредиенты пользователя
        recipe_vectors = []  # Инициализируем список для векторов рецептов
        for recipe in recipes:  # Итерируемся по рецептам
            recipe_ingredients = ' '.join([ingr.lower() for ingr in recipe['LIST_INGRID_LEM']])  # Объединяем ингредиенты рецепта в строку и приводим к нижнему регистру
            recipe_vector = self.model.transform([recipe_ingredients])  # Векторизуем ингредиенты рецепта
            recipe_vectors.append(recipe_vector.toarray()[0])  # Преобразуем вектор в массив и добавляем в список

        knn = NearestNeighbors(n_neighbors=top_n, metric='cosine')  # Создаем объект KNN с использованием косинусного расстояния
        knn.fit(recipe_vectors)  # "Обучаем" модель KNN на векторах рецептов
        user_vector_array = user_vector.toarray()[0]  # Преобразуем вектор пользователя в массив
        distances, indices = knn.kneighbors([user_vector_array])  # Находим ближайших соседей для вектора пользователя

        recipe_scores = []  # Инициализируем список для хранения рекомендаций
        for i in range(top_n):  # проходим по топ-N рецептам
            recipe = recipes[indices[0][i]]  # Получаем рецепт по индексу
            distance = distances[0][i]  # Получаем расстояние до рецепта
            recipe_scores.append((recipe, 1 - distance))  # Добавляем рецепт и его оценку в список

        recipe_scores.sort(key=lambda x: x[1], reverse=True)  # Сортируем рецепты по оценке в порядке убывания
        return recipe_scores[:top_n], None  # Возвращаем топ-N рецептов
#Проверка
def main():
    recommender = RecipeRecommender("tfidf_model.pkl", connect_db())  # Создаем объект рекомендательной системы и подключаемся к базе данных
    user_ingredients = ["кальмар"]  # Ингредиенты пользователя
    allergies = ["лактоза", "глютен"]  # Аллергии пользователя
    recommendations, message = recommender.recommend_recipes(user_ingredients, allergies)  # Получаем рекомендации
    if recommendations:  # Проверяем, есть ли рекомендации
        for recipe, score in recommendations:  # Итерируемся по рекомендациям
            print(f"Recipe: {recipe['NAME']}, Ingredients: {recipe['INGREDIENTS']}, {recipe['RECIPE']}, Similarity: {score:.4f}")  # Выводим информацию о рецепте
    else:
        print(message)  # Выводим сообщение, если нет рекомендаций

if __name__ == "__main__":
    main()
