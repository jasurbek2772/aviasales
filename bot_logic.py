# bot_logic.py
import logging
import os
from datetime import datetime, date, timedelta
from dotenv import load_dotenv

# Загрузка переменных окружения (для локального теста)
load_dotenv()

logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "")
CHAT_ID = os.getenv("CHAT_ID", "")
INTERVAL_HOURS = int(os.getenv("INTERVAL_HOURS", "5"))

ORIGIN = "TAS"
DESTINATION = "KJA"
DATE_FROM = date(2026, 8, 10)
DATE_TO = date(2026, 8, 18)


def make_link(d: date) -> str:
    return (
        f"https://www.aviasales.ru/search/"
        f"{ORIGIN}{d.day:02d}{d.month:02d}{DESTINATION}1"
    )


def make_message() -> str:
    lines = [
        "✈️  Ташкент → Красноярск ",
        f"📅 Проверьте цены на каждый день: ",
        f"🕐 {datetime.now().strftime('%d.%m.%Y %H:%M')} ",
        " ",
    ]
    d = DATE_FROM
    while d <= DATE_TO:
        weekday = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"][d.weekday()]
        lines.append(f" [{d.strftime('%d.%m')} {weekday}]({make_link(d)}) ")
        d += timedelta(days=1)
    
    lines += [
        "",
        f"_Следующая проверка через {INTERVAL_HOURS} ч._",
    ]
    return "\n".join(lines)


async def send_links_to_chat() -> bool:
    """Отправляет сообщение в чат. Возвращает True при успехе."""
    if not CHAT_ID or not TELEGRAM_TOKEN:
        logger.warning("CHAT_ID или TOKEN не заданы")
        return False
    
    text = make_message()
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    
    import aiohttp
    try:
        async with aiohttp.ClientSession() as session:
            payload = {
                "chat_id": CHAT_ID,
                "text": text,
                "parse_mode": "Markdown",
                "disable_web_page_preview": True
            }
            async with session.post(url, json=payload) as resp:
                if resp.status == 200:
                    logger.info("Ссылки успешно отправлены")
                    return True
                else:
                    logger.error(f"Ошибка Telegram API: {resp.status}")
                    return False
    except Exception as e:
        logger.error(f"Ошибка отправки: {e}")
        return False
