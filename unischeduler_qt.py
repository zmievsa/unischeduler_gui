from PyQt5 import QtWidgets, uic
import sys
import unischeduler
from unischeduler.errors import ErrorHandler
from pathlib import Path


# When we put everything in pyinstaller, the directory of data files is in sys._MEIPASS
try:
    BASE_PATH = Path(sys._MEIPASS)
except:
    BASE_PATH = Path(__file__).parent
DATA_FOLDER = BASE_PATH / "data"


class GUI(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi(DATA_FOLDER / 'qtgui.ui', self)

        self.setWindowTitle("Scheduler")
        self.setMaximumWidth(self.width())
        self.setMaximumHeight(self.height())
        self.setMinimumWidth(self.width())
        self.setMinimumHeight(self.height())

        self.label = self.findChild(QtWidgets.QLabel, 'label')
        self.label.setText("Please, paste your schedule in the field below")
        
        self.input = self.findChild(QtWidgets.QPlainTextEdit, 'plainTextEdit')
        self.button = self.findChild(QtWidgets.QPushButton, 'pushButton')
        self.button.hide()
        self.button.show()
        self.button.clicked.connect(self.create_schedule)

        self.checkBox: QtWidgets.QCheckBox = self.findChild(QtWidgets.QCheckBox, 'checkBox')

        self.show()
    
    def create_schedule(self):
        self.label.setText('Starting...')
        with ErrorHandler(self.label.setText):
            calendar = unischeduler.main(self.input.toPlainText(), self.checkBox.isChecked())
            filename, _ = QtWidgets.QFileDialog.getSaveFileName(caption="Select file to export schedule to", filter="Icalendar files (*.ics)")
            if filename:
                filename += "" if filename.lower().endswith(".ics") else ".ics"
                with open(filename, "wb") as f:
                    print(calendar.decode("UTF-8"))
                    f.write(calendar)



app = QtWidgets.QApplication(sys.argv)
window = GUI()
app.exec_()