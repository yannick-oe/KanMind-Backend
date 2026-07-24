# KanMind Backend

A Django REST Framework backend for **KanMind**, a Kanban board
application. It serves a delivered, unmodifiable vanilla-JS frontend and
exposes a token-authenticated JSON API for users, boards, tasks and
comments.

The API covers:

- User registration and token login, plus an email lookup used when
  adding board members.
- Boards with owner and members, aggregate counts, and a detail view
  that embeds members and tasks.
- Tasks with status, priority, assignee, reviewer and due date, plus
  personal "assigned to me" and "reviewing" lists.
- Comments on tasks.

## Requirements

- **Python 3.12 or newer** (developed and tested on Python 3.14).
- **Django 6.0** and **Django REST Framework 3.17** (pinned in
  `requirements.txt`).
- SQLite is used locally; no external database service is required.

## Setup

A fresh clone reaches a running server with the following sequence:

```bash
# 1. Clone and enter the project
git clone <repository-url> KanMind-Backend
cd KanMind-Backend

# 2. Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create the environment file
cp .env.example .env

# 5. Generate a SECRET_KEY and paste it into .env wrapped in SINGLE QUOTES:
#      SECRET_KEY='<generated-key>'
#    The quotes matter: generated keys may contain # or $, which the .env
#    parser would otherwise treat as a comment or a variable reference.
#    An empty SECRET_KEY stops Django from starting.
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# 6. Apply migrations
python manage.py migrate

# 7. Create an admin user (prompts for email, fullname, password).
#    Use a two-word fullname such as "Max Mustermann" — the frontend
#    derives initials from it and fails on a single-word name.
python manage.py createsuperuser

# 8. Seed the frontend guest user
python manage.py seed_guest

# 9. Run the development server
python manage.py runserver
```

The API is then available at `http://127.0.0.1:8000/api/`.
The Django admin is available at `http://127.0.0.1:8000/admin/`.

## Environment variables

Copy `.env.example` to `.env` and fill in the values.

| Name | Purpose | Example value |
|---|---|---|
| `SECRET_KEY` | Django cryptographic key; must be set or Django will not start | *(generated, see step 5)* |
| `DEBUG` | Enables Django debug mode | `True` |
| `ALLOWED_HOSTS` | Comma-separated hosts Django will serve | `127.0.0.1,localhost` |
| `CORS_ALLOWED_ORIGINS` | Comma-separated origins allowed to call the API | `http://127.0.0.1:5500,http://localhost:5500` |
| `GUEST_EMAIL` | Email for the seeded guest user | `kevin@kovacsi.de` |
| `GUEST_PASSWORD` | Password for the seeded guest user | `asdasdasd` |

## Authentication

The API base URL is `http://127.0.0.1:8000/api/`. Authentication uses
**DRF token authentication**: register or log in to receive a token,
then send it on every subsequent request in the `Authorization` header:

```
Authorization: Token <your-token>
```

Obtain a token:

```bash
curl -X POST http://127.0.0.1:8000/api/login/ \
  -H "Content-Type: application/json" \
  -d '{"email": "kevin@kovacsi.de", "password": "asdasdasd"}'
```

Use it:

```bash
curl http://127.0.0.1:8000/api/boards/ \
  -H "Authorization: Token <your-token>"
```

## Endpoints

All paths are prefixed with `/api/`.

| Method | Path | Description |
|---|---|---|
| POST | `registration/` | Register a user; returns a token |
| POST | `login/` | Exchange email and password for a token |
| GET | `email-check/?email=<address>` | Look up a single user by email |
| GET | `boards/` | List boards the user owns or is a member of |
| POST | `boards/` | Create a board |
| GET | `boards/{board_id}/` | Board detail with members and tasks |
| PATCH | `boards/{board_id}/` | Update a board's title and/or members |
| DELETE | `boards/{board_id}/` | Delete a board (owner only) |
| GET | `tasks/assigned-to-me/` | Tasks where the user is the assignee |
| GET | `tasks/reviewing/` | Tasks where the user is the reviewer |
| POST | `tasks/` | Create a task on a board |
| PATCH | `tasks/{task_id}/` | Update a task |
| DELETE | `tasks/{task_id}/` | Delete a task (creator or board owner) |
| GET | `tasks/{task_id}/comments/` | List a task's comments |
| POST | `tasks/{task_id}/comments/` | Add a comment to a task |
| DELETE | `tasks/{task_id}/comments/{comment_id}/` | Delete your own comment |

## Tests and coverage

Run the test suite:

```bash
python manage.py test
```

Measure coverage (requires the dev dependencies,
`pip install -r requirements-dev.txt`):

```bash
coverage run manage.py test
coverage report -m
```

## Special notes

- **List endpoints return bare JSON arrays; pagination is deliberately
  off.** The delivered frontend calls `.filter()`/`.forEach()` directly
  on the response, so a DRF pagination envelope would break the board
  list, the dashboard and the task columns. `DEFAULT_PAGINATION_CLASS`
  is intentionally unset.
- **Serve the frontend from port 5500.** `CORS_ALLOWED_ORIGINS`
  defaults to `http://127.0.0.1:5500` and `http://localhost:5500`
  (the Live Server default). If you serve the frontend from another
  origin, add it to `CORS_ALLOWED_ORIGINS`.
- **`APPEND_SLASH` must stay enabled.** The frontend requests one board
  endpoint without a trailing slash; Django's `301` redirect (via
  `CommonMiddleware` with `APPEND_SLASH=True`) is what makes that call
  reach the API.
- **The guest user is required.** The frontend has a hardcoded guest
  login (`kevin@kovacsi.de` / `asdasdasd`). Without it the guest button
  fails, so `python manage.py seed_guest` must be run once per database.
  The command is idempotent and reads `GUEST_EMAIL`/`GUEST_PASSWORD`
  from the environment.
- **Documented contract interpretations live in `DEVIATIONS.md`** —
  deliberate, dated deviations (for example, allowing a board owner to
  create tasks on their own board) with their reasons.
