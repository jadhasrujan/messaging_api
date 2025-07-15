from datetime import datetime, timedelta
from fastapi import HTTPException
from tinydb import TinyDB, Query
import uuid
from models import *
from passlib.context import CryptContext
from jose import jwt, JWTError

# Database files using TinyDB
db_chats = TinyDB("db/chats.json")
db_users = TinyDB("db/users.json")
db_messages = TinyDB("db/messages.json")
db_groups = TinyDB("db/groups.json")

# JWT Configuration
SECERT_KEY = "c55a4b81cfda5042414d48963f7f57553c3acc87eba4a04f2a2636880bdbeb36"
ALGORITHM = "HS256"

# Password hashing context
pwd_context = CryptContext(schemes=['bcrypt'], deprecated="auto")

Chat = Query()
Message = Query()

class Database:

    # Create JWT access token
    def create_token(data: dict, expiry_delta: timedelta = timedelta(minutes=30)):
        to_enocode = data.copy()
        expire = datetime.utcnow() + expiry_delta
        to_enocode.update({"exp": expire})
        return jwt.encode(to_enocode, SECERT_KEY, algorithm=ALGORITHM)

    # Create a new one-on-one chat room
    @staticmethod
    def create_room(data: dict):
        Chat = Query()
        User = Query()
        room_id = str(uuid.uuid4())

        # Check if room already exists (both directions)
        existing = db_chats.search(
            ((Chat.username_1 == data['username_1']) & (Chat.username_2 == data['username_2'])) |
            ((Chat.username_1 == data['username_2']) & (Chat.username_2 == data['username_1']))
        )

        # Check if user exists
        check_user = db_users.search(User.username == data['username_1'])
        if not check_user:
            return {"message": "User Does not exists"}

        elif existing:
            return {"message": "Room already exists", "room_id": existing[0]['room_id']}

        # Create new room
        db_chats.insert({
            "room_id": room_id,
            "username_1": data["username_1"],
            "username_2": data["username_2"]
        })

        return {"message": "Room created", "room_id": room_id}
    
    # Create a new group chat with members
    @staticmethod
    def create_group(data: dict):
        Users = Query()
        group_members = data["group_members"]
        group_admin = data["group_admin"]
        all_valid = True
        invaild_users = []

        # Validate all users exist
        for user in group_members + [group_admin]:
            check_user = db_users.search(Users.username == user)
            if not check_user:
                all_valid = False
                invaild_users.append(user)

        if not all_valid:
            return {
                "message": "Some users not found!",
                "invalid users": invaild_users
            }

        # Insert group
        db_groups.insert(data)
        return {
            "status": "success",
            "message": "Group Successfully Created!"
        }

    # Get a user's profile by username
    @staticmethod
    def get_user(username: str):
        User = Query()
        result = db_users.search(User.username == username)
        if result:
            return result[0]
        return None

    # Signup/register a new user
    @staticmethod
    def signup(data: dict):
        db_users.insert({
            "username": data['username'],
            "password": data['password']
        })
        return {"message": "User Created Successfully!"}
    
    # Login and return JWT token if valid
    @staticmethod
    def login(data: dict):
        user = Query()
        result = db_users.search(user.username == data['username'])

        if not result:
            return {"message": "Invalid username or password"}

        user_data = result[0]

        # Verify password using bcrypt
        if not pwd_context.verify(data['password'], user_data['password']):
            return {"message": "Invalid username or password"}

        # Generate access token
        token = Database.create_token({"sub": user_data['username']})
        return {"access_token": token, "token_type": "bearer"}

    # Send message in private (1-to-1) chat
    @staticmethod
    def send_message(data: dict):
        room = db_chats.search(Chat.room_id == data['room_id'])
        if not room:
            raise HTTPException(status_code=404, detail="Room does not exist")
        
        room = room[0]

        # Verify sender is part of the room
        if data['sender'] not in [room["username_1"], room["username_2"]]:
            raise HTTPException(status_code=403, detail="You are not a member of this room")

        # Store the message
        db_messages.insert({
            "room_id": data["room_id"],
            "sender": data["sender"],
            "message": data["message"],
            "timestamp": datetime.utcnow().isoformat()
        })
        return {"message": "Message sent successfully"}

    # Send message in a group chat
    @staticmethod
    def send_message_group(data: dict):
        GroupChat = Query()
        room = db_groups.search(GroupChat.room_id == data['room_id'])
        if not room:
            raise HTTPException(status_code=404, detail="Room does not exist")
        
        room = room[0]

        # Verify sender is a member of the group
        if data['sender'] not in room['group_members'] + [room['group_admin']]:
            raise HTTPException(status_code=403, detail="You are not a member of this room")

        # Store the message
        db_messages.insert({
            "room_id": data["room_id"],
            "sender": data["sender"],
            "message": data["message"],
            "is_group": data['is_group'],
            "group_name": room['group_members'],
            "timestamp": datetime.utcnow().isoformat()
        })
        return {"message": "Message sent successfully"}

    # Get list of private chat rooms for a user
    @staticmethod
    def get_room(username: str):
        rooms = db_chats.search(
            (Chat.username_1 == username) | (Chat.username_2 == username)
        )

        if not rooms:
            return {"message": "User is not part of any room."}

        # Get usernames of the other person in each room
        chat_list = []
        for room in rooms:
            other_user = room["username_2"] if room["username_1"] == username else room["username_1"]
            chat_list.append(other_user)

        return chat_list

    # Get all messages from a group chat
    @staticmethod
    def get_group(group_id: str):
        Group = Query()
        Messages = Query()

        # Check if group exists
        groups = db_groups.search(Group.room_id == group_id)
        if not groups:
            return {"message": "Group not found!"}

        # Get messages from that group
        group_chat = db_messages.search(Messages.room_id == group_id)

        return group_chat

    # Get all messages from a private chat room
    @staticmethod
    def get_chat(room_id: str):
        # Check if room exists
        room = db_chats.search(Chat.room_id == room_id)
        if not room:
            return {"message": "No Chats Exists!"}

        # Get messages from the room
        chats = db_messages.search(Message.room_id == room[0]['room_id'])

        return chats
