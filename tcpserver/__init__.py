from . import logger
from . import server

default_port: int = 1234


def set_default_port(port: int):
    """Set the global value of the default port to use. Should only be called just after imports."""
    global default_port
    default_port = port
