import os

from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.environ["BOT_TOKEN"]
# Необязательный HTTP-прокси для api.telegram.org, например http://user:pass@host:port
BOT_PROXY = os.environ.get("BOT_PROXY", "")
ADMIN_ID = int(os.environ.get("ADMIN_ID", "0")) or None
CONTACT_USERNAME = os.environ.get("CONTACT_USERNAME", "")
CONTACT_EMAIL = os.environ.get("CONTACT_EMAIL", "")
GITHUB_URL = os.environ.get("GITHUB_URL", "")

# Оператор персональных данных (152-ФЗ) — подставляется в политику конфиденциальности.
OPERATOR_NAME = os.environ.get("OPERATOR_NAME", "Максим Минеев")
OPERATOR_INN = os.environ.get("OPERATOR_INN", "")
OPERATOR_EMAIL = os.environ.get("OPERATOR_EMAIL", "") or CONTACT_EMAIL
# Через сколько дней после последнего обращения данные пользователя удаляются.
RETENTION_DAYS = int(os.environ.get("RETENTION_DAYS", "365"))

# Яндекс.Диск: выгрузка Excel-отчёта по визитам (см. analytics/export.py).
# Токен получить на https://yandex.ru/dev/disk/poligon/ (кнопка "Получить OAuth-токен").
YANDEX_DISK_TOKEN = os.environ.get("YANDEX_DISK_TOKEN", "")
YANDEX_DISK_PATH = os.environ.get("YANDEX_DISK_PATH", "/Signea/Бот-визитка/visits.xlsx")
