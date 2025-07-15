from typing import List
from pydantic import BaseModel

class CreateRoom(BaseModel):
    username_2:str

class UserSignup(BaseModel):
    username:str
    password:str

class SendMessage(BaseModel):
    room_id: str
    message: str

class CreateGroup(BaseModel):
    group_members : List[str]
    group_admin: str