FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libffi-dev \
    libssl-dev \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir --timeout 100 -r requirements.txt

COPY darkeye_bot.py .

ENV PYTHONUNBUFFERED=1

CMD ["python", "darkeye_bot.py"]
