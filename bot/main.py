import telebot
from telebot import types
import requests
from config import TELEGRAM_TOKEN, API_URL

bot = telebot.TeleBot(TELEGRAM_TOKEN)
user_tokens = {}  # telegram_id: token

# Клавиатура с основными командами
def main_keyboard():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = ["/add", "/list", "/done", "/delete", "/logout"]
    keyboard.add(*buttons)
    return keyboard

def get_token(telegram_id, password):
    response = requests.post(f"{API_URL}/token", data={
        "username": telegram_id,
        "password": password
    })
    if response.ok:
        return response.json().get("access_token")
    return None

@bot.message_handler(commands=['start'])
def start(message):
    telegram_id = str(message.from_user.id)
    if telegram_id in user_tokens:
        bot.send_message(message.chat.id, "Вы уже вошли в систему.", reply_markup=main_keyboard())
        return
    bot.send_message(message.chat.id, "Привет! Введите пароль для регистрации или входа:")
    bot.register_next_step_handler(message, handle_password)

def handle_password(message):
    telegram_id = str(message.from_user.id)
    password = message.text.strip()
    response = requests.post(f"{API_URL}/register", json={
        "telegram_id": telegram_id,
        "username": message.from_user.username or "",
        "password": password
    })
    if response.ok or response.status_code == 400:  # 400 — возможно, пользователь уже зарегистрирован
        token = get_token(telegram_id, password)
        if token:
            user_tokens[telegram_id] = token
            bot.send_message(message.chat.id,
                             "Успешный вход! Выберите действие на клавиатуре ниже.",
                             reply_markup=main_keyboard())
        else:
            bot.send_message(message.chat.id, "Ошибка авторизации. Попробуйте снова.")
            bot.register_next_step_handler(message, handle_password)
    else:
        bot.send_message(message.chat.id, "Ошибка регистрации. Попробуйте снова.")
        bot.register_next_step_handler(message, handle_password)

def require_auth(func):
    """Декоратор для проверки авторизации пользователя"""
    def wrapper(message):
        telegram_id = str(message.from_user.id)
        if telegram_id not in user_tokens:
            bot.send_message(message.chat.id, "Пожалуйста, сначала войдите через /start.")
            return
        return func(message, telegram_id)
    return wrapper

@bot.message_handler(commands=['add'])
@require_auth
def add_habit(message, telegram_id):
    msg = bot.send_message(message.chat.id, "Введите название привычки:")
    bot.register_next_step_handler(msg, lambda m: process_add_habit(m, telegram_id))

def process_add_habit(message, telegram_id):
    token = user_tokens[telegram_id]
    habit_name = message.text.strip()
    if not habit_name:
        bot.send_message(message.chat.id, "Название привычки не может быть пустым. Попробуйте снова.")
        return
    response = requests.post(f"{API_URL}/habits/", headers={"Authorization": f"Bearer {token}"}, json={"name": habit_name})
    if response.ok:
        bot.send_message(message.chat.id, "Привычка добавлена!")
    else:
        bot.send_message(message.chat.id, "Ошибка при добавлении привычки.")

@bot.message_handler(commands=['list'])
@require_auth
def list_habits(message, telegram_id):
    token = user_tokens[telegram_id]
    response = requests.get(f"{API_URL}/habits/", headers={"Authorization": f"Bearer {token}"})
    if response.ok:
        habits = response.json()
        if not habits:
            bot.send_message(message.chat.id, "У вас нет привычек.")
        else:
            text = "Ваши привычки:\n" + "\n".join(
                f"{h['id']}: {h['name']} (Выполнено: {h['completed_times']})" for h in habits)
            bot.send_message(message.chat.id, text)
    else:
        bot.send_message(message.chat.id, "Ошибка при получении привычек.")

@bot.message_handler(commands=['done'])
@require_auth
def mark_done(message, telegram_id):
    token = user_tokens[telegram_id]
    response = requests.get(f"{API_URL}/habits/", headers={"Authorization": f"Bearer {token}"})
    if response.ok:
        habits = response.json()
        if not habits:
            bot.send_message(message.chat.id, "У вас нет привычек для отметки.")
            return
        keyboard = types.InlineKeyboardMarkup()
        for habit in habits:
            keyboard.add(types.InlineKeyboardButton(text=habit['name'], callback_data=f"done_{habit['id']}"))
        bot.send_message(message.chat.id, "Выберите привычку для отметки выполнения сегодня:", reply_markup=keyboard)
    else:
        bot.send_message(message.chat.id, "Ошибка при получении привычек.")

@bot.callback_query_handler(func=lambda call: call.data.startswith('done_'))
def callback_mark_done(call):
    telegram_id = str(call.from_user.id)
    if telegram_id not in user_tokens:
        bot.answer_callback_query(call.id, "Пожалуйста, сначала войдите через /start.")
        return
    habit_id = call.data.split('_')[1]
    token = user_tokens[telegram_id]
    response = requests.post(f"{API_URL}/habits/{habit_id}/complete", headers={"Authorization": f"Bearer {token}"})
    if response.ok:
        bot.answer_callback_query(call.id, "Привычка отмечена как выполненная сегодня.")
        bot.send_message(call.message.chat.id, f"Привычка с ID {habit_id} отмечена как выполненная.")
    else:
        bot.answer_callback_query(call.id, "Ошибка при отметке выполнения.")

@bot.message_handler(commands=['delete'])
@require_auth
def delete_habit(message, telegram_id):
    token = user_tokens[telegram_id]
    response = requests.get(f"{API_URL}/habits/", headers={"Authorization": f"Bearer {token}"})
    if response.ok:
        habits = response.json()
        if not habits:
            bot.send_message(message.chat.id, "У вас нет привычек для удаления.")
            return
        keyboard = types.InlineKeyboardMarkup()
        for habit in habits:
            keyboard.add(types.InlineKeyboardButton(text=habit['name'], callback_data=f"delete_{habit['id']}"))
        bot.send_message(message.chat.id, "Выберите привычку для удаления:", reply_markup=keyboard)
    else:
        bot.send_message(message.chat.id, "Ошибка при получении привычек.")

@bot.callback_query_handler(func=lambda call: call.data.startswith('delete_'))
def callback_delete_habit(call):
    telegram_id = str(call.from_user.id)
    if telegram_id not in user_tokens:
        bot.answer_callback_query(call.id, "Пожалуйста, сначала войдите через /start.")
        return
    habit_id = call.data.split('_')[1]
    token = user_tokens[telegram_id]
    response = requests.delete(f"{API_URL}/habits/{habit_id}", headers={"Authorization": f"Bearer {token}"})
    if response.ok:
        bot.answer_callback_query(call.id, "Привычка удалена.")
        bot.send_message(call.message.chat.id, f"Привычка с ID {habit_id} удалена.")
    else:
        bot.answer_callback_query(call.id, "Ошибка при удалении привычки.")

@bot.message_handler(commands=['logout'])
@require_auth
def logout(message, telegram_id):
    user_tokens.pop(telegram_id, None)
    bot.send_message(message.chat.id, "Вы вышли из системы. Для входа используйте /start.", reply_markup=types.ReplyKeyboardRemove())

@bot.message_handler(func=lambda message: True)
def unknown(message):
    bot.send_message(message.chat.id, "Неизвестная команда. Используйте клавиатуру для выбора действия.", reply_markup=main_keyboard())

if __name__ == '__main__':
    print("Бот запущен!")
    bot.infinity_polling()
