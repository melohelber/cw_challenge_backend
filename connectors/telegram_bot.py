#!/usr/bin/env python3

import os
import sys
import logging
import re
from datetime import datetime, timedelta
from typing import Optional

import requests
from telegram import Update
from telegram.ext import Application, MessageHandler, CommandHandler, ContextTypes, filters
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
BOT_USERNAME = os.getenv("BOT_USERNAME", "telegram_bot")
BOT_PASSWORD = os.getenv("BOT_PASSWORD")
SESSION_TIMEOUT_MINUTES = int(os.getenv("BOT_SESSION_TIMEOUT_MINUTES", "10"))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [%(name)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("telegram_bot")

last_message_time = {}
processed_message_ids = set()


class BackendClient:

    def __init__(self):
        self.backend_url = BACKEND_URL
        self.bot_username = BOT_USERNAME
        self.bot_password = BOT_PASSWORD
        self.jwt_token: Optional[str] = None
        self.token_expires_at: Optional[datetime] = None

    def login(self) -> bool:
        try:
            response = requests.post(
                f"{self.backend_url}/auth/login",
                json={"username": self.bot_username, "password": self.bot_password},
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                self.jwt_token = data["access_token"]
                self.token_expires_at = datetime.now() + timedelta(minutes=25)
                logger.info("Bot authenticated successfully with backend")
                return True
            else:
                logger.error(f"Login failed: {response.status_code} - {response.text}")
                return False

        except Exception as e:
            logger.error(f"Login error: {str(e)}")
            return False

    def ensure_authenticated(self) -> bool:
        if not self.jwt_token or not self.token_expires_at:
            logger.info("No token found, logging in...")
            return self.login()

        if datetime.now() >= self.token_expires_at:
            logger.info("JWT token expired, renewing...")
            return self.login()

        return True

    def send_message(self, message: str, telegram_user_id: str) -> dict:
        if not self.ensure_authenticated():
            return {
                "response": "Desculpe, estou com problemas de conexão com o servidor. Tente novamente em instantes.",
                "error": "authentication_failed"
            }

        try:
            user_id = f"telegram_{telegram_user_id}"

            response = requests.post(
                f"{self.backend_url}/chat",
                json={"message": message},
                headers={"Authorization": f"Bearer {self.jwt_token}"},
                timeout=30
            )

            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Backend error: {response.status_code} - {response.text}")
                return {
                    "response": "Desculpe, ocorreu um erro ao processar sua mensagem. Tente novamente.",
                    "error": f"backend_error_{response.status_code}"
                }

        except requests.exceptions.Timeout:
            logger.error("Backend request timeout")
            return {
                "response": "Desculpe, a resposta está demorando muito. Tente uma pergunta mais simples.",
                "error": "timeout"
            }
        except Exception as e:
            logger.error(f"Error sending message to backend: {str(e)}")
            return {
                "response": "Desculpe, ocorreu um erro inesperado. Tente novamente.",
                "error": str(e)
            }


backend = BackendClient()


def format_for_telegram(text: str) -> str:
    text = re.sub(r'^#+\s+', '', text, flags=re.MULTILINE)
    text = re.sub(r'\*\*(.*?)\*\*', r'*\1*', text)
    text = re.sub(r'__(.*?)__', r'_\1_', text)
    return text


def strip_all_markdown(text: str) -> str:
    text = re.sub(r'^#+\s+', '', text, flags=re.MULTILINE)
    text = re.sub(r'<b>(.*?)</b>', r'\1', text)
    text = re.sub(r'<i>(.*?)</i>', r'\1', text)
    text = re.sub(r'<code>(.*?)</code>', r'\1', text)
    text = re.sub(r'<.*?>', '', text)
    text = text.replace("**", "")
    text = text.replace("__", "")
    text = text.replace("*", "")
    text = text.replace("_", "")
    text = text.replace("`", "")

    return text


def sanitize_and_enrich_message(message: str, user_first_name: str) -> str:
    clean_message = re.sub(
        r'\[User\'?s?\s+real\s+first\s+name\s+is:.*?\]',
        '',
        message,
        flags=re.IGNORECASE
    ).strip()

    enriched_message = f"{clean_message}\n\n[User's real first name is: {user_first_name}]"

    return enriched_message


async def send_welcome_message(update: Update):
    user = update.effective_user
    welcome_message = (
        f"Olá, {user.first_name}! 👋\n\n"
        "Sou o assistente da InfinitePay. Posso ajudar você com:\n"
        "• Informações sobre produtos (Pix, maquininha, conta digital)\n"
        "• Consultas sobre sua conta\n"
        "• Histórico de transações\n"
        "• Suporte técnico\n\n"
        "Envie sua pergunta e eu te ajudo!"
    )
    await update.message.reply_text(welcome_message)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    logger.info(f"User [telegram_{user.id}] started bot - {user.first_name}")

    await send_welcome_message(update)

    last_message_time[user.id] = datetime.now()


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    logger.info(f"User [telegram_{user.id}] requested help")

    help_message = (
        "📚 Como usar este bot:\n\n"
        "Simplesmente envie sua pergunta em texto.\n\n"
        "Exemplos:\n"
        "• \"Qual a taxa do Pix?\"\n"
        "• \"Como funciona a maquininha?\"\n"
        "• \"Mostre minhas transações recentes\"\n"
        "• \"Qual é o status da minha conta?\"\n\n"
        "Estou aqui para ajudar! 🤖"
    )

    await update.message.reply_text(help_message)


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    message_id = update.message.message_id
    message_text = update.message.text
    now = datetime.now()

    logger.info(f"[HANDLER START] user_id={user.id}, message_id={message_id}, text='{message_text[:20]}...'")

    if message_id in processed_message_ids:
        logger.warning(f"[DEDUP] Duplicate message detected (ID: {message_id}), skipping")
        return

    processed_message_ids.add(message_id)
    logger.info(f"[DEDUP] Added message_id={message_id} to processed set (total: {len(processed_message_ids)})")

    if len(processed_message_ids) > 1000:
        processed_message_ids.clear()
        logger.info("Cleared processed message IDs cache")

    is_new_session = False

    if user.id in last_message_time:
        time_since_last = now - last_message_time[user.id]
        if time_since_last > timedelta(minutes=SESSION_TIMEOUT_MINUTES):
            is_new_session = True
            logger.info(f"User [telegram_{user.id}] session timeout ({SESSION_TIMEOUT_MINUTES}min) - new session")
    else:
        is_new_session = True
        logger.info(f"User [telegram_{user.id}] first message - new session")

    last_message_time[user.id] = now

    logger.info(f"User [telegram_{user.id}] sent message: '{message_text[:50]}...'")

    await update.message.chat.send_action("typing")

    enriched_message = sanitize_and_enrich_message(message_text, user.first_name)

    logger.info(f"[DEBUG] Sending to backend: user_id={user.id}, message_id={message_id}")
    result = backend.send_message(enriched_message, str(user.id))
    logger.info(f"[DEBUG] Backend response received: agent={result.get('agent_used', 'unknown')}")

    response_text = result.get("response", "Desculpe, não consegui processar sua mensagem.")

    response_text = format_for_telegram(response_text)

    try:
        await update.message.reply_text(response_text, parse_mode="Markdown")
    except Exception as e:
        logger.warning(f"Markdown parse error, stripping all formatting and sending as plain text: {e}")
        plain_text = strip_all_markdown(result.get("response", "Desculpe, não consegui processar sua mensagem."))
        await update.message.reply_text(plain_text)

    logger.info(f"User [telegram_{user.id}] received response (agent: {result.get('agent_used', 'unknown')})")


async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Update {update} caused error {context.error}")


def main():
    if not TELEGRAM_BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN not found in environment variables!")
        logger.error("Please add it to your .env file")
        sys.exit(1)

    if not BOT_PASSWORD:
        logger.error("BOT_PASSWORD not found in environment variables!")
        logger.error("Please add it to your .env file")
        sys.exit(1)

    logger.info("=" * 60)
    logger.info("CloudWalk Telegram Bot Connector Starting...")
    logger.info(f"Backend URL: {BACKEND_URL}")
    logger.info(f"Bot Username: {BOT_USERNAME}")
    logger.info("=" * 60)

    if not backend.login():
        logger.error("Failed to authenticate with backend on startup!")
        logger.error("Make sure:")
        logger.error("1. Backend is running")
        logger.error("2. User 'telegram_bot' exists in backend")
        logger.error("3. BOT_PASSWORD in .env matches user password")
        sys.exit(1)

    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    application.add_error_handler(error_handler)

    logger.info("Bot is now running! Press Ctrl+C to stop.")
    logger.info("Send messages to your bot on Telegram to test.")

    application.run_polling()


if __name__ == "__main__":
    main()
