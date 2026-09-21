"""Локальный учёт посещений бота.

Важно (152-ФЗ «О персональных данных»): мы намеренно НЕ сохраняем username,
имя, фамилию, телефон или текст сообщений пользователя — только:
- telegram_id — числовой идентификатор аккаунта в Telegram (сам по себе
  не раскрывает личность человека без доступа к данным самого Telegram);
- временные метки визитов;
- какие разделы/кейсы бота смотрели (callback_data или имя команды вида
  "/start" — свободный текст, который пользователь мог бы ввести сам,
  никогда не сохраняется).

Это позволяет видеть "кто-то (аккаунт №...) заходил тогда-то и смотрел то-то"
и отличать повторных посетителей от новых, не собирая персональные данные.
"""

import sqlite3
from contextlib import closing
from datetime import datetime, timedelta, timezone
from pathlib import Path

DB_PATH = Path(__file__).parent / "visits.db"

# Пауза, после которой новое обращение считается отдельным визитом, а не
# продолжением текущего (типовое окно сессии в веб-аналитике).
SESSION_GAP = timedelta(minutes=30)

MSK = timezone(timedelta(hours=3))


def _now() -> datetime:
    return datetime.now(MSK)


def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def init_db() -> None:
    with closing(_connect()) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS visitors (
                telegram_id INTEGER PRIMARY KEY,
                first_seen  TEXT NOT NULL,
                last_seen   TEXT NOT NULL,
                visits      INTEGER NOT NULL DEFAULT 1
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS events (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_id INTEGER NOT NULL,
                ts          TEXT NOT NULL,
                action      TEXT NOT NULL
            )
            """
        )
        conn.commit()


def record_event(telegram_id: int, action: str) -> None:
    now = _now()
    now_str = now.isoformat(timespec="seconds")

    with closing(_connect()) as conn:
        row = conn.execute(
            "SELECT last_seen, visits FROM visitors WHERE telegram_id = ?",
            (telegram_id,),
        ).fetchone()

        if row is None:
            conn.execute(
                "INSERT INTO visitors (telegram_id, first_seen, last_seen, visits) VALUES (?, ?, ?, 1)",
                (telegram_id, now_str, now_str),
            )
        else:
            last_seen = datetime.fromisoformat(row[0])
            visits = row[1]
            if now - last_seen > SESSION_GAP:
                visits += 1
            conn.execute(
                "UPDATE visitors SET last_seen = ?, visits = ? WHERE telegram_id = ?",
                (now_str, visits, telegram_id),
            )

        conn.execute(
            "INSERT INTO events (telegram_id, ts, action) VALUES (?, ?, ?)",
            (telegram_id, now_str, action),
        )
        conn.commit()


def fetch_visitors() -> list[tuple]:
    with closing(_connect()) as conn:
        return conn.execute(
            "SELECT telegram_id, first_seen, last_seen, visits FROM visitors ORDER BY last_seen DESC"
        ).fetchall()


def fetch_events(limit: int = 5000) -> list[tuple]:
    with closing(_connect()) as conn:
        return conn.execute(
            "SELECT telegram_id, ts, action FROM events ORDER BY ts DESC LIMIT ?",
            (limit,),
        ).fetchall()
