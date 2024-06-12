import logging

class Logger:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Logger, cls).__new__(cls)
            cls._instance.logger = logging.getLogger("application_logger")
            cls._instance.logger.setLevel(logging.INFO)
            
            # Clear any existing handlers to prevent duplicate logging
            if not cls._instance.logger.handlers:
                handler = logging.StreamHandler()
                formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
                handler.setFormatter(formatter)
                cls._instance.logger.addHandler(handler)
        return cls._instance

    def get_logger(self):
        return self.logger

# Provide a convenient function to get the singleton logger
def get_logger():
    return Logger().get_logger()