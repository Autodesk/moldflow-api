# SPDX-FileCopyrightText: 2025 Autodesk, Inc.
# SPDX-License-Identifier: Apache-2.0

"""
Logging module for Moldflow.
"""

import logging
from .i18n import get_text
from .common import LogMessage
from .constants import DEFAULT_LOG_FILE

_IS_LOGGING = True

CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "simple": {
            "format": "[%(levelname)-8s - %(asctime)s] - %(name)s:  %(message)s",
            "datefmt": "%H:%M:%S",
        }
    },
}


class SafeStreamHandler(logging.StreamHandler):
    """Stream handler that falls back to backslash-escaping on encoding errors.

    This prevents UnicodeEncodeError when writing to non-UTF-8 terminals by
    re-encoding the message using the stream's encoding with errors="backslashreplace".
    """

    def emit(self, record):  # type: ignore[override]
        try:
            msg = self.format(record)
            stream = self.stream
            stream.write(f"{msg}{self.terminator}")
            self.flush()
        except UnicodeEncodeError:
            try:
                stream = self.stream
                encoding = getattr(stream, "encoding", None) or "utf-8"
                msg = self.format(record)
                safe_text = msg.encode(encoding, errors="backslashreplace").decode(
                    encoding, errors="ignore"
                )
                stream.write(f"{safe_text}{self.terminator}")
                self.flush()
            except Exception:  # pragma: no cover - delegate to logging error handler
                self.handleError(record)
        except Exception:  # pragma: no cover - delegate to logging error handler
            self.handleError(record)


def set_is_logging(is_logging: bool):
    """
    Enables or Disables moldflow API logging system
    Args:
        is_logging (bool): If true, enable logging, If false, disable logging
    """
    global _IS_LOGGING
    _IS_LOGGING = is_logging


def configure_file_logging(
    command_line_logs: bool, log_file: bool, log_file_name: str = DEFAULT_LOG_FILE
):
    """
    Configures logging for the moldflow API.
    If log_file is True, sets up a file handler for the moldflow logger.
    If the root logger has no handlers, sets up a simple stream handler with the CONFIG formatter.

    Args:
        command_line_logs (bool): If true, enable command line logging.
        log_file (bool): If true, enable file logging.
        log_file_name (str): The name of the log file. Defaults to DEFAULT_LOG_FILE.
    """
    root_logger = logging.getLogger()
    # Set logging state based on the parameters
    if command_line_logs or log_file or root_logger.handlers:
        set_is_logging(True)
    else:
        set_is_logging(False)
        return

    moldflow_logger = logging.getLogger("moldflow")
    moldflow_logger.propagate = False

    # Set up commandline logging if requested
    if command_line_logs:
        handler = SafeStreamHandler()
        formatter = logging.Formatter(
            CONFIG["formatters"]["simple"]["format"], CONFIG["formatters"]["simple"]["datefmt"]
        )
        handler.setFormatter(formatter)
        moldflow_logger.addHandler(handler)

    # If log_file is True, set up a file handler
    if log_file:
        save_file = log_file_name if log_file_name.endswith(".log") else f"{log_file_name}.log"
        file_handler = logging.FileHandler(
            save_file, mode="w", encoding="utf-8", errors="backslashreplace"
        )

        # Use the formatter from the first root handler if available, else fallback to CONFIG
        if command_line_logs:
            formatter = moldflow_logger.handlers[0].formatter
        else:
            formatter = logging.Formatter(
                CONFIG["formatters"]["simple"]["format"], CONFIG["formatters"]["simple"]["datefmt"]
            )
        file_handler.setFormatter(formatter)
        moldflow_logger.addHandler(file_handler)

    moldflow_logger.setLevel(root_logger.getEffectiveLevel())


def get_logger(name) -> logging.Logger | None:
    """
    Retrieve or create a logger with the specified name.
    Returns a configured logger instance or None if logging is disabled.

    Args:
        name: The name of the logger.

    Returns:
        logging.Logger: The logger instance.
    """
    if _IS_LOGGING:
        moldflow_logger = logging.getLogger("moldflow")
        logger = moldflow_logger.getChild(name)
        return logger
    return None


def process_log(logger_name: str, message_log: LogMessage | str, dump=None, **kwargs):
    """
    Processes a log entry with the message_log.

    Args:
        logger_name (str): The name of the logger.
        message_log (LogMessage | str): The message to log.
        dump: The dictionary of arguments to dump. Defaults to None.
        **kwargs: The keyword arguments to format the message.
    """
    if _IS_LOGGING:
        logger = get_logger(logger_name)
        _ = get_text()

        message = message_log
        level = logging.INFO

        # If message is LogMessage (intended)
        if isinstance(message_log, LogMessage):
            level = message_log.value[1]
            message = _(message_log.value[0]).format(**kwargs)
        logger.log(level, message)

        # If running on debug, dump all function args
        if logger.level <= logging.DEBUG and dump is not None:
            for n in dump.items():
                logger.debug(f'{n[0]}:{n[1]}')
