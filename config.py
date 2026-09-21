import os

from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.environ["BOT_TOKEN"]
ADMIN_ID = int(os.environ.get("ADMIN_ID", "0")) or None
CONTACT_USERNAME = os.environ.get("CONTACT_USERNAME", "")
CONTACT_EMAIL = os.environ.get("CONTACT_EMAIL", "")
GITHUB_URL = os.environ.get("GITHUB_URL", "")

# Яндекс.Диск: выгрузка Excel-отчёта по визитам (см. analytics/export.py).
# Токен получить на https://yandex.ru/dev/disk/poligon/ (кнопка "Получить OAuth-токен").
YANDEX_DISK_TOKEN = os.environ.get("YANDEX_DISK_TOKEN", "")
YANDEX_DISK_PATH = os.environ.get("YANDEX_DISK_PATH", "/Signea/Бот-визитка/visits.xlsx")
