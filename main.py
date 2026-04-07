import sys
from PyQt5.QtWidgets import QApplication
from app import SpideyApp
from game_loop import GameLoop
from config import Config

def main():
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(True)
    Config.initialize(app)
    
    spidey_app = SpideyApp()
    game_loop = GameLoop(spidey_app)
    spidey_app.game_loop = game_loop
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
