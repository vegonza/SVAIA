from datetime import datetime, timezone
import logging
import os
from hashlib import sha256
import logging
import functools
from typing import Callable, Any, Optional
from typeguard import typechecked

from colorama import Fore, Style, init

init(autoreset=True)


class ColoredFormatter(logging.Formatter):
    """Colored log formatter."""

    def __init__(self, *args, **kwargs):
        logging.Formatter.__init__(self, *args, **kwargs)

    @typechecked
    def format(self, record: logging.LogRecord) -> str:
        """Format the record with colors."""
        color = ""
        if record.levelno >= logging.ERROR:
            color = Fore.RED
        elif record.levelno >= logging.WARNING:
            color = Fore.YELLOW
        elif record.levelno >= logging.INFO:
            color = Fore.GREEN
        elif record.levelno >= logging.DEBUG:
            color = Fore.CYAN
        else:
            color = Fore.WHITE

        record.levelname = color + record.levelname + Style.RESET_ALL
        return logging.Formatter.format(self, record)


class SecureLogManager:
    @typechecked
    def __init__(self, log_file: str) -> None:
        self.log_file = log_file
        self.logger = self._setup_logger(log_file.split(".")[0], log_file)
        self._init_log_file()

    @typechecked
    def _setup_logger(self, logger_name: str, log_file: str, level: int = logging.DEBUG) -> logging.Logger:
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
        streamHandler.setLevel(level)
        streamHandler.setFormatter(colored_formatter)

        logger.setLevel(level)
        logger.addHandler(fileHandler)
        logger.addHandler(streamHandler)

        return logger

    @typechecked
    def _init_log_file(self) -> None:
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

    @typechecked
    def _get_timestamp(self) -> str:
        """
        Returns the current time in a readable format
        """
        # Get the current time in UTC
        timestamp = datetime.now(timezone.utc)

        # Formatear la hora en UTC con la zona horaria
        timestamp = timestamp.strftime("%Y-%m-%d %H:%M:%S %Z")
        return timestamp

    @typechecked
    def _hash_string(self, string: str) -> str:
        """
        Returns the hash of a string
        """
        return sha256(string.encode()).hexdigest()

    @typechecked
    def _file_exists(self, file_path: str) -> bool:
        """
        Returns True if the file exists, False otherwise
        """
        return os.path.exists(file_path)

    @typechecked
    def _file_empty(self, file_path: str) -> bool:
        """
        Returns True if the file is empty, False otherwise
        """
        return os.path.getsize(file_path) == 0

    @typechecked
    def _get_hash_from_line(self, line: str) -> str:
        """
        Returns the hash of a line
        """
        return line.split("|")[2].split(":")[0].strip("' ")

    @typechecked
    def _get_last_hash(self, log_file: str) -> Optional[str]:
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

    @typechecked
    def _get_log_string_from_line(self, line: str) -> str:
        """
        Returns the log string from a line
        """
        return line.split("|")[2].split(":")[-1].strip()

    @typechecked
    def add_log(self, log_level: str, log_string: str, user: str, function: str = "", argument: str = "") -> None:
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

    @typechecked
    def verify_hash_chain(self) -> bool:
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
    @typechecked
    def __init__(self, log_manager: SecureLogManager) -> None:
        self.log_manager = log_manager

    @typechecked
    def __call__(self, user: str, log_level: str) -> Callable:
        @typechecked
        def decorator(func: Callable) -> Callable:
            @functools.wraps(func)
            @typechecked
            def wrapper(*args: Any, **kwargs: Any) -> Any:
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
