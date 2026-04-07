from __future__ import annotations

from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
SOURCE_PATH = ROOT / "assets" / "spidey_pro_v2.png"
OUTPUT_PATH = ROOT / "assets" / "spidey_pro_clean.png"

GRID_COLS = 8
GRID_ROWS = 6
CELL_SIZE = 128
TARGET_SIZE = 128
PADDING = 10
WHITE_THRESHOLD = 240
INNER_X_MARGIN = 2
ROW_BANDS = (
    (31, 126),
    (160, 255),
    (287, 383),
    (415, 511),
    (544, 639),
    (672, 767),
)


def crop_character(frame_region: Image.Image) -> Image.Image:
    cropped = frame_region.convert("RGBA")
    rgba_pixels = cropped.load()
    for y in range(cropped.height):
        for x in range(cropped.width):
            r, g, b, _ = rgba_pixels[x, y]
            if r >= WHITE_THRESHOLD and g >= WHITE_THRESHOLD and b >= WHITE_THRESHOLD:
                rgba_pixels[x, y] = (0, 0, 0, 0)

    bbox = cropped.getbbox()
    if bbox is None:
        return Image.new("RGBA", (TARGET_SIZE, TARGET_SIZE), (0, 0, 0, 0))

    trimmed = cropped.crop(bbox)
    max_w = TARGET_SIZE - (PADDING * 2)
    max_h = TARGET_SIZE - (PADDING * 2)
    scale = min(max_w / trimmed.width, max_h / trimmed.height, 1.0)
    resized = trimmed.resize(
        (max(1, int(trimmed.width * scale)), max(1, int(trimmed.height * scale))),
        Image.Resampling.LANCZOS,
    )

    canvas = Image.new("RGBA", (TARGET_SIZE, TARGET_SIZE), (0, 0, 0, 0))
    offset_x = (TARGET_SIZE - resized.width) // 2
    offset_y = TARGET_SIZE - PADDING - resized.height
    canvas.alpha_composite(resized, (offset_x, offset_y))
    return canvas


def build_sheet() -> None:
    source = Image.open(SOURCE_PATH).convert("RGB")
    output = Image.new(
        "RGBA",
        (GRID_COLS * TARGET_SIZE, GRID_ROWS * TARGET_SIZE),
        (0, 0, 0, 0),
    )

    for row, (top, bottom) in enumerate(ROW_BANDS):
        for col in range(GRID_COLS):
            left = (col * CELL_SIZE) + INNER_X_MARGIN
            right = ((col + 1) * CELL_SIZE) - INNER_X_MARGIN
            frame_region = source.crop((left, top, right, bottom))
            frame = crop_character(frame_region)
            output.alpha_composite(frame, (col * TARGET_SIZE, row * TARGET_SIZE))

    output.save(OUTPUT_PATH)
    print(f"Saved cleaned spritesheet to {OUTPUT_PATH}")


if __name__ == "__main__":
    build_sheet()
