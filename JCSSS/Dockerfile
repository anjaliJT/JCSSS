
# Use official Python image
FROM python:3.10-slim

# Prevent Python from writing pyc files to disk
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt /app/
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy project
COPY . /app/

# Expose port 8000
EXPOSE 8000

# Default command runs collectstatic before starting gunicorn
# CMD ["/bin/sh", "-c", "python manage.py collectstatic --noinput && gunicorn --bind 0.0.0.0:8000 JCSSS.wsgi:application"]
CMD ["/bin/sh", "-c", "python manage.py collectstatic --noinput && gunicorn --bind 0.0.0.0:8000 JCSSS.wsgi:application"]
