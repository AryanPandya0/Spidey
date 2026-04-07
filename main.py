import sys
from PyQt5.QtWidgets import QApplication
from app import SpideyApp
from game_loop import GameLoop
from config import Config

def main():
    # Initialize Config
    Config.initialize()
    
    # Initialize App
    app = QApplication(sys.argv)
    
    # Initialize Main System
    spidey_app = SpideyApp()
    
    # Initialize Game Loop
    game_loop = GameLoop(spidey_app)
    
    # Run
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
