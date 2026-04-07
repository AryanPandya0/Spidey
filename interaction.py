from PyQt5.QtWidgets import QMenu, QAction
from PyQt5.QtCore import Qt
from config import Config

class InteractionSystem:
    def __init__(self, behavior, app):
        self.behavior = behavior
        self.app = app # References the QWidget window

    def handle_mouse_press(self, event):
        if event.button() == Qt.LeftButton:
            # Check if clicked on character
            if self._is_on_character(event.pos()):
                self.behavior.force_interact()
        elif event.button() == Qt.RightButton:
            self.show_context_menu(event.globalPos())

    def _is_on_character(self, pos):
        # Character bounding box
        global_pos = self.app.mapToGlobal(pos)
        cx, cy = self.app.physics.x, self.app.physics.y
        w, h = Config.RENDER_SIZE, Config.RENDER_SIZE
        return cx <= global_pos.x() <= cx + w and cy <= global_pos.y() <= cy + h

    def show_context_menu(self, pos):
        menu = QMenu(self.app)
        
        # Mode options
        idle_act = QAction("IDLE", menu)
        idle_act.triggered.connect(lambda: self.behavior._change_state("IDLE"))
        jump_act = QAction("JUMP", menu)
        jump_act.triggered.connect(lambda: self.behavior._change_state("JUMP"))
        swing_act = QAction("SWING", menu)
        swing_act.triggered.connect(lambda: self.behavior._change_state("SWING"))
        
        menu.addAction(idle_act)
        menu.addAction(jump_act)
        menu.addAction(swing_act)
        menu.addSeparator()
        
        # Controls
        debug_act = QAction("Debug Mode", menu, checkable=True)
        debug_act.setChecked(Config.DEBUG_MODE)
        def toggle_debug(): Config.DEBUG_MODE = not Config.DEBUG_MODE
        debug_act.triggered.connect(toggle_debug)
        menu.addAction(debug_act)
        
        exit_act = QAction("Exit", menu)
        exit_act.triggered.connect(self.app.close)
        menu.addAction(exit_act)
        
        menu.exec_(pos)
