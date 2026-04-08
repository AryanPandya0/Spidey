import json
import os
from PyQt5.QtCore import QPoint

class PersistenceManager:
    def __init__(self, file_path):
        self.file_path = file_path
        self.data = {}
        self.load()

    def load(self):
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, 'r') as f:
                    self.data = json.load(f)
            except Exception as e:
                print(f"Error loading persistence: {e}")
                self.data = {}
        else:
            self.data = {}

    def save(self):
        try:
            with open(self.file_path, 'w') as f:
                json.dump(self.data, f, indent=4)
        except Exception as e:
            print(f"Error saving persistence: {e}")

    def get(self, key, default=None):
        return self.data.get(key, default)

    def set(self, key, value):
        self.data[key] = value
        self.save()

    def get_pos(self):
        pos = self.get("position")
        if pos:
            return QPoint(pos['x'], pos['y'])
        return None

    def save_pos(self, x, y):
        self.set("position", {'x': int(x), 'y': int(y)})
