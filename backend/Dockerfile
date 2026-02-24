# Use an official lightweight Python image
FROM python:3.13-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=travel_ai_backend.settings

# Set work directory
WORKDIR /app

# Install system dependencies for pgvector/psycopg2
RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY requirements.txt /app/
RUN pip install --upgrade pip \
    && pip install -r requirements.txt \
    && pip install gunicorn

# Copy project
COPY . /app/

# Expose port
EXPOSE 8000

# Run gunicorn (this command will be overridden by docker-compose for dev, but useful for prod)
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "travel_ai_backend.wsgi:application"]
