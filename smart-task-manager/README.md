# Smart Task Management System

A complete production-ready Smart Task Management System built with Python Flask, PostgreSQL, Pandas, NumPy, and WebSockets.

## Features

- **User Authentication**: Secure registration and login using Flask-Login and JWT Authentication.
- **REST APIs**: Full CRUD operations for Tasks (`GET`, `POST`, `PUT`, `DELETE`).
- **PostgreSQL Integration**: Robust relational data storage using SQLAlchemy ORM.
- **Real-Time Updates**: WebSockets (Socket.IO) instantly broadcast task updates (creates, edits, deletions) without page reloads.
- **Analytics Dashboard**: Pandas and NumPy compute live statistics (total tasks, completion percentage, pending tasks, etc.).
- **Modern UI**: A responsive, mobile-friendly dashboard utilizing Bootstrap 5 with a custom "Dark Glassmorphism" aesthetic (purple/blue gradients, blurs, and hover animations).

## Tech Stack

**Backend**
- Python 3.12+
- Flask & Flask-SQLAlchemy
- Flask-Login & Flask-JWT-Extended
- Flask-SocketIO & Flask-CORS
- Psycopg2 & PostgreSQL
- Pandas & NumPy

**Frontend**
- HTML5 / CSS3 / Vanilla JavaScript
- Bootstrap 5
- Socket.IO Client
- FontAwesome Icons

## Project Structure

```
smart-task-manager/
├── app/
│   ├── __init__.py      # App factory
│   ├── config.py        # Config classes (Dev/Prod)
│   ├── models.py        # SQLAlchemy models (User, Task)
│   ├── extensions.py    # Flask extensions 
│   ├── sockets.py       # SocketIO event handlers
│   │
│   ├── auth/            # Web Authentication blueprint
│   ├── tasks/           # Tasks Web & Analytics blueprint
│   ├── templates/       # HTML templates (base, login, register, dashboard)
│   ├── static/          # CSS and Vanilla JS
│   └── api/             # JWT-protected REST API routes
│
├── requirements.txt     # Python dependencies
├── .env.example         # Environment variables template
├── run.py               # Main application entry point
├── docker-compose.yml   # PostgreSQL Docker setup
├── schema.sql           # Raw SQL Schema
└── README.md            # Documentation
```

## Installation & Setup

### 1. PostgreSQL Setup
The easiest way to set up PostgreSQL is using the provided Docker Compose file:
```bash
docker-compose up -d
```
This will spin up a PostgreSQL 15 instance on port `5432` with the `task_db` database created and initialized using `schema.sql`.

Alternatively, install PostgreSQL manually, create a database named `task_db`, and run the `schema.sql` file.

### 2. Environment Variables
Copy the `.env.example` file to `.env`:
```bash
cp .env.example .env
```
Ensure the `DATABASE_URL` matches your local setup. If using Docker, the default values will work perfectly. Update `SECRET_KEY` and `JWT_SECRET_KEY` for security.

### 3. Install Python Dependencies
Create a virtual environment and install the requirements:
```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

pip install -r requirements.txt
```

### 4. Run the Application
Run the application using the entry point:
```bash
python run.py
```
The server will start on `http://127.0.0.1:5000`.

## API Documentation

All API endpoints (except authentication) require a valid JWT `Bearer` token in the `Authorization` header.

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/register` | Register a new user |
| `POST` | `/api/login` | Login and receive a JWT access token |
| `GET` | `/api/tasks` | Get all tasks for the logged-in user |
| `POST` | `/api/tasks` | Create a new task |
| `PUT` | `/api/tasks/<id>` | Update an existing task |
| `DELETE` | `/api/tasks/<id>` | Delete a task |
| `GET` | `/api/analytics` | Get NumPy/Pandas task analytics |

## WebSocket Functionality
The application utilizes `Flask-SocketIO`. Upon loading the dashboard, the client connects to the socket server and emits a `join` event containing their JWT token. They are placed in a private room based on their `user_id`. When any task operation occurs (create/update/delete) via the API, the backend broadcasts a `task_update` event to that user's specific room, causing the frontend to re-fetch data instantly and seamlessly.

## Screenshots / Verification
1. Launch the app and visit `http://127.0.0.1:5000/`.
2. Register a new account and login.
3. Open two separate browser windows (or tabs) and login with the same account.
4. Add a task in Window A. Observe Window B instantly updating its task list and analytics without a page refresh!

## Future Improvements
- Pagination for large task lists.
- Interactive Chart.js or Recharts visual diagrams on the dashboard.
- Due date functionality with email/push reminders.
- Swagger / OpenAPI documentation via Flasgger.
- GitHub Actions CI/CD pipeline for automated testing and deployment.
