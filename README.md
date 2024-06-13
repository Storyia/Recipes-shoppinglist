# Система рекомендаций рецептов

## Общая информация

Этот проект представляет собой интерактивную платформу, предназначенную для помощи пользователям в планировании покупок и создании персонализированных рекомендаций рецептов на основе их предпочтений в ингредиентах и аллергиях.

## Особенности

- **Сбор данных:** Автоматический сбор данных с сайта eda.ru с использованием библиотек Python (requests, BeautifulSoup, json, pandas).
- **Предварительная обработка текста:** Включает токенизацию, лемматизацию, нормализацию и очистку данных.
- **Реализация модели:**
  - TF-IDF для векторизации текста и генерации рекомендаций.
- **Механизм рекомендаций:** Использует алгоритм NearestNeighbors для поиска и рекомендаций рецептов, наиболее схожих с введенными пользователем данными.
- **Веб-интерфейс:** Построен с использованием Flask и Bootstrap, что обеспечивает удобное взаимодействие с системой и управление списками покупок.

## Будущие улучшения

- Улучшение моделей и алгоритмов.
- Введение персонализированных рекомендаций.
- Разработка мобильного приложения.
- Расширение функционала для возможности делиться рецептами в социальных сетях и интеграции с онлайн-магазинами.

## Установка

Клонируйте репозиторий:
https://github.com/Storyia/Recipes-shoppinglist.git

## Запуск приложения

app.py

## Использование

1. Откройте веб-приложение в браузере.
2. Введите свои ингредиенты и предпочтения.
3. Получите персонализированные рекомендации рецептов.

## Лицензия

Этот проект лицензирован по лицензии MIT - подробности см. в файле LICENSE.

## Благодарности

- Факультет вычислительной математики и кибернетики МГУ.
- Моему руководителю Юлии Мочаловой за руководство и поддержку.

## Демонстрация работы

[Смотреть видео на Google Drive](https://drive.google.com/file/d/1a8GRV5EKF6wS1yYmuOJdLB_qZhzzIJLj/preview)

![Обложка](./Обложка.png)

# Sistema de recomendación de recetas

## Información general

Este proyecto es una plataforma interactiva diseñada para ayudar a los usuarios a planificar sus compras y crear recomendaciones personalizadas de recetas basadas en sus preferencias de ingredientes y alergias.

## Características

- **Recolección de datos:** Recopilación automática de datos del sitio eda.ru utilizando bibliotecas de Python (requests, BeautifulSoup, json, pandas).
- **Preprocesamiento de texto:** Incluye tokenización, lematización, normalización y limpieza de datos.
- **Implementación del modelo:**
  - TF-IDF para la vectorización de texto y generación de recomendaciones.
- **Mecanismo de recomendaciones:** Utiliza el algoritmo NearestNeighbors para encontrar y recomendar recetas más similares a los datos ingresados por el usuario.
- **Interfaz web:** Construida con Flask y Bootstrap, proporcionando una interacción conveniente con el sistema y gestión de listas de compras.

## Mejoras futuras

- Mejora de modelos y algoritmos.
- Implementación de recomendaciones personalizadas.
- Desarrollo de una aplicación móvil.
- Expansión de funcionalidades para compartir recetas en redes sociales e integración con tiendas en línea.

## Instalación

Clona el repositorio:
   git clone https://github.com/Storyia/Recipes-shoppinglist.git


## Inicio de la aplicación
app.py

## Uso

1. Abre la aplicación web en el navegador.
2. Ingresa tus ingredientes y preferencias.
3. Obtén recomendaciones personalizadas de recetas.

## Licencia

Este proyecto está licenciado bajo la licencia MIT - consulta el archivo LICENSE para más detalles.

## Agradecimientos

- Facultad de Matemáticas Computacionales y Cibernética de la Universidad Estatal de Moscú.
- A mi supervisora, Julia Mochalova, por su guía y apoyo.

