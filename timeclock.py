from square.client import Client as squareClient
from employeeAPI import Employee, ApiRequestError, apiKey
from datetime import datetime, timezone
from PySide2.QtWidgets import QApplication, QHBoxLayout, QVBoxLayout, QPushButton, QLabel, QWidget, QLineEdit
from PySide2.QtCore import Qt, QSize
from PySide2.QtGui import QPixmap, QMovie, QFont
import os, time, threading

logo = 'logo.png'

class InactiveEmployeeError(Exception):
    def __init__(self, message):
        super().__init__(message)

class EmployeeNotFoundError(Exception):
    def __init__(self, message):
        super().__init__(message)

Prompts_En = {
    'startup':'Hello!\nPlease enter your employee PIN number.',
    'button':'Punch!',
    'punch_in':'Success! Punched in at: ',
    'punch_out':'Success! Punched out at: ',
    'error':'Error: ',
    'translate':'Español',
    'not_found':'Employee not found',
    'inactive':'Employee Inactive'
}

Prompts_Es = {
    'startup':'Bienvenido!\nPor favor, escribe tu numero de empleado.',
    'button':'Punchear!',
    'punch_in':'Perfecto! Entró a las: ',
    'punch_out':'Perfecto! Salió a las: ',
    'error':'Error: ',
    'translate':'English',
    'not_found':'Empleado no encontrado',
    'inactive':'Empleado no activo'
}

def getEmployeeID(pin):
    _client = squareClient(access_token=apiKey, environment='production')
    _client = _client.team

    _employees = _client.search_team_members(body={})
    _employees = _employees.body['team_members']
    for e in _employees:
        try:
            if e['reference_id'] == str(pin):
                return e
        except KeyError:
            pass
    raise EmployeeNotFoundError('PIN: %s'%str(pin))


class Timeclock(QWidget):
    def __init__(self):
        super().__init__()
        # Set master settings
        self.setAutoFillBackground(True)
        _p = self.palette()
        _p.setColor(self.backgroundRole(), Qt.white)
        self.setPalette(_p)

        # Set Language
        self._span = False
        self._prompts = Prompts_En

        # Initialize widgets
        self.text = QLabel(self._prompts['startup'])
        self.button = QPushButton(self._prompts['button'])
        self.language = QPushButton(self._prompts['translate'])
        self.logo = QLabel()
        self.logo.setPixmap(QPixmap(os.getcwd()+'/%s'%logo))

        self.buttons = QHBoxLayout()
        self.employee = QVBoxLayout()
        self.pin = QLineEdit()

        # Set widget alignment
        self.logo.setAlignment(Qt.AlignCenter)
        self.text.setAlignment(Qt.AlignCenter)
        self.employee.setAlignment(Qt.AlignCenter)
        self.pin.setAlignment(Qt.AlignCenter)

        # Set Font Size
        self.text.setFont(QFont('Calibri', 14))
        
        # Create button layout
        self.buttons.addWidget(self.button)
        self.buttons.addWidget(self.language)

        # Create Name layout
        self.employee.addWidget(self.pin)

        # Set master layout
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.logo)
        self.layout.addWidget(self.text)
        self.layout.addLayout(self.employee)
        self.layout.addLayout(self.buttons)
        self.setLayout(self.layout)

        # Set Actions
        self.button.clicked.connect(self.submit)
        self.pin.returnPressed.connect(self.submit)
        self.language.clicked.connect(self.translate)
    
    def submit(self):
        _movie = QMovie(os.getcwd()+'/loading.gif')
        _movie.setScaledSize(QSize(50, 50))
        self.text.setMovie(_movie)
        _movie.start()

        t = threading.Thread(target=self.processEmployee)
        t.start()

    def processEmployee(self):
        try: 
            _pin = self.pin.text()
            self.pin.clear()

            _user = getEmployeeID(_pin)
            _id = _user['id']
            _loc = _user['assigned_locations']['location_ids'][0]
        except EmployeeNotFoundError: 
            self.text.setText('%s: %s'%(self._prompts['not_found'], _pin))
            return
        except InactiveEmployeeError: 
            self.text.setText('%s: %s'%(self._prompts['inactive'], _pin))
            return
        except Exception as e: 
            self.text.setText('%s%s'%(self._prompts['error'], e))
            return

        _user = Employee(_id, _loc)
        try:
            _time, _punch_in = _user.punch()
            if _punch_in: self.text.setText(self._prompts['punch_in'] + _time)
            else: self.text.setText(self._prompts['punch_out'] + _time)
            time.sleep(5)
            self.text.setText(self._prompts['startup'])
        except ApiRequestError as e: self.text.setText('Error: API Request Error: %s'%e)
        except Exception as e: self.text.setText('Error: %s'%e)


    def translate(self):
        if self._span:
            self._span = False
            self._prompts = Prompts_En
        else:
            self._span = True
            self._prompts = Prompts_Es
        self.text.setText(self._prompts['startup'])
        self.button.setText(self._prompts['button'])
        self.language.setText(self._prompts['translate'])


if __name__ == "__main__":
    
    app = QApplication([])
    window = Timeclock()
    #window.resize(400, 600)
    window.show()

    app.exec_()
