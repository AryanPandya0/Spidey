from PyQt5.QtWidgets import QMenu, QAction
from PyQt5.QtCore import Qt
from config import Config

class InteractionSystem:
    def __init__(self, behavior, app):
        self.behavior = behavior
        self.app = app # References the QWidget window
        self.dragging = False
        self.drag_offset = None

    def handle_mouse_press(self, event):
        if event.button() == Qt.LeftButton:
            if self._is_on_character(event.pos()):
                self.dragging = True
                self.drag_offset = event.pos()
                self.behavior.force_interact()
                self.behavior._change_state("DRAG")
        elif event.button() == Qt.RightButton:
            self.show_context_menu(event.globalPos())

    def handle_mouse_move(self, event):
        if self.dragging:
            delta = event.pos() - self.drag_offset
            new_pos = self.app.pos() + delta
            self.app.move(new_pos)
            
            # Sync physics position to window position
            self.app.physics.x = float(new_pos.x())
            self.app.physics.y = float(new_pos.y())
            self.app.physics.vx = 0
            self.app.physics.vy = 0

    def handle_mouse_release(self, event):
        if event.button() == Qt.LeftButton and self.dragging:
            self.dragging = False
            self.drag_offset = None
            self.behavior._change_state("IDLE")

    def _is_on_character(self, pos):
        # Character bounding box is RENDER_SIZE x RENDER_SIZE
        # Since the widget is synced to the character rect, pos is relative to (0,0) of the character
        cx, cy = 0, 0
        w, h = Config.RENDER_SIZE, Config.RENDER_SIZE
        # Add a bit of padding for easier grabbing
        padding = 10
        return cx - padding <= pos.x() <= cx + w + padding and cy - padding <= pos.y() <= cy + h + padding

    def show_context_menu(self, pos):
        menu = QMenu(self.app)
        menu.setStyleSheet("QMenu { background-color: #2b2b2b; color: white; border: 1px solid #555; } QMenu::item:selected { background-color: #444; }")
        
        # State transitions
        states_menu = menu.addMenu("Actions")
        for state in ["IDLE", "WALK", "RUN", "JUMP", "SWING", "WEBSHOOT"]:
            act = QAction(state, menu)
            act.triggered.connect(lambda checked, s=state: self.behavior._change_state(s))
            states_menu.addAction(act)
        
        menu.addSeparator()
        
        # Controls
        debug_act = QAction("Debug Mode", menu, checkable=True)
        debug_act.setChecked(Config.DEBUG_MODE)
        def toggle_debug(): Config.DEBUG_MODE = not Config.DEBUG_MODE
        debug_act.triggered.connect(toggle_debug)
        menu.addAction(debug_act)
        
        exit_act = QAction("Exit Spidey", menu)
        exit_act.triggered.connect(self.app.close)
        menu.addAction(exit_act)
        
        menu.exec_(pos)
