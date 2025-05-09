from datetime import datetime, timezone
import logging
import os
from hashlib import sha256
import logging
import functools

class ColoredFormatter(logging.Formatter):
    COLORS = {
        logging.DEBUG: "\033[34m",     # blue
        logging.INFO: "\033[32m",      # green
        logging.WARNING: "\033[33m",   # yellow
        logging.ERROR: "\033[31m",     # red
    }

    RESET = "\033[0m"

    def format(self, record):
        color = self.COLORS.get(record.levelno, self.RESET)
        # Format the message using the parent formatter
        message = super().format(record)
        # Apply color to each line of the message
        colored_lines = [f"{color}{line}{self.RESET}" for line in message.splitlines()]
        return "\n".join(colored_lines)

class SecureLogManager:
    def __init__(self, log_file: str):
        self.log_file = log_file
        self.logger = self._setup_logger(log_file.split(".")[0], log_file)
        self._init_log_file()

    def _setup_logger(self, logger_name, log_file, level=logging.INFO) -> logging.Logger:
        logger = logging.getLogger(logger_name)
        log_formatter = logging.Formatter(
            fmt="%(timestamp)s: %(levelname)-8s | %(user)s | '%(hash)s': Llamada a la función %(function)s con parámetros: %(argument)s -> Resultado: %(log_string)s |",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        colored_formatter = ColoredFormatter(
            fmt="%(timestamp)s: %(levelname)-8s | %(user)s | '%(hash)s': Llamada a la función %(function)s con parámetros: %(argument)s -> Resultado: %(log_string)s |",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        fileHandler = logging.FileHandler(log_file, mode='a')
        fileHandler.setFormatter(log_formatter)
        streamHandler = logging.StreamHandler()
        streamHandler.setFormatter(colored_formatter)

        logger.setLevel(level)
        logger.addHandler(fileHandler)
        logger.addHandler(streamHandler)

        return logger

    def _init_log_file(self):
        """
        Initializes the log file
        """
        if not self._file_exists(self.log_file) or (self._file_exists(self.log_file) and self._file_empty(self.log_file)):
            self.add_log(
                log_level="info",
                log_string=f"Inicialización del log en el tiempo {self._get_timestamp()} UTC",
                user="system",
                function="init_log_file",
                argument=""
            )

    def _get_timestamp(self):
        """
        Returns the current time in a readable format
        """
        # Get the current time in UTC
        timestamp = datetime.now(timezone.utc)

        # Formatear la hora en UTC con la zona horaria
        timestamp = timestamp.strftime("%Y-%m-%d %H:%M:%S %Z")
        return timestamp

    def _hash_string(self, string: str) -> str:
        """
        Returns the hash of a string
        """
        return sha256(string.encode()).hexdigest()

    def _file_exists(self, file_path):
        """
        Returns True if the file exists, False otherwise
        """
        return os.path.exists(file_path)

    def _file_empty(self, file_path):
        """
        Returns True if the file is empty, False otherwise
        """
        return os.path.getsize(file_path) == 0

    def _get_hash_from_line(self, line: str) -> str:
        """
        Returns the hash of a line
        """
        return line.split("|")[2].split(":")[0].strip("' ")

    def _get_last_hash(self, log_file) -> str | None:
        """
        Reads the last line of the log file and extracts the data after the date and log type.

        Parameters:
            log_file (str): Log file path.

        Returns:
            str: The extracted data, or None if the file does not exist or is empty.
        """
        if not self._file_exists(log_file) or self._file_empty(log_file):
            return None
        with open(log_file, 'r') as file:
            return self._get_hash_from_line(file.readlines()[-1])

    def _get_log_string_from_line(self, line: str) -> str:
        """
        Returns the log string from a line
        """
        return line.split("|")[2].split(":")[-1].strip()

    def add_log(self, log_level: str, log_string: str, user: str, function: str = "", argument: str = ""):
        """
        Adds a log to the log file

        Parameters:
            log_level (str): Log level.
            log_string (str): Log string.
            user (str): User.
            function (str): Function.
            argument (str): Arguments.
        """
        log_levels = {
            "warning": self.logger.warning,
            "error": self.logger.error,
            "debug": self.logger.debug,
            "info": self.logger.info
        }

        # Calculate the chained hash and create the string to introduce in the log
        last_hash = self._get_last_hash(self.log_file)
        if last_hash is None:
            last_hash = ""
        new_hash = self._hash_string(last_hash + log_string)

        # Call the log function corresponding to the log level
        log_levels[log_level](log_string, extra={
            'timestamp': self._get_timestamp(),
            'user': user,
            'hash': new_hash,
            'log_string': log_string,
            'function': function,
            'argument': argument
        })

    def verify_hash_chain(self):
        """
        Verify that the hash chain in the log file is correct.

        Returns:
            bool: True if the hash chain is correct, False if there is an error.
        """
        with open(self.log_file, 'r') as file:
            previous_hash = self._get_hash_from_line(file.readline())
            for line in file:
                log_string = self._get_log_string_from_line(line)
                if self._hash_string(previous_hash + log_string) != self._get_hash_from_line(line):
                    return False
                previous_hash = self._get_hash_from_line(line)
        return True


class FunctionMonitor:
    def __init__(self, log_manager: SecureLogManager):
        self.log_manager = log_manager

    def __call__(self, user: str, log_level: str):
        def decorator(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                func_name = func.__name__
                args_str = ", ".join([repr(arg) for arg in args])
                kwargs_str = ", ".join([f"{k}={repr(v)}" for k, v in kwargs.items()])
                all_args = f"{args_str}{', ' if args_str and kwargs_str else ''}{kwargs_str}"

                result = func(*args, **kwargs)

                log_string = repr(result)
                self.log_manager.add_log(
                    log_level=log_level,
                    log_string=log_string,
                    user=user,
                    function=func_name,
                    argument=all_args
                )

                return result
            return wrapper
        return decorator
