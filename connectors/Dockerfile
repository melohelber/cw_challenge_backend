FROM python:3.11-slim

WORKDIR /app

RUN pip install --no-cache-dir \
    python-telegram-bot==20.7 \
    requests==2.31.0 \
    python-dotenv==1.0.0

COPY connectors/ /app/connectors/

CMD ["python", "-u", "connectors/telegram_bot.py"]
