"""Генерация аватара для бота @signea_cases_bot.

Концепция: буква "S" (Signea) на диагональном градиенте indigo -> violet -> blue
(тех/AI-палитра), с акцентной "искрой"-узлом на хвосте буквы, символизирующей
AI/автоматизацию, и тонкими линиями-узлами (намёк на no-code/воркфлоу).

Запуск: .venv/Scripts/python assets/avatar/generate_avatar.py
Результат: assets/avatar/avatar.png (1024x1024, для загрузки в @BotFather /setuserpic)
"""

import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

SIZE = 1024
OUT = Path(__file__).parent / "avatar.png"
FONT_PATH = r"C:\Windows\Fonts\seguibl.ttf"  # Segoe UI Black

COLOR_TOP_LEFT = (26, 22, 74)      # тёмный indigo
COLOR_BOTTOM_RIGHT = (70, 60, 230)  # яркий violet-blue
ACCENT = (0, 224, 255)             # голубая "искра" (AI-акцент)
ACCENT_SOFT = (140, 235, 255)


def make_gradient(size: int) -> Image.Image:
    base = Image.new("RGB", (size, size), COLOR_TOP_LEFT)
    top_left = COLOR_TOP_LEFT
    bottom_right = COLOR_BOTTOM_RIGHT
    for y in range(size):
        for_row = Image.new("RGB", (size, 1))
        row_px = for_row.load()
        for x in range(size):
            t = (x + y) / (2 * size)
            r = int(top_left[0] + (bottom_right[0] - top_left[0]) * t)
            g = int(top_left[1] + (bottom_right[1] - top_left[1]) * t)
            b = int(top_left[2] + (bottom_right[2] - top_left[2]) * t)
            row_px[x, 0] = (r, g, b)
        base.paste(for_row, (0, y))
    return base


def make_gradient_fast(size: int) -> Image.Image:
    # Быстрее построчной версии: используем numpy-подобный подход через resize.
    small = 64
    grad = Image.new("RGB", (small, small))
    px = grad.load()
    for y in range(small):
        for x in range(small):
            t = (x + y) / (2 * small)
            r = int(COLOR_TOP_LEFT[0] + (COLOR_BOTTOM_RIGHT[0] - COLOR_TOP_LEFT[0]) * t)
            g = int(COLOR_TOP_LEFT[1] + (COLOR_BOTTOM_RIGHT[1] - COLOR_TOP_LEFT[1]) * t)
            b = int(COLOR_TOP_LEFT[2] + (COLOR_BOTTOM_RIGHT[2] - COLOR_TOP_LEFT[2]) * t)
            px[x, y] = (r, g, b)
    return grad.resize((size, size), Image.BICUBIC)


def draw_node_lines(draw: ImageDraw.ImageDraw, size: int) -> None:
    # Тонкая сетка узлов-точек на заднем плане — намёк на no-code/workflow.
    import random

    random.seed(7)
    nodes = []
    for _ in range(14):
        x = random.randint(int(size * 0.08), int(size * 0.92))
        y = random.randint(int(size * 0.08), int(size * 0.92))
        nodes.append((x, y))

    for i, (x1, y1) in enumerate(nodes):
        for x2, y2 in nodes[i + 1:]:
            dist = math.hypot(x2 - x1, y2 - y1)
            if dist < size * 0.22:
                draw.line([(x1, y1), (x2, y2)], fill=(255, 255, 255, 18), width=2)

    for x, y in nodes:
        r = 4
        draw.ellipse([x - r, y - r, x + r, y + r], fill=(255, 255, 255, 40))


def main() -> None:
    base = make_gradient_fast(SIZE).convert("RGBA")

    overlay = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    draw_node_lines(ImageDraw.Draw(overlay), SIZE)
    base = Image.alpha_composite(base, overlay)

    # Мягкое затемнение по краям (виньетка), чтобы буква читалась лучше.
    vignette = Image.new("L", (SIZE, SIZE), 0)
    vdraw = ImageDraw.Draw(vignette)
    vdraw.ellipse([-SIZE * 0.25, -SIZE * 0.25, SIZE * 1.25, SIZE * 1.25], fill=60)
    vignette = vignette.filter(ImageFilter.GaussianBlur(SIZE * 0.15))
    dark = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 255))
    base = Image.composite(base, Image.alpha_composite(base, Image.merge("RGBA", (*dark.split()[:3], vignette))), Image.new("L", (SIZE, SIZE), 255))

    draw = ImageDraw.Draw(base)

    # Буква "S"
    font_size = int(SIZE * 0.62)
    font = ImageFont.truetype(FONT_PATH, font_size)
    text = "S"
    bbox = draw.textbbox((0, 0), text, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    tx = (SIZE - tw) / 2 - bbox[0]
    ty = (SIZE - th) / 2 - bbox[1] - SIZE * 0.02

    # Лёгкая тень под буквой для глубины
    shadow = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    sdraw = ImageDraw.Draw(shadow)
    sdraw.text((tx + 10, ty + 14), text, font=font, fill=(0, 0, 0, 120))
    shadow = shadow.filter(ImageFilter.GaussianBlur(14))
    base = Image.alpha_composite(base, shadow)
    draw = ImageDraw.Draw(base)

    draw.text((tx, ty), text, font=font, fill=(255, 255, 255, 255))

    # Акцентная "искра" на конце нижнего хвоста буквы S (справа снизу от центра)
    spark_x = SIZE * 0.665
    spark_y = SIZE * 0.775

    glow = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    gdraw = ImageDraw.Draw(glow)
    gr = SIZE * 0.09
    gdraw.ellipse([spark_x - gr, spark_y - gr, spark_x + gr, spark_y + gr], fill=(*ACCENT, 160))
    glow = glow.filter(ImageFilter.GaussianBlur(SIZE * 0.035))
    base = Image.alpha_composite(base, glow)
    draw = ImageDraw.Draw(base)

    r = SIZE * 0.028
    draw.ellipse([spark_x - r, spark_y - r, spark_x + r, spark_y + r], fill=ACCENT_SOFT)
    r2 = r * 0.5
    draw.ellipse([spark_x - r2, spark_y - r2, spark_x + r2, spark_y + r2], fill=(255, 255, 255, 255))

    base.convert("RGB").save(OUT, "PNG", quality=95)
    print(f"Saved: {OUT}")


if __name__ == "__main__":
    main()
