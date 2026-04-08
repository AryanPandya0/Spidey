import os
from PyQt5.QtGui import QImage, QColor, QPixmap
from PyQt5.QtCore import Qt, QRect
from config import Config

class Assets:
    _sprites = {}
    SPRITESHEET_PATH = os.path.join("assets", "spidey spreadsheet.jpg")

    @classmethod
    def get_sprites(cls, state):
        if not cls._sprites:
            cls.generate_all()
        return cls._sprites.get(state, [])

    @classmethod
    def generate_all(cls):
        if not os.path.exists(cls.SPRITESHEET_PATH):
            print(f"Error: Classic spreadsheet not found at {cls.SPRITESHEET_PATH}")
            return

        full_sheet = QImage(cls.SPRITESHEET_PATH)
        if full_sheet.isNull():
            print(f"Error: Failed to load classic spreadsheet from {cls.SPRITESHEET_PATH}")
            return

        full_sheet = full_sheet.convertToFormat(QImage.Format_ARGB32)

        # JPEG Threshold Background Removal
        # This handles the "noisy" white pixels from JPEG compression
        for y in range(full_sheet.height()):
            for x in range(full_sheet.width()):
                c = full_sheet.pixelColor(x, y)
                if c.red() > 220 and c.green() > 220 and c.blue() > 220:
                    full_sheet.setPixelColor(x, y, QColor(0, 0, 0, 0))

        size = Config.SPRITE_BASE_SIZE # 64
        
        # Mapping for "spidey spreadsheet.jpg"
        # Based on visual analysis of the Sega Genesis sheet structure
        cls._sprites['WALK'] = cls._slice_sheet(full_sheet, row=0, num_frames=6, size=size)
        cls._sprites['RUN']  = cls._slice_sheet(full_sheet, row=1, num_frames=10, size=size)
        cls._sprites['JUMP'] = cls._slice_sheet(full_sheet, row=4, num_frames=7, size=size)
        cls._sprites['CRAWL'] = cls._slice_sheet(full_sheet, row=5, num_frames=4, start_col=8, size=size)
        cls._sprites['SWING'] = cls._slice_sheet(full_sheet, row=6, num_frames=5, start_col=4, size=size)
        cls._sprites['IDLE']  = cls._slice_sheet(full_sheet, row=7, num_frames=6, size=size)

    @classmethod
    def _slice_sheet(cls, sheet, row, num_frames, size, start_col=0):
        frames = []
        for i in range(num_frames):
            rect = QRect((start_col + i) * size, row * size, size, size)
            frame_img = sheet.copy(rect)
            # Scale up to RENDER_SIZE
            scaled = frame_img.scaled(Config.RENDER_SIZE, Config.RENDER_SIZE, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            frames.append(QPixmap.fromImage(scaled))
        return frames
