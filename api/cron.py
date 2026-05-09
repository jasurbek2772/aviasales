# api/cron.py
import json
from http.server import BaseHTTPRequestHandler
import asyncio
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from bot_logic import send_links_to_chat

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Этот метод вызывается Vercel Cron"""
        status_code = 200
        response_body = {"message": "Cron job started"}
        
        try:
            # Запускаем асинхронную функцию отправки
            result = asyncio.run(send_links_to_chat())
            if result:
                response_body["status"] = "success"
            else:
                response_body["status"] = "failed"
                status_code = 500
        except Exception as e:
            response_body["error"] = str(e)
            status_code = 500

        self.send_response(status_code)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(response_body).encode())
