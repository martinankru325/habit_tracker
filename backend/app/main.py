from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from . import models, schemas, database, crud, auth
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware

models.Base.metadata.create_all(bind=database.engine)

app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/register")
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_telegram_id(db, user.telegram_id)
    if db_user:
        raise HTTPException(status_code=400, detail="User already registered")
    password_hash = auth.hash_password(user.password)
    user = crud.create_user(db, user, password_hash)
    return {"msg": "User registered successfully"}

@app.post("/token")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = crud.get_user_by_telegram_id(db, form_data.username)
    if not user or not auth.verify_password(form_data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Incorrect credentials")
    access_token = auth.create_access_token({"sub": user.telegram_id})
    crud.update_user_token(db, user, access_token)
    return {"access_token": access_token, "token_type": "bearer"}

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    payload = auth.decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    user = crud.get_user_by_telegram_id(db, payload["sub"])
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.post("/habits/", response_model=schemas.HabitRead)
def add_habit(habit: schemas.HabitCreate, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    return crud.create_habit(db, current_user.id, habit)

@app.get("/habits/", response_model=list[schemas.HabitRead])
def list_habits(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    return crud.get_user_habits(db, current_user.id)

@app.post("/habits/{habit_id}/complete", response_model=schemas.HabitRead)
def complete_habit(habit_id: int, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    habit = crud.mark_habit_completed(db, habit_id)
    if not habit or habit.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Habit not found")
    return habit

@app.delete("/habits/{habit_id}")
def remove_habit(habit_id: int, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    habit = crud.delete_habit(db, habit_id)
    if not habit:
        raise HTTPException(status_code=404, detail="Habit not found")
    return {"ok": True}

@app.get("/users/", response_model=list[schemas.UserRead])
def get_all_users(db: Session = Depends(get_db)):
    users = crud.get_all_users(db)
    return [{"telegram_id": user.telegram_id, "last_token": user.last_token} for user in users]
