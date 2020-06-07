import socket
from .settings import default_header_size, default_chunk_size
from . import logger
import threading
import pickle


class ConnectedServer:
    def __init__(self, ip: str, port: int, background: bool):
        self.background: bool = background
        if self.background:
            self.connection_thread = threading.Thread(target=self.start_connection)
        self.ip: str = ip
        self.port: int = port
        logger.log("Creating server socket")
        self.socket: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def on_connection(self, func):
        self.start_connection = func

    def start_connection(self):
        raise Exception("No Connection Handler Set")

    def connect(self):
        logger.log(f"Connecting to {self.ip} at {self.port}")
        self.socket.connect((self.ip, self.port))
        logger.log(f"Connection Successful")
        if self.background:
            self.connection_thread.start()
        else:
            self.start_connection()
