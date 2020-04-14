from PySide2.QtWidgets import QWidget, QApplication #, QHBoxLayout, QVBoxLayout, QPushButton, QLabel, QLineEdit
from PySide2.QtCore import #Qt, QSize
from PySide2.QtGui import #QPixmap, QMovie, QFont
import os
from sys import platform
import timeclock

class SetupWizard(QWidget):
    def __init__(self):
        super().__init__()

        self.text = 'Welcome to the Setup Wizard!'
        self.config = {}

        



def main(): 
    if platform == 'linux':
        config_path = '~/.config/punchclock/'
    else:
        config_path = os.getenv('APPDATA')
        # config_path = APPDATA/punchclock/

    if os.path.exists(config_path):
        timeclock.main(config_path)
    else:
        app = QApplication([])
        window = SetupWizard()
        #window.resize(400, 600)
        window.show()
        app.exec_()

if __name__ == "__main__":
    main()