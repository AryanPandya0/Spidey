import os
from config import Config

try:
    import win32gui
    import win32process
except ImportError:
    win32gui = None
    win32process = None

class WindowHelper:
    def __init__(self):
        self.window_rects = []
        self.last_scan_time = 0
        self.scan_interval = 500 # ms
        self.my_pid = os.getpid()

    def update(self, current_time_ms):
        if win32gui is None or win32process is None:
            self.window_rects = []
            return

        if current_time_ms - self.last_scan_time > self.scan_interval:
            self.last_scan_time = current_time_ms
            self._scan_windows()

    def _scan_windows(self):
        self.window_rects = []
        
        def callback(hwnd, extra):
            if not win32gui.IsWindowVisible(hwnd):
                return
            
            # Skip minimized windows
            if win32gui.IsIconic(hwnd):
                return

            # Skip self
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            if pid == self.my_pid:
                return

            title = win32gui.GetWindowText(hwnd)
            if not title:
                return

            # Skip common system windows that aren't "ground"
            if title in ["Program Manager", "Settings", "Microsoft Text Input Application"]:
                return

            rect = win32gui.GetWindowRect(hwnd)
            # rect is (left, top, right, bottom)
            w = rect[2] - rect[0]
            h = rect[3] - rect[1]
            
            # Simple heuristic: window must have some size and be within screen bounds
            if w > 100 and h > 50:
                self.window_rects.append({
                    'left': rect[0],
                    'top': rect[1],
                    'right': rect[2],
                    'bottom': rect[3],
                    'title': title
                })

        win32gui.EnumWindows(callback, None)

    def get_window_at(self, x, y):
        """Returns the top-most window under the given point (if any)."""
        for rect in self.window_rects:
            if rect['left'] <= x <= rect['right'] and rect['top'] <= y <= rect['bottom']:
                return rect
        return None

    def get_ground_y(self, x, current_y, render_size):
        """Finds the highest ground (floor or window top) below the character."""
        screen_rect = Config.get_screen_available_rect(
            x + (render_size / 2),
            current_y + (render_size / 2),
        )
        floor_y = screen_rect.bottom() - render_size
        best_y = floor_y
        
        char_center_x = x + render_size // 2
        
        for rect in self.window_rects:
            # We are looking for the top edge of a window
            # Conditions: 
            # 1. Character's x is within window's horizontal bounds
            # 2. Window's top is below character's current bottom (approx)
            if rect['left'] <= char_center_x <= rect['right']:
                window_top = rect['top'] - render_size
                if window_top >= current_y - 5 and window_top < best_y:
                    best_y = window_top
                    
        return best_y
