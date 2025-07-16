# 📩 Messaging API (FastAPI)

This repository contains the backend for a chat application, built using **FastAPI**. It provides functionalities for user authentication, private messaging, group chats, and profile/room management.

---

## 🚀 Features

### 🔐 User Authentication
- User registration (`/signup`)
- User login (`/login`) with JWT-based access tokens

### 💬 Private Messaging
- Send private messages between two users (`/send-message`)
- Retrieve private chat history (`/get_chats`)

### 👥 Group Chat
- Create new groups (`/create-group`)
- Send messages to groups (`/send-message-group`)
- Retrieve group chat history (`/get_chats_group`)

### 🏷️ Room and Profile Management
- Get user profile information (`/profile`)
- Retrieve a user's active chat rooms (`/get_room`)
- Create new private chat rooms (`/create-room`)

---

## 🧪 Setup and Installation

### ✅ Prerequisites
- Python 3.8+
- pip (Python package installer)

### 🛠 Installation

```bash
# Clone the repository
git clone <your-repository-url>
cd <your-repository-name>

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

> **Note**: If `requirements.txt` doesn't exist, create one with the following:

```
fastapi
uvicorn
pydantic
python-jose[cryptography]
passlib[bcrypt]
```

---

### 🗃️ Set up your database

This app expects a `database.py` and `models.py` to handle DB operations and data models. You need to implement:

- `get_user`, `signup`
- `send_message`, `send_message_group`
- `get_room`, `get_chat`, `get_group`
- `create_room`, `create_group`

You may use SQLite, PostgreSQL, MongoDB, or any preferred database backend.

---

### ▶️ Run the Application

```bash
uvicorn main:app --reload
```

- API Base URL: [http://127.0.0.1:8000](http://127.0.0.1:8000)
- Swagger Docs: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

## 📘 API Endpoints

### 🔐 Authentication

#### POST `/signup`
Registers a new user.

**Request Body**:
```json
{
  "username": "string",
  "password": "string"
}
```

**Response**:
```json
{
  "message": "User created successfully"
}
```

#### POST `/login`
Authenticates a user and returns an access token.

**Form Data**:
- username: string
- password: string

**Response**:
```json
{
  "access_token": "your_jwt_token",
  "token_type": "bearer"
}
```

---

### 💬 Messaging

#### POST `/send-message`
Send a private message. **(Auth required)**

**Headers**:
```
Authorization: Bearer <access_token>
```

**Request**:
```json
{
  "room_id": "string",
  "message": "string"
}
```

#### POST `/send-message-group`
Send a group chat message. **(Auth required)**

**Headers**:
```
Authorization: Bearer <access_token>
```

**Request**:
```json
{
  "room_id": "string",
  "message": "string"
}
```

---

### 🧑 Profile and Room Management

#### GET `/profile`
Returns authenticated user's profile. **(Auth required)**

#### GET `/get_room`
Returns user's active chat rooms. **(Auth required)**

#### GET `/get_chats`
Retrieve private chat messages.

**Query Param**: `room_id`

#### GET `/get_chats_group`
Retrieve group chat messages.

**Query Param**: `group_id`

---

### 🏠 Room/Group Creation

#### POST `/create-room`
Create a private room between two users. **(Auth required)**

**Request**:
```json
{
  "username_2": "string"
}
```

#### POST `/create-group`
Create a group chat. The caller becomes group admin. **(Auth required)**

**Request**:
```json
{
  "group_members": ["string", "string"]
}
```

---

## 🔒 Security

- **JWT Auth**: Tokens expire after 60 minutes.
- **Password Hashing**: Passwords are hashed using bcrypt.
- **Environment Variables**: `SECRET_KEY` should be set via environment variables in production.

---

## 🤝 Contributing

Fork this repo, open issues, and submit PRs! Contributions are welcome 🚀

---
