"""
Logger.py
    Provides functions for printing logs to console and multiple files simultaneously.
"""
from time import ctime
from typing import List
import sys
from typing import TextIO
import os

logging: bool = True
log_to: List[TextIO] = [sys.stdout]


def close_log_files():
    """Closes all default log files in the list logging.log_to."""
    for file in log_to:
        if file == sys.stdout:
            continue
        file.close()


def add_log_files(*args: TextIO):
    """
    Add multiple opened file objects to the list of files which the logger logs to. When using tcpsockets.server or
    tcpsockets.client these list of files(logging.log_to) will be closed automatically.
    Args: args(TextIO):All the file objects where logs are written to.
    """
    global log_to
    log_to.extend(args)


def set_log_files(file_list: List[TextIO]):
    """
    Set the list of files which the logger logs to. When using tcpsockets.server or tcpsockets.client these list of
    files(logging.log_to) will be closed automatically.
    Args: file_list(List[TextIO]): list of all files the logger must log to
    """
    global log_to
    log_to.clear()
    log_to.extend(file_list)


def set_logging(logBool: bool):
    """Turn Logging on or off. Should only be called just after imports.
    Args:
        logBool(bool): Set logging to True or False
    """
    global logging
    logging = logBool

def log_print(*args, **kwargs):
    """ Prints the log with time in front. Same signature as that of print."""
    log_init = f"[{ctime()}] "
    print(log_init, *args, **kwargs)


def log(*args, files: List[TextIO] = None, **kwargs):
    """
    Write logs to console and multiple opened files simultaneously.
    Args:
        files(List[TextIO]): A list of opened file objects to log to. Overrides file keyword argument for print.
        args: same as print.
        kwargs: same as print.
    """
    if not logging:
        return
    if "file" in kwargs:
        if files is None:
            files = [kwargs["file"]]
        else:
            del kwargs["file"]
    else:
        if files is None:
            files = log_to
    
    for file in files:
        log_print(*args, file=file, **kwargs)
        file.flush()
        try:
            os.fsync(file.fileno())
        except OSError:
            pass
