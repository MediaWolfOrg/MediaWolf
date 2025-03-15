import sys

from loguru import logger
from services.config_services import LOG_FILE_NAME


class CustomLogger:
    _instance = None

    def __new__(cls, log_file=LOG_FILE_NAME, log_level="DEBUG"):
        if cls._instance is None:
            cls._instance = super(CustomLogger, cls).__new__(cls)
            cls._instance.configure(log_file, log_level)
        return cls._instance

    def configure(self, log_file, log_level):
        logger.remove()
        logger.add(sys.stdout, format="{time} - {level} - {message}", level=log_level)
        logger.add(sys.stderr, format="{time} - {level} - {message}", level="ERROR")
        logger.add(
            log_file,
            format="{time} - {level} - {message}",
            level="DEBUG",
            rotation="10 MB",
            compression="zip",
        )
        self.logger = logger
        self.log_level = log_level

    def set_level(self, log_level):
        self.log_level = log_level
        logger.remove()
        self.configure(LOG_FILE_NAME, log_level)

    def info(self, message):
        self.logger.info(message)

    def error(self, message):
        self.logger.error(message)

    def debug(self, message):
        self.logger.debug(message)

    def warning(self, message):
        self.logger.warning(message)


CustomLogger()
