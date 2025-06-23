FROM python:3.12.7-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system deps
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY . .

# Collect static files and migrate on startup
CMD ["sh", "-c", "cd DiagnosticTool && python manage.py collectstatic --noinput && python manage.py migrate && gunicorn DiagnosticTool.wsgi:application --bind 0.0.0.0:8000"]
