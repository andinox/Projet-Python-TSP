FROM python:3.12.7-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/root/.local/bin:$PATH"

# Install system deps
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    bash \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY DiagnosticTool/fixtures /app/DiagnosticTool/fixtures
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --break-system-packages gunicorn -r requirements.txt

COPY . .

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

CMD ["/entrypoint.sh"]
