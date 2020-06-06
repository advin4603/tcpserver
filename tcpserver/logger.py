from time import ctime
from typing import List
import sys

logging: bool = True
log_to: List[type(sys.stdout)] = [sys.stdout]


def add_log_files(*args: type(sys.stdout)):
    """
    Add multiple opened file objects to the list of files which the logger logs to.
    Args:
        args(io.TextIOWrapper):All the file objects where logs are written to.
    """
    global log_to
    log_to.extend(args)


def set_log_files(file_list: List[type(sys.stdout)]):
    """
    Set the list of files which the logger logs to.
    Args:
        file_list(List[type(sys.stdout)]): list of all files the logger must log to
    """
    global log_to
    log_to.clear()
    log_to.extend(file_list)


def set_logging(logBool: bool):
    """Turn Logging on or off. Should only be called just after imports."""
    global logging
    logging = logBool


def log(*args, files: List[type(sys.stdout)] = None, **kwargs):
    """
    Log statements to multiple opened files.
    Args:
        files(List[type(sys.stdout)]): A list of opened file objects to log to.
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
            files = [sys.stdout]
    log_init = f"[{ctime()}] "
    for file in files:
        print(log_init, *args, file=file, **kwargs)
