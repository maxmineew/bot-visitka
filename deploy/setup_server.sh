#!/usr/bin/env bash
# Настройка бота на сервере Beget (VPS/облачный сервер, Ubuntu/Debian).
#
# Запускать на сервере от root ПОСЛЕ того, как код проекта уже загружен
# в APP_DIR (см. раздел «Деплой на Beget» в README.md — команда tar+ssh).
#
# Использование:
#   sudo bash deploy/setup_server.sh
#
# Скрипт идемпотентен — его можно безопасно запускать повторно (например,
# после обновления кода), чтобы переустановить зависимости и перезапустить
# сервис.

set -euo pipefail

APP_DIR="/opt/bot-visitka"
APP_USER="bot-visitka"

if [ "$(id -u)" -ne 0 ]; then
    echo "Запустите скрипт от root (sudo bash deploy/setup_server.sh)" >&2
    exit 1
fi

if [ ! -d "$APP_DIR" ]; then
    echo "Не найдена директория $APP_DIR — сначала загрузите туда код проекта" >&2
    exit 1
fi

echo "==> Устанавливаю системные пакеты (python3-venv, python3-pip)"
apt-get update -qq
apt-get install -y -qq python3-venv python3-pip

if ! id "$APP_USER" >/dev/null 2>&1; then
    echo "==> Создаю системного пользователя $APP_USER"
    useradd --system --home "$APP_DIR" --shell /usr/sbin/nologin "$APP_USER"
fi

if [ ! -d "$APP_DIR/.venv" ]; then
    echo "==> Создаю виртуальное окружение"
    python3 -m venv "$APP_DIR/.venv"
fi

echo "==> Устанавливаю зависимости"
"$APP_DIR/.venv/bin/pip" install --upgrade pip -q
"$APP_DIR/.venv/bin/pip" install -q -r "$APP_DIR/requirements.txt"

if [ ! -f "$APP_DIR/.env" ]; then
    echo "ВНИМАНИЕ: файл $APP_DIR/.env не найден — бот не сможет запуститься." >&2
    echo "Загрузите .env отдельно (например, scp .env root@сервер:$APP_DIR/.env) и запустите скрипт ещё раз." >&2
    exit 1
fi

echo "==> Настраиваю права доступа"
chown -R "$APP_USER":"$APP_USER" "$APP_DIR"
chmod 600 "$APP_DIR/.env"

echo "==> Устанавливаю systemd-сервис"
cp "$APP_DIR/deploy/bot-visitka.service" /etc/systemd/system/bot-visitka.service
systemctl daemon-reload
systemctl enable --now bot-visitka
systemctl restart bot-visitka

sleep 2
echo "==> Статус сервиса:"
systemctl status bot-visitka --no-pager -l || true

echo
echo "Готово. Логи: journalctl -u bot-visitka -f"
