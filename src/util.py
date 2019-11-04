from pathlib import Path
import sys
from traceback import print_exception
import datetime as dt
from typing import List

# When we put everything in pyinstaller, the directory of data files is in sys._MEIPASS
try:
    BASE_PATH = Path(sys._MEIPASS)
except:
    BASE_PATH = Path(__file__).parent
DATA_FOLDER = BASE_PATH / "data"


class SchedulerError(Exception):
    pass


class ErrorHandler:
    def __init__(self, handler_method):
        self.handler_method = handler_method
    
    def __enter__(self):
        pass
   
    def __exit__(self, type, value, traceback):
        if traceback is None:
            self.handler_method("Finished successfully!")
        else:
            log_path = Path(__file__).parent / "log.txt"
            with open(log_path, 'a') as f:
                print_exception(type, value, traceback)
                print_exception(type, value, traceback, file=f)
            if isinstance(value, SchedulerError):
                self.handler_method(str(value))
            else:
                print(type, value)
                self.handler_method('UNKNOWN ERROR OCCURRED. CHECK LOG FILE')
        return True  # Suppresses exceptions for some magical reason