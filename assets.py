import os
from PyQt5.QtGui import QImage, QColor, QPixmap
from PyQt5.QtCore import Qt, QRect
from config import Config

class Assets:
    _sprites = {}
    SPRITESHEET_PATH = os.path.join("assets", "spidey_master.png")

    @classmethod
    def get_sprites(cls, state):
        if not cls._sprites:
            cls.generate_all()
        return cls._sprites.get(state, [])

    @classmethod
    def generate_all(cls):
        # Master sheet rows:
        # 0: IDLE, 1: WALK, 2: RUN, 3: JUMP/FALL, 4: CRAWL, 5: SWING
        # 8 columns of 128x128 pixel frames.

        if not os.path.exists(cls.SPRITESHEET_PATH):
            print(f"Error: Master spritesheet not found at {cls.SPRITESHEET_PATH}")
            return

        full_sheet = QImage(cls.SPRITESHEET_PATH)
        if full_sheet.isNull():
            print(f"Error: Failed to load master spritesheet from {cls.SPRITESHEET_PATH}")
            return

        full_sheet = full_sheet.convertToFormat(QImage.Format_ARGB32)

        # Cleanup White background and anti-aliased whites.
        for y in range(full_sheet.height()):
            for x in range(full_sheet.width()):
                c = full_sheet.pixelColor(x, y)
                if c.red() > 240 and c.green() > 240 and c.blue() > 240:
                    full_sheet.setPixelColor(x, y, QColor(0, 0, 0, 0))

        size = Config.SPRITE_BASE_SIZE # 128
        states = ['IDLE', 'WALK', 'RUN', 'JUMP', 'CRAWL', 'SWING']
        
        for idx, state in enumerate(states):
            cls._sprites[state] = cls._slice_sheet(full_sheet, idx, 8, size)

    @classmethod
    def _slice_sheet(cls, sheet, row, num_frames, size):
        frames = []
        for i in range(num_frames):
            rect = QRect(i * size, row * size, size, size)
            frame_img = sheet.copy(rect)
            # Center the sprite in the RENDER_SIZE frame.
            scaled = frame_img.scaled(Config.RENDER_SIZE, Config.RENDER_SIZE, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            frames.append(QPixmap.fromImage(scaled))
        return frames
