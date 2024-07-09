# Dockerfile
FROM python:3.12

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /code

# Install dependencies
COPY requirements.txt /code/
RUN apt-get update \
    && apt-get install -y postgresql-client \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --upgrade pip \
    && pip install -r requirements.txt

# Copy project
COPY . /code/

# Run the Django server
CMD ["./wait-for-postgres.sh", "db", "python", "manage.py", "runserver", "0.0.0.0:8000"]
