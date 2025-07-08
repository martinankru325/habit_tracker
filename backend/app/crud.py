from sqlalchemy.orm import Session
from . import models, schemas
from datetime import date

def create_user(session: Session, user_data: schemas.UserCreate, password_hash: str):
    user = models.User(
        telegram_id=user_data.telegram_id,
        username=user_data.username,
        password_hash=password_hash
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user

def get_user_by_telegram_id(session: Session, telegram_id: str):
    return session.query(models.User).filter(models.User.telegram_id == telegram_id).first()

def update_user_token(session: Session, user: models.User, token: str):
    user.last_token = token
    session.commit()

def get_all_users(session: Session):
    return session.query(models.User).all()

def create_habit(session: Session, user_id: int, habit_data: schemas.HabitCreate):
    habit = models.Habit(
        name=habit_data.name,
        user_id=user_id
    )
    session.add(habit)
    session.commit()
    session.refresh(habit)
    return habit

def get_user_habits(session: Session, user_id: int):
    return session.query(models.Habit).filter(models.Habit.user_id == user_id).all()

def mark_habit_completed(session: Session, habit_id: int):
    habit = session.query(models.Habit).get(habit_id)
    if habit:
        habit.is_completed_today = True
        habit.completed_times += 1
        habit.last_completed_date = date.today()
        session.commit()
    return habit

def delete_habit(session: Session, habit_id: int):
    habit = session.query(models.Habit).get(habit_id)
    if habit:
        session.delete(habit)
        session.commit()
    return habit

def reset_habits_daily(session: Session):
    habits = session.query(models.Habit).all()
    for habit in habits:
        if habit.completed_times < 21:
            habit.is_completed_today = False
        else:
            session.delete(habit)
    session.commit()
