from time import ctime
from typing import List
import sys
from typing import TextIO

logging: bool = True
log_to: List[TextIO] = [sys.stdout]


def close_log_files():
    for file in log_to:
        file.close()


def add_log_files(*args: TextIO):
    """
    Add multiple opened file objects to the list of files which the logger logs to.
    Args:
        args(TextIO):All the file objects where logs are written to.
    """
    global log_to
    log_to.extend(args)


def set_log_files(file_list: List[TextIO]):
    """
    Set the list of files which the logger logs to.
    Args:
        file_list(List[TextIO]): list of all files the logger must log to
    """
    global log_to
    log_to.clear()
    log_to.extend(file_list)


def set_logging(logBool: bool):
    """Turn Logging on or off. Should only be called just after imports."""
    global logging
    logging = logBool


def log(*args, files: List[TextIO] = None, **kwargs):
    """
    Log statements to multiple opened files.
    Args:
        files(List[TextIO]): A list of opened file objects to log to.
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
    log_init = f"[{ctime()}] "
    for file in files:
        print(log_init, *args, file=file, **kwargs)
