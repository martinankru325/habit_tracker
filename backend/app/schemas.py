from pydantic import BaseModel
from datetime import date

class UserCreate(BaseModel):
    telegram_id: str
    username: str | None = None
    password: str

class UserAuth(BaseModel):
    telegram_id: str
    password: str

class HabitCreate(BaseModel):
    name: str

class HabitRead(BaseModel):
    id: int
    name: str
    completed_times: int
    is_completed_today: bool
    last_completed_date: date | None

    class Config:
        orm_mode = True

class UserRead(BaseModel):
    telegram_id: str
    last_token: str | None = None
