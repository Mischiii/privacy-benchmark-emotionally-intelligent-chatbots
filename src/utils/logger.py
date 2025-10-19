import logging
import sys
from colorlog import ColoredFormatter

class ExitOnErrorHandler(logging.Handler):
    def emit(self, record):
        if record.levelno >= logging.ERROR:
            sys.exit(1)

class Logger:
    def __init__(self, name: str, log_to_file: bool = False, log_file: str = '../app.log', level: int = logging.INFO):
        """
        Initializing Logger.

        :arg name (str): Name of the Logger.
        :arg log_to_file (bool): Whether to log messages to a file. Default is False.
        :arg log_file (str): File path for logging. Default is '../app.log'.
        :arg level (int): Logging level (e.g., logging.DEBUG, logging.INFO). Default is logging.INFO.
        """

        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)

        # Create a colored formatter for console logs
        colored_formatter = ColoredFormatter(
            "%(log_color)s%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
            log_colors={
                'DEBUG': 'cyan',
                'INFO': 'green',
                'WARNING': 'yellow',
                'ERROR': 'red',
                'CRITICAL': 'bold_red'
            }
        )

        # Console handler with colored output
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)
        console_handler.setFormatter(colored_formatter)
        self.logger.addHandler(console_handler)

        # Optional file handler for plain logs
        if log_to_file:
            file_formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S"
            )
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(level)
            file_handler.setFormatter(file_formatter)
            self.logger.addHandler(file_handler)

    def get_logger(self):
        """Return the configured logger."""
        return self.logger

logger_instance = Logger(name="Benchmark Emotionally Intelligent Chatbots", log_to_file=False, log_file="../app.log", level=logging.INFO)
logger = logger_instance.get_logger()
exit_handler = ExitOnErrorHandler()
logger.addHandler(exit_handler)