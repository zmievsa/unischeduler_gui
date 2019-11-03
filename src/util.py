import os

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
            log_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "log.txt")
            with open(log_path, 'a') as f:
                f.write(str(value))
                f.write(str(traceback))
            if isinstance(type, SchedulerError):
                self.handler_method(str(value))
            else:
                self.handler_method('UNKNOWN ERROR OCCURRED. CHECK LOG FILE')