# Используем официальный образ Python 3.11 slim
FROM python:3.11-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Обновляем пакеты и устанавливаем необходимые системные зависимости для сборки
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl build-essential gcc libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем Poetry через официальный скрипт
RUN curl -sSL https://install.python-poetry.org | python3 -

# Добавляем Poetry в PATH
ENV PATH="/root/.local/bin:$PATH"

# Копируем файлы описания зависимостей
COPY pyproject.toml poetry.lock /app/

# Отключаем создание виртуальных окружений и устанавливаем зависимости без установки проекта
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --no-root

# Копируем исходный код приложения
COPY app /app/app

# Команда запуска приложения
CMD ["poetry", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
