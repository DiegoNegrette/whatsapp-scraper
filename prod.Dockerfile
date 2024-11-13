# Use the official Python image from the Docker Hub
FROM python:3.10.4-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DJANGO_PORT=8000

# Create a directory for the application
WORKDIR /code

# Copy only the Pipfile and Pipfile.lock first to leverage Docker cache
COPY Pipfile Pipfile.lock /code/

# Install system dependencies and Python dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        nginx \
        nano \
        dumb-init \
        build-essential \
        libpq-dev \
    && python -m pip install --upgrade pip \
    && pip install pipenv \
    && pipenv install gunicorn \
    && pipenv install --system --deploy \
    && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false build-essential \
    && rm -rf /var/lib/apt/lists/* \
    && rm -f Pipfile Pipfile.lock

# Create the nginx user
RUN useradd -r -d /nonexistent -s /bin/false nginx

# Copy the application code to the container
COPY . /code/

# Set work directory
WORKDIR /code/whatsapp-scraper

# Collect static files for production
RUN python manage.py collectstatic --noinput

# Copy NGINX configuration
COPY nginx/nginx.conf /etc/nginx/nginx.conf
COPY nginx/default.conf /etc/nginx/conf.d/

# Expose the port the app runs on
EXPOSE 80

# Start the application using dumb-init for proper signal handling
CMD ["dumb-init", "sh", "-c", "nginx && gunicorn --bind 0.0.0.0:8000 --timeout 500 service.wsgi:application"]
