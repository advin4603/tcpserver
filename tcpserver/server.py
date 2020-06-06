import socket
from . import logger
from abc import ABC, abstractmethod, abstractproperty
from typing import Any
import threading


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

    def __init__(self, ip: str = socket.gethostbyname(socket.gethostname()), port: int = None, queue: int = None,
                 background: bool = True):
        from . import default_port, default_queue
        self.background = background
        self.running = False
        self.port: int = port
        if self.port is None:
            if default_port is None:
                raise Exception("Either Server port or Default Port must be set.")
            self.port = default_port
        self.queue = queue
        if self.queue is None:
            if default_queue is None:
                raise Exception("Either queue parameter or Default Queue must be set.")
            self.queue = default_queue

        self.ip: str = ip
        logger.log("Creating server socket")
        self.socket: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        logger.log(f"Binding socket to {self.ip} at {self.port}")
        self.socket.bind((self.ip, self.port))

    @abstractmethod
    def handler(self, client):
        return

    @abstractmethod
    def client_handler(self, func):
        pass

    @abstractmethod
    def start(self):
        pass


class SequentialServer(Server):
    def __init__(self, ip: str = socket.gethostbyname(socket.gethostname()), port: int = None, queue: int = None,
                 background: bool = True):
        super(SequentialServer, self).__init__(ip, port, queue, background)
        self.handling = False
        self.stopper_thread = threading.Thread(target=self.stopper)

        if self.background:
            self.server_thread = threading.Thread(target=self.starter)
        self.current_client = None

    def handler(self, client):
        raise Exception("No Handler Set")

    def check_run(self) -> bool:
        if not self.running:
            self.socket.close()
            return True
        return False

    def stopper(self):
        while self.running or self.handling:
            pass
        closer_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        closer_socket.connect((self.ip, self.port))

    def client_handler(self, func):
        self.handler = func

    def starter(self):
        self.running = True
        self.stopper_thread.start()
        logger.log(f"Listening for connections on {self.ip} at {self.port}")
        self.socket.listen(self.queue)
        while self.running:
            client, address = self.socket.accept()
            # TODO Create Client Class then Instantiate and pass to handler
            self.handling = True
            self.current_client = client
            logger.log(f"Connection from {address}")
            self.handler(client)
            logger.log(f"Client from {address} disconnected")
            self.handling = False
            self.current_client = None

    def start(self):
        if self.background:
            self.server_thread.start()
        else:
            self.starter()
