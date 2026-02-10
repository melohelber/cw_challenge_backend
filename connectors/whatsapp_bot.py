#!/usr/bin/env python3

import os
import sys
import logging
import re
import json
import time
from datetime import datetime, timedelta
from typing import Optional
from threading import Lock

import requests
from flask import Flask, request, jsonify
from dotenv import load_dotenv

load_dotenv()

UAZAPI_BASE_URL = os.getenv("UAZAPI_BASE_URL", "https://your-subdomain.uazapi.com")
UAZAPI_API_TOKEN = os.getenv("UAZAPI_API_TOKEN")
UAZAPI_INSTANCE_ID = os.getenv("UAZAPI_INSTANCE_ID")
UAZAPI_WEBHOOK_TOKEN = os.getenv("UAZAPI_WEBHOOK_TOKEN", "")

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
BOT_USERNAME = os.getenv("WHATSAPP_BOT_USERNAME", "whatsapp_bot")
BOT_PASSWORD = os.getenv("WHATSAPP_BOT_PASSWORD")
SESSION_TIMEOUT_MINUTES = int(os.getenv("WHATSAPP_SESSION_TIMEOUT_MINUTES", "10"))

WEBHOOK_PORT = int(os.getenv("WHATSAPP_WEBHOOK_PORT", "5001"))
WEBHOOK_HOST = os.getenv("WHATSAPP_WEBHOOK_HOST", "0.0.0.0")

MAX_MESSAGE_LENGTH = 4000

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [%(name)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("whatsapp_bot")

last_message_time = {}
processed_message_ids = set()
state_lock = Lock()


class UazapiClient:

    def __init__(self):
        self.base_url = UAZAPI_BASE_URL
        self.api_token = UAZAPI_API_TOKEN
        self.instance_id = UAZAPI_INSTANCE_ID

    def _headers(self) -> dict:
        return {
            "Content-Type": "application/json",
            "token": self.api_token
        }

    def send_text(self, phone: str, message: str) -> bool:
        try:
            response = requests.post(
                f"{self.base_url}/send/text",
                json={
                    "number": phone,
                    "text": message,
                    "linkPreview": True,
                    "readchat": True,
                    "readmessages": True
                },
                headers=self._headers(),
                timeout=15
            )

            if response.status_code == 200:
                logger.info(f"Message sent to {self._mask_phone(phone)}")
                return True
            elif response.status_code == 429:
                logger.warning("UAZAPI rate limit hit, retrying after 2s...")
                time.sleep(2)
                retry = requests.post(
                    f"{self.base_url}/send/text",
                    json={"number": phone, "text": message, "readchat": True},
                    headers=self._headers(),
                    timeout=15
                )
                if retry.status_code == 200:
                    logger.info(f"Message sent to {self._mask_phone(phone)} (after retry)")
                    return True
                logger.error(f"UAZAPI retry failed: {retry.status_code}")
                return False
            else:
                logger.error(f"UAZAPI send failed: {response.status_code} - {response.text}")
                return False

        except requests.exceptions.Timeout:
            logger.error("UAZAPI request timeout")
            return False
        except Exception as e:
            logger.error(f"Error sending WhatsApp message: {str(e)}")
            return False

    def send_long_message(self, phone: str, text: str) -> bool:
        if len(text) <= MAX_MESSAGE_LENGTH:
            return self.send_text(phone, text)

        chunks = self._split_at_paragraphs(text, MAX_MESSAGE_LENGTH)
        success = True
        for chunk in chunks:
            if not self.send_text(phone, chunk):
                success = False
        return success

    def get_instance_status(self) -> dict:
        try:
            response = requests.get(
                f"{self.base_url}/status",
                headers={"token": self.api_token},
                timeout=10
            )
            return response.json() if response.status_code == 200 else {"status": "error"}
        except Exception as e:
            logger.error(f"Error checking instance status: {str(e)}")
            return {"status": "error", "detail": str(e)}

    @staticmethod
    def _mask_phone(phone: str) -> str:
        if len(phone) > 4:
            return "*" * (len(phone) - 4) + phone[-4:]
        return "****"

    @staticmethod
    def _split_at_paragraphs(text: str, max_length: int) -> list:
        if len(text) <= max_length:
            return [text]

        chunks = []
        current = ""

        for paragraph in text.split("\n\n"):
            if len(current) + len(paragraph) + 2 <= max_length:
                current = f"{current}\n\n{paragraph}" if current else paragraph
            else:
                if current:
                    chunks.append(current.strip())
                if len(paragraph) <= max_length:
                    current = paragraph
                else:
                    for line in paragraph.split("\n"):
                        if len(current) + len(line) + 1 <= max_length:
                            current = f"{current}\n{line}" if current else line
                        else:
                            if current:
                                chunks.append(current.strip())
                            current = line

        if current:
            chunks.append(current.strip())

        return chunks


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

    def send_message(self, message: str, whatsapp_phone: str) -> dict:
        if not self.ensure_authenticated():
            return {
                "response": "Desculpe, estou com problemas de conexao com o servidor. Tente novamente em instantes.",
                "error": "authentication_failed"
            }

        try:
            user_id = f"whatsapp_{whatsapp_phone}"
            logger.info(f"[DEBUG] Sending to backend: user_id={user_id}")

            response = requests.post(
                f"{self.backend_url}/chat",
                json={"message": message},
                headers={"Authorization": f"Bearer {self.jwt_token}"},
                timeout=30
            )

            if response.status_code == 200:
                result = response.json()
                logger.info(f"[DEBUG] Backend response received: agent={result.get('agent_used', 'unknown')}")
                return result
            else:
                logger.error(f"Backend error: {response.status_code} - {response.text}")
                return {
                    "response": "Desculpe, ocorreu um erro ao processar sua mensagem. Tente novamente.",
                    "error": f"backend_error_{response.status_code}"
                }

        except requests.exceptions.Timeout:
            logger.error("Backend request timeout")
            return {
                "response": "Desculpe, a resposta esta demorando muito. Tente uma pergunta mais simples.",
                "error": "timeout"
            }
        except Exception as e:
            logger.error(f"Error sending message to backend: {str(e)}")
            return {
                "response": "Desculpe, ocorreu um erro inesperado. Tente novamente.",
                "error": str(e)
            }


def format_for_whatsapp(text: str) -> str:
    text = re.sub(r'^#+\s+', '', text, flags=re.MULTILINE)
    text = re.sub(r'\*\*(.*?)\*\*', r'*\1*', text)
    text = re.sub(r'__(.*?)__', r'_\1_', text)
    text = re.sub(r'(?<!`)`([^`]+)`(?!`)', r'```\1```', text)
    return text


def strip_all_formatting(text: str) -> str:
    text = re.sub(r'^#+\s+', '', text, flags=re.MULTILINE)
    text = text.replace("**", "")
    text = text.replace("__", "")
    text = text.replace("*", "")
    text = text.replace("_", "")
    text = text.replace("`", "")
    text = text.replace("~", "")
    return text


def sanitize_and_enrich_message(message: str, contact_name: str) -> str:
    clean_message = re.sub(
        r'\[User\'?s?\s+real\s+first\s+name\s+is:.*?\]',
        '',
        message,
        flags=re.IGNORECASE
    ).strip()

    enriched_message = f"{clean_message}\n\n[User's real first name is: {contact_name}]"
    return enriched_message


def extract_contact_name(webhook_data: dict) -> str:
    try:
        chat = webhook_data.get("chat", {})
        name = chat.get("wa_name", "") or chat.get("name", "")
        if name:
            return name
        push_name = webhook_data.get("data", {}).get("pushName", "")
        if push_name:
            return push_name
        return "Usuario"
    except Exception:
        return "Usuario"


def is_duplicate_message(message_id: str) -> bool:
    with state_lock:
        if message_id in processed_message_ids:
            logger.warning(f"[DEDUP] Duplicate message detected (ID: {message_id}), skipping")
            return True

        processed_message_ids.add(message_id)
        logger.info(f"[DEDUP] Added message_id={message_id} to processed set (total: {len(processed_message_ids)})")

        if len(processed_message_ids) > 1000:
            processed_message_ids.clear()
            logger.info("Cleared processed message IDs cache")

        return False


def check_session_status(phone: str) -> bool:
    now = datetime.now()

    with state_lock:
        if phone in last_message_time:
            time_since_last = now - last_message_time[phone]
            if time_since_last > timedelta(minutes=SESSION_TIMEOUT_MINUTES):
                logger.info(f"Phone {UazapiClient._mask_phone(phone)} session timeout ({SESSION_TIMEOUT_MINUTES}min) - new session")
                last_message_time[phone] = now
                return True
            last_message_time[phone] = now
            return False
        else:
            logger.info(f"Phone {UazapiClient._mask_phone(phone)} first message - new session")
            last_message_time[phone] = now
            return True


def normalize_phone(phone: str) -> str:
    phone = phone.replace("@s.whatsapp.net", "").replace("@g.us", "")
    phone = re.sub(r'[\s\-\(\)\+]', '', phone)
    return phone


uazapi = UazapiClient()
backend = BackendClient()

app = Flask(__name__)


@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        data = request.get_json()

        if not data:
            return jsonify({"status": "error", "message": "No data"}), 400

        print(f"[WEBHOOK RAW] {json.dumps(data, default=str)[:2000]}", flush=True)

        if UAZAPI_WEBHOOK_TOKEN:
            token = request.headers.get("X-Webhook-Token", "")
            if token != UAZAPI_WEBHOOK_TOKEN:
                print(f"[WEBHOOK] Invalid token received", flush=True)
                return jsonify({"status": "unauthorized"}), 401

        event_type = data.get("EventType", "") or data.get("event", "")
        print(f"[WEBHOOK] event_type='{event_type}'", flush=True)

        if event_type not in ("messages", "messages.upsert", "message"):
            print(f"[WEBHOOK] Ignoring non-message event: {event_type}", flush=True)
            return jsonify({"status": "ignored"}), 200

        msg = data.get("message", {})
        chat = data.get("chat", {})
        message_id = msg.get("messageid", "") or msg.get("id", "")
        from_me = msg.get("fromMe", False)
        remote_jid = msg.get("chatid", "") or chat.get("wa_chatid", "")
        is_group = msg.get("isGroup", False) or chat.get("wa_isGroup", False)

        if is_group or "@g.us" in remote_jid:
            logger.debug(f"Ignoring group message from {remote_jid}")
            return jsonify({"status": "skipped_group"}), 200

        if from_me:
            return jsonify({"status": "skipped_own"}), 200

        phone = chat.get("phone", "") or normalize_phone(remote_jid)
        if not phone:
            return jsonify({"status": "skipped_no_phone"}), 200

        message_text = msg.get("content", "")

        if not message_text:
            media_type = msg.get("mediaType", "")
            message_type = msg.get("messageType", "")
            is_media = bool(media_type) or message_type not in ("Conversation", "extendedTextMessage", "")
            if is_media:
                uazapi.send_text(
                    phone,
                    "Desculpe, no momento so consigo processar mensagens de texto. "
                    "Por favor, envie sua pergunta como texto."
                )
                return jsonify({"status": "media_rejected"}), 200
            return jsonify({"status": "skipped_empty"}), 200

        if is_duplicate_message(message_id):
            return jsonify({"status": "duplicate"}), 200

        is_new_session = check_session_status(phone)

        contact_name = extract_contact_name(data)

        logger.info(f"[HANDLER START] phone={UazapiClient._mask_phone(phone)}, message_id={message_id}, text='{message_text[:20]}...'")
        logger.info(f"Phone {UazapiClient._mask_phone(phone)} sent message: '{message_text[:50]}...'")

        enriched_message = sanitize_and_enrich_message(message_text, contact_name)

        result = backend.send_message(enriched_message, phone)

        response_text = result.get("response", "Desculpe, nao consegui processar sua mensagem.")

        formatted_response = format_for_whatsapp(response_text)

        send_success = uazapi.send_long_message(phone, formatted_response)

        if not send_success:
            plain_text = strip_all_formatting(response_text)
            uazapi.send_long_message(phone, plain_text)

        logger.info(f"Phone {UazapiClient._mask_phone(phone)} received response (agent: {result.get('agent_used', 'unknown')})")

        return jsonify({"status": "processed"}), 200

    except Exception as e:
        logger.error(f"Webhook error: {str(e)}", exc_info=True)
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/webhook", methods=["GET"])
def webhook_verify():
    return jsonify({
        "status": "active",
        "service": "cloudwalk-whatsapp-bot",
        "timestamp": datetime.now().isoformat()
    }), 200


@app.route("/health", methods=["GET"])
def health():
    instance_status = uazapi.get_instance_status()
    return jsonify({
        "status": "healthy",
        "uazapi_instance": instance_status.get("status", "unknown"),
        "backend_authenticated": backend.jwt_token is not None
    }), 200


def main():
    if not UAZAPI_API_TOKEN:
        logger.error("UAZAPI_API_TOKEN not found in environment variables!")
        logger.error("Please add it to your .env file")
        sys.exit(1)

    if not UAZAPI_INSTANCE_ID:
        logger.error("UAZAPI_INSTANCE_ID not found in environment variables!")
        logger.error("Please add it to your .env file")
        sys.exit(1)

    if not BOT_PASSWORD:
        logger.error("WHATSAPP_BOT_PASSWORD not found in environment variables!")
        logger.error("Please add it to your .env file")
        sys.exit(1)

    logger.info("=" * 60)
    logger.info("CloudWalk WhatsApp Bot Connector Starting...")
    logger.info(f"Backend URL: {BACKEND_URL}")
    logger.info(f"Bot Username: {BOT_USERNAME}")
    logger.info(f"UAZAPI Base URL: {UAZAPI_BASE_URL}")
    logger.info(f"UAZAPI Instance: {UAZAPI_INSTANCE_ID}")
    logger.info(f"Webhook Port: {WEBHOOK_PORT}")
    logger.info("=" * 60)

    if not backend.login():
        logger.error("Failed to authenticate with backend on startup!")
        logger.error("Make sure:")
        logger.error("1. Backend is running")
        logger.error("2. User 'whatsapp_bot' exists in backend")
        logger.error("3. WHATSAPP_BOT_PASSWORD in .env matches user password")
        sys.exit(1)

    status = uazapi.get_instance_status()
    logger.info(f"UAZAPI instance status: {status}")

    logger.info("WhatsApp webhook server starting...")
    logger.info(f"Listening on {WEBHOOK_HOST}:{WEBHOOK_PORT}")
    logger.info("Configure UAZAPI webhook URL to point to this server's /webhook endpoint")

    app.run(host=WEBHOOK_HOST, port=WEBHOOK_PORT, debug=False)


if __name__ == "__main__":
    main()
