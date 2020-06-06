import socket
from . import logger
from abc import ABC, abstractmethod, abstractproperty


class Server(ABC):
    """
    An Abstract Server object contains the ip and port it is bound to.

    Args:
        ip (str): The ip address(IPV4) of the server. Defaults to local machine's ip
        port(int): The port the server must be bound to. Defaults to socketServer.default_port if it is not set to None
                   else raises Exception.
    Attributes:
        ip (str): The ip address(IPV4) of the server.
        port(str): The port the server is bound to.
        socket(socket.socket): Reference to the socket object.
    """
    def __init__(self, ip: str = socket.gethostbyname(socket.gethostname()), port: int = None):
        from . import default_port
        self.port: int = port
        if self.port is None:
            if default_port is None:
                raise Exception("Either Server port or Default Port must be set.")
            self.port = default_port

        self.ip: str = ip
        logger.log("Creating server socket")
        self.socket: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        logger.log(f"Binding socket to {self.ip} at {self.port}")
