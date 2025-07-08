# Habit Tracker Chat Bot

Проект — чат-бот для трекинга привычек с напоминаниями.  
Реализован на FastAPI, PostgreSQL, SQLAlchemy, Alembic, PyTelegramBotAPI, APScheduler и Docker Compose.

---

## Оглавление

- [Описание](#описание)  
- [Технологии](#технологии)  
- [Установка и запуск](#установка-и-запуск)  
- [Использование](#использование)  
- [Структура проекта](#структура-проекта)  
- [Миграции Alembic](#миграции-alembic)  
- [Автор](#автор)

---

## Описание

Данный проект позволяет пользователям через Telegram-бота создавать и отслеживать привычки, отмечать их выполнение, получать ежедневные напоминания в 21:00.  
Все данные хранятся в PostgreSQL, API реализовано на FastAPI с использованием JWT-аутентификации.

---

## Технологии

- Python 3.11+  
- FastAPI  
- SQLAlchemy + Alembic  
- PostgreSQL  
- PyTelegramBotAPI  
- APScheduler  
- Docker, Docker Compose  
- Poetry (для backend)

---

## Установка и запуск

1. Клонируйте репозиторий:

```
git clone https://github.com/yourusername/habit_tracker_project.git
cd habit_tracker_project
```

2. Создайте файл `.env` или задайте переменные окружения для Telegram токена и базы данных (опционально).

3. Запустите проект через Docker Compose:

```
docker-compose up --build
```

4. Backend будет доступен по адресу: `http://localhost:8000`

5. Запустите Telegram-бота и начните взаимодействовать с ним.

---

## Использование

- `/start` — регистрация и вход (введите пароль)  
- `/add` — добавить новую привычку  
- `/list` — показать список привычек  
- `/done` — отметить привычку выполненной сегодня  
- `/delete` — удалить привычку  

Ежедневно в 21:00 бот будет отправлять напоминания о невыполненных привычках.

---

## Структура проекта

```
habit_tracker_project/
├── backend/           # FastAPI backend с моделями, миграциями и API
├── bot/               # Telegram-бот для взаимодействия с пользователем
├── notifier/          # Сервис напоминаний, отправляющий уведомления в Telegram
├── docker-compose.yml # Конфигурация Docker Compose для всех сервисов
└── README.md          # Этот файл
```

---

## Миграции Alembic

Для управления миграциями:

- Инициализация Alembic (один раз):

```
poetry run alembic init alembic
```

- Автоматическая генерация миграций:

```
poetry run alembic revision --autogenerate -m "Описание миграции"
```

- Применение миграций:

```
poetry run alembic upgrade head
```

---



