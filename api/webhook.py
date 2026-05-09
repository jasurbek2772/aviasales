# api/webhook.py
import os
import json
from http.server import BaseHTTPRequestHandler
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Импорт логики
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from bot_logic import TELEGRAM_TOKEN, make_message, send_links_to_chat

# Инициализация приложения один раз (глобально)
app = Application.builder().token(TELEGRAM_TOKEN).build()

async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Привет!\n\n"
        "Я бот для мониторинга цен TAS → KJA.\n"
        "Используйте /links для получения ссылок."
    )

async def cmd_links(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        make_message(),
        parse_mode="Markdown",
        disable_web_page_preview=True,
    )

async def cmd_chatid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cid = update.effective_chat.id
    await update.message.reply_text(
        f"🆔 Ваш Chat ID: `{cid}`",
        parse_mode="Markdown",
    )

# Регистрируем хендлеры
app.add_handler(CommandHandler("start", cmd_start))
app.add_handler(CommandHandler("links", cmd_links))
app.add_handler(CommandHandler("chatid", cmd_chatid))

class handler(BaseHTTPRequestHandler):
    async def post(self):
        """Обработка входящих обновлений от Telegram"""
        content_length = int(self.headers['Content-Length'])
        body = self.rfile.read(content_length)
        self.send_response(200)
        self.end_headers()
        
        # Парсим обновление
        update = Update.de_json(json.loads(body), app.bot)
        
        # Обрабатываем
        await app.process_update(update)
        
        self.wfile.write(b"OK")

    def do_POST(self):
        import asyncio
        asyncio.run(self.post())
