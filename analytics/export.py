"""Сборка Excel-отчёта по визитам и выгрузка его на Яндекс.Диск.

Отчёт содержит только псевдонимный telegram_id, временные метки и то, какие
разделы бота смотрели — без имени, username, телефона или иных персональных
данных (см. пояснение в analytics/storage.py).
"""

import asyncio
import io
import logging

import aiohttp
from openpyxl import Workbook
from openpyxl.styles import Font

import config
from analytics.storage import fetch_events, fetch_visitors

logger = logging.getLogger(__name__)

YANDEX_API_BASE = "https://cloud-api.yandex.net/v1/disk"

# Не выгружаем отчёт на каждый клик — ждём паузу в потоке событий, чтобы не
# засыпать Яндекс.Диск запросами при активном использовании бота.
EXPORT_DEBOUNCE_SECONDS = 15

_dirty = False
_scheduled = False
_lock = asyncio.Lock()


def build_workbook() -> bytes:
    wb = Workbook()

    ws1 = wb.active
    ws1.title = "Посетители"
    ws1.append(["ID аккаунта (Telegram)", "Первый визит", "Последний визит", "Кол-во визитов"])
    for cell in ws1[1]:
        cell.font = Font(bold=True)
    for telegram_id, first_seen, last_seen, visits in fetch_visitors():
        ws1.append([telegram_id, first_seen, last_seen, visits])
    for column_cells in ws1.columns:
        length = max(len(str(c.value)) for c in column_cells)
        ws1.column_dimensions[column_cells[0].column_letter].width = max(18, length + 2)

    ws2 = wb.create_sheet("События")
    ws2.append(["ID аккаунта (Telegram)", "Время", "Действие"])
    for cell in ws2[1]:
        cell.font = Font(bold=True)
    for telegram_id, ts, action in fetch_events():
        ws2.append([telegram_id, ts, action])
    for column_cells in ws2.columns:
        length = max(len(str(c.value)) for c in column_cells)
        ws2.column_dimensions[column_cells[0].column_letter].width = max(18, length + 2)

    buffer = io.BytesIO()
    wb.save(buffer)
    return buffer.getvalue()


async def upload_to_yandex_disk(data: bytes) -> None:
    token = config.YANDEX_DISK_TOKEN
    if not token:
        logger.debug("YANDEX_DISK_TOKEN не задан — выгрузка на Яндекс.Диск пропущена")
        return

    path = config.YANDEX_DISK_PATH
    headers = {"Authorization": f"OAuth {token}"}

    async with aiohttp.ClientSession(headers=headers) as session:
        folder = path.rsplit("/", 1)[0] or "/"
        if folder and folder != "/":
            async with session.put(
                f"{YANDEX_API_BASE}/resources",
                params={"path": folder},
            ) as resp:
                if resp.status not in (201, 409):
                    logger.warning("Не удалось создать папку %s на Яндекс.Диске: %s", folder, resp.status)

        async with session.get(
            f"{YANDEX_API_BASE}/resources/upload",
            params={"path": path, "overwrite": "true"},
        ) as resp:
            if resp.status != 200:
                body = await resp.text()
                logger.error("Яндекс.Диск: не удалось получить ссылку для загрузки (%s): %s", resp.status, body)
                return
            upload_info = await resp.json()

        async with session.put(upload_info["href"], data=data) as resp:
            if resp.status not in (201, 202):
                body = await resp.text()
                logger.error("Яндекс.Диск: ошибка загрузки файла (%s): %s", resp.status, body)
            else:
                logger.info("Отчёт visits.xlsx выгружен на Яндекс.Диск: %s", path)


async def export_and_upload() -> None:
    try:
        data = build_workbook()
        await upload_to_yandex_disk(data)
    except Exception:
        logger.exception("Ошибка при формировании/выгрузке отчёта по визитам")


async def _debounced_export() -> None:
    global _dirty, _scheduled
    await asyncio.sleep(EXPORT_DEBOUNCE_SECONDS)
    async with _lock:
        _scheduled = False
        if _dirty:
            _dirty = False
            await export_and_upload()


def schedule_export() -> None:
    """Планирует фоновую пересборку и выгрузку отчёта, не блокируя ответ бота."""
    global _dirty, _scheduled
    _dirty = True
    if not _scheduled:
        _scheduled = True
        asyncio.create_task(_debounced_export())
