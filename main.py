from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
import uuid

from database import Database
from models import CreateGroup, CreateRoom, SendMessage, UserSignup

# Configuration
SECRET_KEY = "c55a4b81cfda5042414d48963f7f57553c3acc87eba4a04f2a2636880bdbeb36"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# FastAPI app
app = FastAPI()

# Security utils
pwd_context = CryptContext(schemes=['bcrypt'], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


# Utility Functions
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: timedelta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if not username:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        user = Database.get_user(username)
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
        return username
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")


# Auth Routes
@app.post("/signup")
def signup(user: UserSignup):
    if Database.get_user(user.username):
        raise HTTPException(status_code=400, detail="User already exists")
    hashed_password = get_password_hash(user.password)
    Database.signup({"username": user.username, "password": hashed_password})
    return {"message": "User created successfully"}

@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user_record = Database.get_user(form_data.username)
    if not user_record or not verify_password(form_data.password, user_record["password"]):
        raise HTTPException(status_code=400, detail="Invalid credentials")
    token = create_access_token(data={"sub": form_data.username})
    return {"access_token": token, "token_type": "bearer"}


# Message Routes
@app.post("/send-message")
def send_message(message_data: SendMessage, current_user: str = Depends(get_current_user)):
    full_data = {
        "room_id": message_data.room_id,
        "message": message_data.message,
        "sender": current_user
    }
    return Database.send_message(full_data)

@app.post("/send-message-group")
def send_message_group(message_data: SendMessage, current_user: str = Depends(get_current_user)):
    full_data = {
        "room_id": message_data.room_id,
        "message": message_data.message,
        "sender": current_user,
        "is_group": True,
    }
    return Database.send_message_group(full_data)


# Profile and Room Management
@app.get("/profile")
def get_profile(username: str = Depends(get_current_user)):
    return Database.get_user(username)

@app.get("/get_room")
def get_user_rooms(username: str = Depends(get_current_user)):
    return Database.get_room(username)

@app.get("/get_chats")
def get_chats(room_id: str):
    return Database.get_chat(room_id)

@app.get("/get_chats_group")
def get_group_chats(group_id: str):
    return Database.get_group(group_id)


# Room/Group Creation
@app.post("/create-room")
def create_new_room(room_data: CreateRoom, current_user: str = Depends(get_current_user)):
    full_data = {
        "username_1": current_user,
        "username_2": room_data.username_2
    }
    return Database.create_room(full_data)

@app.post("/create-group")
def create_new_group(group_data: CreateGroup, current_user: str = Depends(get_current_user)):
    full_data = {
        "room_id": str(uuid.uuid4()),
        "group_admin": current_user,
        "group_members": group_data.group_members
    }
    return Database.create_group(full_data)
