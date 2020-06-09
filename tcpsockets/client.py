import socket
from .settings import default_header_size, default_chunk_size
from . import logger
import threading
import pickle
from typing import Any, Callable


class ConnectedServer:
    def __init__(self, ip: str, port: int, background: bool = True):
        self.background: bool = background
        if self.background:
            self.connection_thread = None
        self.ip: str = ip
        self.port: int = port
        logger.log("Creating server socket")
        self.socket: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def on_connection(self, func: Callable):
        self.start_connection = func

    def start_connection(self):
        raise Exception("No Connection Handler Set")

    def main_connection(self):
        self.start_connection()
        self.close()

    def close(self):
        self.socket.close()
        logger.close_log_files()

    def connect(self):
        logger.log(f"Connecting to {self.ip} at {self.port}")
        self.socket.connect((self.ip, self.port))
        logger.log(f"Connection Successful")
        self.connection_thread = threading.Thread(target=self.main_connection)
        if self.background:
            self.connection_thread.start()
        else:
            self.start_connection()

    def send(self, obj: Any):
        pickled_obj = pickle.dumps(obj)
        pickled_obj_size = len(pickled_obj)
        header = str(pickled_obj_size).ljust(default_header_size).encode("utf-8")
        self.socket.send(header)
        self.socket.send(pickled_obj)

    def receive(self, chunk_size: int = None) -> Any:
        if chunk_size is None:
            chunk_size = default_chunk_size
        obj_size_header: str = self.socket.recv(default_header_size).decode("utf-8")
        obj_size: int = int(obj_size_header.strip())
        obj_pickled = b""
        for _ in range(obj_size // chunk_size):
            obj_pickled += self.socket.recv(chunk_size)
        obj_pickled += self.socket.recv(obj_size % chunk_size)
        return pickle.loads(obj_pickled)
