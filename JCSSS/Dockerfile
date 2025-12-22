FROM python:3.10-slim

# Security & performance
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Create non-root user
RUN addgroup --system django \
    && adduser --system --ingroup django django

WORKDIR /app

# System dependencies (minimal)
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install dependencies first (better caching)
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Permissions
RUN chown -R django:django /app
USER django

EXPOSE 8001

CMD ["gunicorn", "JCSSS.wsgi:application", "--bind", "0.0.0.0:8001", "--workers", "3", "--timeout", "120"]
