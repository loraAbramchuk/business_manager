# Business Manager

Business Manager is a Django project for team work management.

The app supports:

- user registration and login;
- teams and team membership;
- invitation by team code;
- task creation and task comments;
- meetings;
- employee task evaluations;
- calendar views;
- a small REST API for tasks with JWT authentication.

## Tech Stack

- Python 3.11
- Django 5
- Django REST Framework
- Simple JWT
- SQLite
- Docker / Docker Compose

## Project Structure

The project uses a classic Django structure with a small root routing layer.

- `config/` - Django settings, ASGI and WSGI configuration.
- `app/` - project-level web and API routers.
- `users/` - users, registration and profile pages.
- `teams/` - teams, memberships and invitation codes.
- `tasks/` - tasks, comments, calendar and task API.
- `meetings/` - meetings.
- `evaluations/` - employee evaluations.
- `comments/` - task comments.

Inside apps, business logic is split into simple layers:

- `views.py` - request and response logic;
- `services.py` - actions that change data;
- `selectors.py` - database queries;
- `permissions.py` - access checks;
- `forms.py` - form validation;
- `models.py` - database models.

## Local Setup

Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create an `.env` file in the project root:

```bash
cp .env.example .env
```

Run migrations:

```bash
python manage.py migrate
```

Start the server:

```bash
python manage.py runserver
```

Open:

```text
http://127.0.0.1:8000/
```

## Docker Setup

Build and start the app:

```bash
docker compose up --build
```

In another terminal, apply migrations:

```bash
docker compose exec web python manage.py migrate
```

Open:

```text
http://127.0.0.1:8000/
```

To stop containers:

```bash
docker compose down
```

## REST API

JWT endpoints:

```text
POST /api/token/
POST /api/token/refresh/
```

Tasks endpoint:

```text
/api/tasks/
```

Only authenticated users can use the API. Task creation is allowed only for
team managers.

## Tests

Run all tests:

```bash
python manage.py test
```

The test suite covers teams, tasks, task API, evaluations, users and meetings.

## Security Notes

Do not commit local secret or database files:

- `.env`
- `.local_secret_key`
- `db.sqlite3`
- `.venv/`

These files are ignored by `.gitignore` and `.dockerignore`.
