import telebot
import requests
from config import TELEGRAM_TOKEN, API_URL

bot = telebot.TeleBot(TELEGRAM_TOKEN)
user_tokens = {}  # telegram_id: token

def get_token(telegram_id, password):
    response = requests.post(f"{API_URL}/token", data={
        "username": telegram_id,
        "password": password
    })
    if response.ok:
        return response.json()["access_token"]
    return None

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Привет! Введите пароль для регистрации или входа:")
    bot.register_next_step_handler(message, handle_password)

def handle_password(message):
    telegram_id = str(message.from_user.id)
    password = message.text.strip()
    response = requests.post(f"{API_URL}/register", json={
        "telegram_id": telegram_id,
        "username": message.from_user.username,
        "password": password
    })
    if response.ok or response.status_code == 400:
        token = get_token(telegram_id, password)
        if token:
            user_tokens[telegram_id] = token
            bot.send_message(message.chat.id, "Успешный вход! Используйте /add, /list, /done, /delete.")
        else:
            bot.send_message(message.chat.id, "Ошибка авторизации.")
    else:
        bot.send_message(message.chat.id, "Ошибка регистрации.")


@bot.message_handler(commands=['add'])
def add_habit(message):
    telegram_id = str(message.from_user.id)
    if telegram_id not in user_tokens:
        bot.send_message(message.chat.id, "Сначала выполните вход через /start.")
        return
    msg = bot.send_message(message.chat.id, "Введите название привычки:")
    bot.register_next_step_handler(msg, lambda m: process_add_habit(m, telegram_id))

def process_add_habit(message, telegram_id):
    token = user_tokens[telegram_id]
    response = requests.post(f"{API_URL}/habits/", headers={"Authorization": f"Bearer {token}"}, json={"name": message.text})
    if response.ok:
        bot.send_message(message.chat.id, "Привычка добавлена!")
    else:
        bot.send_message(message.chat.id, "Ошибка при добавлении привычки.")

@bot.message_handler(commands=['list'])
def list_habits(message):
    telegram_id = str(message.from_user.id)
    if telegram_id not in user_tokens:
        bot.send_message(message.chat.id, "Сначала выполните вход через /start.")
        return
    token = user_tokens[telegram_id]
    response = requests.get(f"{API_URL}/habits/", headers={"Authorization": f"Bearer {token}"})
    if response.ok:
        habits = response.json()
        if not habits:
            bot.send_message(message.chat.id, "У вас нет привычек.")
        else:
            text = "Ваши привычки:\n" + "\n".join(f"{h['id']}: {h['name']} (Выполнено: {h['completed_times']})" for h in habits)
            bot.send_message(message.chat.id, text)
    else:
        bot.send_message(message.chat.id, "Ошибка при получении привычек.")

@bot.message_handler(commands=['done'])
def mark_done(message):
    telegram_id = str(message.from_user.id)
    if telegram_id not in user_tokens:
        bot.send_message(message.chat.id, "Сначала выполните вход через /start.")
        return
    msg = bot.send_message(message.chat.id, "Введите ID привычки для отметки выполнения:")
    bot.register_next_step_handler(msg, lambda m: process_mark_done(m, telegram_id))

def process_mark_done(message, telegram_id):
    token = user_tokens[telegram_id]
    habit_id = message.text.strip()
    response = requests.post(f"{API_URL}/habits/{habit_id}/complete", headers={"Authorization": f"Bearer {token}"})
    if response.ok:
        bot.send_message(message.chat.id, "Привычка отмечена как выполненная сегодня.")
    else:
        bot.send_message(message.chat.id, "Ошибка при отметке выполнения.")

@bot.message_handler(commands=['delete'])
def delete_habit(message):
    telegram_id = str(message.from_user.id)
    if telegram_id not in user_tokens:
        bot.send_message(message.chat.id, "Сначала выполните вход через /start.")
        return
    msg = bot.send_message(message.chat.id, "Введите ID привычки для удаления:")
    bot.register_next_step_handler(msg, lambda m: process_delete_habit(m, telegram_id))

def process_delete_habit(message, telegram_id):
    token = user_tokens[telegram_id]
    habit_id = message.text.strip()
    response = requests.delete(f"{API_URL}/habits/{habit_id}", headers={"Authorization": f"Bearer {token}"})
    if response.ok:
        bot.send_message(message.chat.id, "Привычка удалена.")
    else:
        bot.send_message(message.chat.id, "Ошибка при удалении привычки.")

if __name__ == '__main__':
    print("Бот запущен!")
    bot.infinity_polling()
