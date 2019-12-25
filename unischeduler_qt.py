from PyQt5 import QtWidgets, uic
import sys
import unischeduler
from pathlib import Path


# When we put everything in pyinstaller, the directory of data files is in sys._MEIPASS
try:
    BASE_PATH = Path(sys._MEIPASS)
except AttributeError:
    BASE_PATH = Path(__file__).parent
DATA_FOLDER = BASE_PATH / "data"


class GUI(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi(DATA_FOLDER / 'mainwindow.ui', self)

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
        with unischeduler.ErrorHandler(self.label.setText, unknown_error_handler=self.error_handler):
            calendar = unischeduler.main(self.input.toPlainText(), self.checkBox.isChecked())
            filename, _ = QtWidgets.QFileDialog.getSaveFileName(caption="Select file to export schedule to", filter="Icalendar files (*.ics)")
            if filename:
                filename += "" if filename.lower().endswith(".ics") else ".ics"
                with open(filename, "wb") as f:
                    print(calendar.decode("UTF-8"))
                    f.write(calendar)

    def error_handler(self, exception: str):
        qm = QtWidgets.QMessageBox
        ret = qm.question(self, 'Error handler', "Unknown error encountered. Would you like to save it to some file so that the developer can fix it later for you? He is usually very quick to fix stuff!", qm.Yes | qm.No)

        if ret == qm.Yes:
            filename, _ = QtWidgets.QFileDialog.getSaveFileName(caption="Select file to save error to")
            if filename:
                with open(filename, "w") as f:
                    f.write(exception)
            self.label.setText('Send the error file to my developer, please')
        else:
            self.label.setText('Finished with an error')


app = QtWidgets.QApplication(sys.argv)
window = GUI()
app.exec_()
