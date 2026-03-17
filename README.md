# Politico — E-Voting API

A secure, transparent, and accessible electronic voting system built with Django REST Framework and PostgreSQL.

## Tech Stack

- **Backend:** Django 5, Django REST Framework
- **Database:** PostgreSQL
- **Authentication:** JWT (SimpleJWT)
- **Hosting:** Render

## Features

- Voter registration and authentication
- Election management
- Candidate management
- Constituency management
- Secure vote casting with double-vote prevention
- Live election results with percentages
- Admin dashboard
- Full vote audit log

## API Endpoints

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/api/auth/register/` | Register a voter | Public |
| POST | `/api/auth/login/` | Login and get JWT token | Public |
| POST | `/api/auth/logout/` | Logout | Voter |
| GET | `/api/auth/profile/` | View profile | Voter |
| GET | `/api/elections/` | List all elections | Public |
| GET | `/api/elections/active/` | List active elections | Public |
| POST | `/api/elections/` | Create election | Admin |
| PATCH | `/api/elections/<id>/status/` | Update election status | Admin |
| GET | `/api/candidates/` | List all candidates | Public |
| POST | `/api/candidates/` | Add candidate | Admin |
| GET | `/api/constituencies/` | List constituencies | Public |
| POST | `/api/constituencies/` | Add constituency | Admin |
| POST | `/api/votes/cast/` | Cast a vote | Voter |
| GET | `/api/votes/results/<id>/` | Get election results | Public |
| GET | `/api/votes/log/` | Full audit log | Admin |
| GET | `/api/votes/my-history/` | My vote history | Voter |

## Setup & Installation

### 1. Clone the repository
```bash
git clone https://github.com/yourusername/politico-api.git
cd politico-api
```

### 2. Create and activate virtual environment
```bash
python -m venv env
env\Scripts\activate      # Windows
source env/bin/activate   # Mac/Linux
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Create `.env` file
```
SECRET_KEY=your-secret-key
DEBUG=True
DATABASE_URL=postgres://postgres:yourpassword@localhost:5432/politico_db
ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=http://localhost:5500,http://127.0.0.1:5500
```

### 5. Run migrations
```bash
python manage.py migrate
```

### 6. Create superuser
```bash
python manage.py createsuperuser
```

### 7. Run the server
```bash
python manage.py runserver
```

## Environment Variables

| Variable | Description |
|----------|-------------|
| `SECRET_KEY` | Django secret key |
| `DEBUG` | True for development, False for production |
| `DATABASE_URL` | PostgreSQL connection string |
| `ALLOWED_HOSTS` | Comma-separated list of allowed hosts |
| `CORS_ALLOWED_ORIGINS` | Comma-separated list of allowed frontend origins |

## Deployment

Deployed on Render. The `build.sh` script handles:
- Installing dependencies
- Collecting static files
- Running migrations

## License

MIT
