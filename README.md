# HabitBot

HabitBot is a Telegram bot designed to help users track and manage their habits. The project is built using Django, Celery, PostgreSQL, and Redis, and it is containerized using Docker to facilitate easy deployment and scaling.

## Project Structure

.
├── Dockerfile
├── celery.Dockerfile
├── celerybeat-schedule.db
├── celerybeat.Dockerfile
├── config
│   ├── __init__.py
│   ├── asgi.py
│   ├── celery.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── docker-compose.yml
├── habits
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── migrations
│   │   ├── 0001_initial.py
│   │   ├── 0002_habit_last_reminder_date.py
│   │   └── __init__.py
│   ├── models.py
│   ├── serializers.py
│   ├── tasks.py
│   ├── tests.py
│   ├── urls.py
│   ├── validators.py
│   └── views.py
├── manage.py
├── requirements.txt
├── telegram_bot
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── bot.py
│   ├── management
│   │   ├── __init__.py
│   │   └── commands
│   │       ├── __init__.py
│   │       ├── cpt.py
│   │       └── start_bot.py
│   ├── migrations
│   │   └── __init__.py
│   ├── models.py
│   ├── tasks.py
│   ├── tests.py
│   └── views.py
├── users
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── migrations
│   │   ├── 0001_initial.py
│   │   └── __init__.py
│   ├── models.py
│   ├── serializers.py
│   ├── tests.py
│   ├── urls.py
│   └── views.py
└── wait-for-postgres.sh

## Getting Started

### Prerequisites

Make sure you have the following installed on your machine:
- Docker
- Docker Compose

### Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/habitbot.git
   cd habitbot
   ```

2. Create and configure the `.env` file:
   ```
   cp .env.example .env
   ```
   Edit the `.env` file to include your specific configuration details:
   ```
   SECRET_KEY=your-secret-key
   DEBUG=True

   DB_NAME=habitbot
   DB_USER=postgres
   DB_PASSWORD=password
   DB_HOST=db
   DB_PORT=5432

   TELEGRAM_BOT_TOKEN=your-telegram-bot-token

   REDIS_HOST=redis
   REDIS_PORT=6379
   ```

3. Build and start the Docker containers:
   ```
   docker-compose up --build
   ```

4. Apply database migrations:
   ```
   docker-compose run web python manage.py migrate
   ```

5. Create a superuser for accessing the Django admin interface:
   ```
   docker-compose run web python manage.py createsuperuser
   ```

### Usage

1. Start the Docker containers:
   ```
   docker-compose up
   ```

2. Access the Django admin interface at:
   ```
   http://localhost:8000/admin/
   ```
   Log in with the superuser credentials you created earlier.

3. The Telegram bot will be running and ready to receive commands.

### Project Services

The project consists of the following services, all managed by Docker Compose:
- **web**: The Django web application.
- **db**: PostgreSQL database.
- **redis**: Redis server for caching and Celery broker.
- **celery**: Celery worker for handling background tasks.
- **celerybeat**: Celery Beat for scheduling periodic tasks.

### Running Tests

To run the tests for the Django applications, use the following command:
```
docker-compose run web python manage.py test
```

### Troubleshooting

If you encounter any issues, check the logs of the individual services:
```
docker-compose logs web
docker-compose logs db
docker-compose logs redis
docker-compose logs celery
docker-compose logs celerybeat
```

## License

This project is licensed under the MIT License. See the LICENSE file for more details.

## Contributing

If you would like to contribute to this project, please fork the repository and submit a pull request. For major changes, please open an issue first to discuss what you would like to change.

## Acknowledgements

- Django
- Celery
- PostgreSQL
- Redis
- Docker
- Telegram

If you have any questions or need further assistance, feel free to open an issue or contact me directly.
