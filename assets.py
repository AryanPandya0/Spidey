import os
from PyQt5.QtGui import QImage, QPainter, QColor, QPixmap
from PyQt5.QtCore import Qt, QRect
from config import Config

class Assets:
    _sprites = {}
    SPRITESHEET_PATH = os.path.join("assets", "spidey_pixel_pro.png")

    @classmethod
    def get_sprites(cls, state):
        if not cls._sprites:
            cls.generate_all()
        return cls._sprites.get(state, [])

    @classmethod
    def generate_all(cls):
        # States: IDLE, WALK, RUN, JUMP, CRAWL, SWING
        # Row mapping (128x128 grid)
        # Row 0: IDLE (6 frames)
        # Row 1: WALK (8 frames)
        # Row 2: RUN (8 frames)
        # Row 3: JUMP (8 frames)
        # Row 4: CRAWL (8 frames)
        # Row 5: SWING (8 frames)
        
        if not os.path.exists(cls.SPRITESHEET_PATH):
            print(f"Error: Spritesheet not found at {cls.SPRITESHEET_PATH}")
            return

        full_sheet = QImage(cls.SPRITESHEET_PATH)
        if full_sheet.isNull():
            print(f"Error: Failed to load spritesheet from {cls.SPRITESHEET_PATH}")
            return

        # Ensure we are working with ARGB32 for transparency
        full_sheet = full_sheet.convertToFormat(QImage.Format_ARGB32)
        
        # Transparent background removal (assuming white background)
        # We look for pixels near white and make them transparent.
        # This is a basic approach; for pixel art a perfect mask is better.
        for y in range(full_sheet.height()):
            for x in range(full_sheet.width()):
                c = full_sheet.pixelColor(x, y)
                if c.red() > 245 and c.green() > 245 and c.blue() > 245:
                    full_sheet.setPixelColor(x, y, QColor(0, 0, 0, 0))

        size = Config.SPRITE_BASE_SIZE # 128
        
        cls._sprites['IDLE'] = cls._slice_sheet(full_sheet, 0, 6, size)
        cls._sprites['WALK'] = cls._slice_sheet(full_sheet, 1, 8, size)
        cls._sprites['RUN'] = cls._slice_sheet(full_sheet, 2, 8, size)
        cls._sprites['JUMP'] = cls._slice_sheet(full_sheet, 3, 8, size)
        cls._sprites['CRAWL'] = cls._slice_sheet(full_sheet, 4, 8, size)
        cls._sprites['SWING'] = cls._slice_sheet(full_sheet, 5, 8, size)

    @classmethod
    def _slice_sheet(cls, sheet, row, num_frames, size):
        frames = []
        for i in range(num_frames):
            rect = QRect(i * size, row * size, size, size)
            frame_img = sheet.copy(rect)
            # Scale up to RENDER_SIZE
            scaled = frame_img.scaled(Config.RENDER_SIZE, Config.RENDER_SIZE, Qt.KeepAspectRatio, Qt.FastTransformation)
            frames.append(QPixmap.fromImage(scaled))
        return frames
