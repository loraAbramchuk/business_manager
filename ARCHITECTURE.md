# Project structure

The project uses a classic Django structure with a small extra root layer.

## Root packages

- `config/` - Django settings, ASGI and WSGI configuration.
- `app/` - project-level routing. Web routes and API routes are collected here.

## Django apps

Each domain is split into a separate Django app:

- `users/`
- `teams/`
- `tasks/`
- `meetings/`
- `evaluations/`
- `comments/`

## Layers inside apps

Apps use simple layers:

- `views.py` - request/response logic.
- `services.py` - business actions that change data.
- `selectors.py` - database queries used by views.
- `permissions.py` - access checks.
- `forms.py` - form validation.
- `models.py` - database models.
- `urls.py` - app-level routes.

Not every app needs every file. A file is added only when the app has enough
logic for that layer.
