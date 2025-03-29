# custom_logging/logger.py
from .interfaces import ILogger
from .debug_logger import DebugLogger

class Logger:
    _instance = None
    _logger_impl: ILogger = None

    def __new__(cls):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    def initialize(cls, implementation: ILogger = None) -> None:
        if cls._logger_impl is not None:
            raise Exception("Logger уже инициализирован!")
        if implementation is None:
            cls._logger_impl = DebugLogger()
        else:
            cls._logger_impl = implementation

    def debug(self, message: str) -> None:
        if not self._logger_impl:
            raise Exception("Logger не инициализирован!")
        self._logger_impl.debug(message)

    def info(self, message: str) -> None:
        if not self._logger_impl:
            raise Exception("Logger не инициализирован!")
        self._logger_impl.info(message)

    def warning(self, message: str) -> None:
        if not self._logger_impl:
            raise Exception("Logger не инициализирован!")
        self._logger_impl.warning(message)

    def error(self, message: str) -> None:
        if not self._logger_impl:
            raise Exception("Logger не инициализирован!")
        self._logger_impl.error(message)

    def critical(self, message: str) -> None:
        if not self._logger_impl:
            raise Exception("Logger не инициализирован!")
        self._logger_impl.critical(message)