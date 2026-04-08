import os
from PyQt5.QtGui import QImage, QColor, QPixmap, QPainter
from PyQt5.QtCore import Qt, QRect
from config import Config

class Assets:
    _sprites = {}
    ASSETS_DIR = "assets"

    @classmethod
    def get_sprites(cls, state):
        if not cls._sprites:
            cls.generate_all()
        return cls._sprites.get(state, [])

    @classmethod
    def generate_all(cls):
        cls._sprites = {}
        mapping = {
            'WALK': 'walk.png',
            'JUMP': 'jump.png',
            'WEBSHOOT': 'webshoot.png',
            'SWING': 'swing.png'
        }

        for state, filename in mapping.items():
            path = os.path.join(cls.ASSETS_DIR, filename)
            if not os.path.exists(path): continue
            img = QImage(path)
            if img.isNull(): continue

            img = img.convertToFormat(QImage.Format_ARGB32)
            
            # Step 1: Auto-clear background
            cls._sample_and_clear_bg(img)
            
            # Assuming 8 frames for now as a default
            num_frames = 8
            cls._sprites[state] = cls._extract_perfect_frames(img, num_frames, anchor="bottom" if state != "SWING" else "center")

        # Fallbacks
        if 'WALK' in cls._sprites:
            cls._sprites['IDLE'] = [cls._sprites['WALK'][0]]
            cls._sprites['RUN'] = cls._sprites['WALK']

    @classmethod
    def _sample_and_clear_bg(cls, img):
        # Sample all four edges to find the dominant background color
        edge_pixels = []
        for x in range(0, img.width(), 10):
            edge_pixels.append(img.pixelColor(x, 0))
            edge_pixels.append(img.pixelColor(x, img.height()-1))
        for y in range(0, img.height(), 10):
            edge_pixels.append(img.pixelColor(0, y))
            edge_pixels.append(img.pixelColor(img.width()-1, y))
        
        # Find the most frequent color
        from collections import Counter
        color_counts = Counter([(c.red(), c.green(), c.blue()) for c in edge_pixels])
        if not color_counts: return
        bg_rgb, count = color_counts.most_common(1)[0]
        
        # Increase tolerance significantly (35) to handle JPEG noise in the "blue" box
        r_bg, g_bg, b_bg = bg_rgb
        for y in range(img.height()):
            for x in range(img.width()):
                c = img.pixelColor(x, y)
                if abs(c.red() - r_bg) < 35 and abs(c.green() - g_bg) < 35 and abs(c.blue() - b_bg) < 35:
                    img.setPixelColor(x, y, QColor(0, 0, 0, 0))

    @classmethod
    def _extract_perfect_frames(cls, img, num_frames, anchor="bottom"):
        w_raw = img.width() // num_frames
        h_raw = img.height()
        
        raw_frames = []
        bboxes = []
        max_w, max_h = 0, 0
        
        # Step 2: Slice and Find Tight Bounding Boxes
        for i in range(num_frames):
            frame = img.copy(i * w_raw, 0, w_raw, h_raw)
            
            # Find tight bbox
            min_x, min_y = w_raw, h_raw
            max_x_f, max_y_f = 0, 0
            has_px = False
            for y in range(h_raw):
                for x in range(w_raw):
                    if frame.pixelColor(x, y).alpha() > 15:
                        has_px = True
                        min_x, min_y = min(min_x, x), min(min_y, y)
                        max_x_f, max_y_f = max(max_x_f, x), max(max_y_f, y)
            
            if has_px:
                bw, bh = max_x_f - min_x + 1, max_y_f - min_y + 1
                bboxes.append((min_x, min_y, bw, bh))
                max_w, max_h = max(max_w, bw), max(max_h, bh)
                raw_frames.append(frame.copy(min_x, min_y, bw, bh))
            else:
                raw_frames.append(None)
                bboxes.append(None)
        
        if max_w == 0 or max_h == 0: return []

        # Step 3: Re-canvas everyone to (max_w, max_h) using anchoring
        standardized_frames = []
        target_h = int(max_h * Config.SCALE_FACTOR)
        target_w = int(max_w * Config.SCALE_FACTOR)

        for frame in raw_frames:
            canvas = QImage(max_w, max_h, QImage.Format_ARGB32)
            canvas.fill(QColor(0, 0, 0, 0))
            
            if frame is not None:
                painter = QPainter(canvas)
                # Alignment logic
                dest_x = (max_w - frame.width()) // 2
                if anchor == "bottom":
                    dest_y = max_h - frame.height()
                else: # center
                    dest_y = (max_h - frame.height()) // 2
                    
                painter.drawImage(dest_x, dest_y, frame)
                painter.end()
            
            # Scale to Final Render Size
            scaled = QPixmap.fromImage(canvas.scaled(target_w, target_h, Qt.KeepAspectRatio, Qt.FastTransformation))
            standardized_frames.append(scaled)
            
        return standardized_frames
