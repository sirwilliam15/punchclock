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
    'startup':'Hello!\nPlease enter your first and last name.',
    'button':'Punch!',
    'punch_in':'Success! Punched in at: ',
    'punch_out':'Success! Punched out at: ',
    'error':'Error: ',
    'translate':'Español',
    'not_found':'Employee not found',
    'inactive':'Employee Inactive'
}

Prompts_Es = {
    'startup':'Bienvenido!\nPor favor, escribe tu primer nombre y apellido abajo.',
    'button':'Punchear!',
    'punch_in':'Perfecto! Entró a las: ',
    'punch_out':'Perfecto! Salió a las: ',
    'error':'Error: ',
    'translate':'English',
    'not_found':'Empleado no encontrado',
    'inactive':'Empleado no activo'
}

# TODO: Cache Employee IDs and only update on startup of program
def getEmployeeID(fname, lname, location=None):
    _client = squareClient(access_token=apiKey, environment='production')
    _client = _client.employees
    if location == None: _employees = _client.list_employees().body['employees']
    else: _employees = _client.list_employees(location_id=location).body['employees']
     
    for e in _employees:
        if e['first_name'] == fname and e['last_name'] == lname:
            if e['status'] == 'ACTIVE': 
                location = e['location_ids']
                employeeID = e['id']
                return e
            else: raise InactiveEmployeeError('%s, %s'%(lname, fname))
    raise EmployeeNotFoundError(('%s, %s'%(lname, fname)))

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
        self.name = QVBoxLayout()
        self.fname = QLineEdit()
        self.lname = QLineEdit()

        # Set widget alignment
        self.logo.setAlignment(Qt.AlignCenter)
        self.text.setAlignment(Qt.AlignCenter)
        self.name.setAlignment(Qt.AlignCenter)
        self.fname.setAlignment(Qt.AlignCenter)
        self.lname.setAlignment(Qt.AlignCenter)

        # Set Font Size
        self.text.setFont(QFont('Calibri', 14))
        
        # Create button layout
        self.buttons.addWidget(self.button)
        self.buttons.addWidget(self.language)

        # Create Name layout
        self.name.addWidget(self.fname)
        self.name.addWidget(self.lname)

        # Set master layout
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.logo)
        self.layout.addWidget(self.text)
        self.layout.addLayout(self.name)
        self.layout.addLayout(self.buttons)
        self.setLayout(self.layout)

        # Set Actions
        self.button.clicked.connect(self.submit)
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
            _fname = self.fname.text()[0].upper() + self.fname.text()[1:]
            _lname = self.lname.text()[0].upper() + self.lname.text()[1:]
            _user = getEmployeeID(_fname, _lname)
            _id = _user['id']
            _loc = _user['location_ids'][0]
        except EmployeeNotFoundError: 
            self.text.setText('%s: %s, %s'%(self._prompts['not_found'], _lname, _fname))
            return
        except InactiveEmployeeError: 
            self.text.setText('%s: %s, %s'%(self._prompts['inactive'], _lname, _fname))
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
