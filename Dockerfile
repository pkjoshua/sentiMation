FROM python:3.10-slim

# Install cron
RUN apt-get update && apt-get install -y cron && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Expose flask port
EXPOSE 5000

# Start cron and webapp
CMD service cron start && python3 webapp/app.py
