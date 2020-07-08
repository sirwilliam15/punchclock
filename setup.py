from PySide2.QtWidgets import QWizard, QWizardPage, QApplication, QVBoxLayout, QRadioButton, QLabel, QLineEdit, QHBoxLayout
from PySide2.QtCore import Qt, QSize, QIcon
from PySide2.QtSvg import QSvgRenderer
from PySide2.QtGui import QPixmap, QMovie, QFont
import os
from sys import platform
import timeclock
import urllib

class SetupWizard(QWidget):
    def __init__(self, parent=None):
        super(SetupWizard, self).__init__(parent)
        self.addPage()

class ServiceSelect(QWizardPage):
    def __init__(self, parent=None):
        super(ServiceSelect, self).__init__(parent) 

        self.title = QLabel('Please select a service to store your timecards') 
        self.title.setAlignment(Qt.AlignCenter)
        
        self.s1 = QRadioButton('SquareUp Payroll')
        self.s2 = QRadioButton('MySQL or PostreSQL Server')
        self.s2 = QRadioButton('Store Timecards Locally')

        layout = QVBoxLayout()
        layout.addWidget(self.title)
        layout.addWidget(self.s1)
        layout.addWidget(self.s2)
        layout.addWidget(self.s3)
        self.setLayout(layout)

class SquareSetup(QWizardPage):
    def __init__(self, parent=None):
        super(SquareSetup, self).__init__(parent)
        self.url =  'https://xms-production-f.squarecdn.com/xms/assets/logos/square-22d4f700b4c53e104f17cab67cc34b9c27f99f2ea877069c6b2773d821a30004.svg'
        self.img = urllib.urlopen(self.url)

        self.title = QLabel('Square Payroll Setup')
        self.title_img = QIcon(self.img).pixmap(QSize(10))
        self.key_title = QLabel('API Key')
        self.api_key = QLineEdit()

        layout = QVBoxLayout()
        layout.addWidget(self.title)
        layout.addWidget(self.title_img)
        
        layout2 = QHBoxLayout()
        layout2.addWidget(self.key_title)
        layout2.addwidget(self.api_key)
        layout.addLayout(layout2)
        self.setLayout(layout)


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