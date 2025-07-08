import requests
from apscheduler.schedulers.blocking import BlockingScheduler
import telebot
import os

API_URL = os.getenv("API_URL", "http://api:8000")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "7135246902:AAGj2i1ibrgGIo9kQQNEk8EQR_coMX0It2A")

bot = telebot.TeleBot(TELEGRAM_TOKEN)

def fetch_all_users():
    response = requests.get(f"{API_URL}/users/")
    return response.json() if response.ok else []

def fetch_user_habits(token):
    response = requests.get(
        f"{API_URL}/habits/",
        headers={"Authorization": f"Bearer {token}"}
    )
    if response.ok:
        return response.json()
    return []

def send_reminder_to_user(telegram_id, habits):
    if not habits:
        return
    habit_names = [habit['name'] for habit in habits if not habit['is_completed_today']]
    if habit_names:
        text = "Напоминание! Сегодня вы ещё не выполнили привычки:\n" + "\n".join(habit_names)
        bot.send_message(telegram_id, text)

def notify_all_users():
    users = fetch_all_users()
    for user in users:
        telegram_id = user["telegram_id"]
        token = user["last_token"]
        if not token:
            continue
        habits = fetch_user_habits(token)
        send_reminder_to_user(telegram_id, habits)

if __name__ == "__main__":
    scheduler = BlockingScheduler()
    scheduler.add_job(notify_all_users, 'cron', hour=21, minute=0)
    print("Сервис напоминаний запущен!")
    scheduler.start()
