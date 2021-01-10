"""
client.py
    Provides ConnectedSever class to connect to tcp servers and communicate with them.
"""
import socket
from .settings import default_header_size, default_chunk_size
from . import logger
import threading
import pickle
from pathlib import Path
from typing import Any, Callable, Generator, Tuple, Union


class ConnectedServer:
    """
    Class to handle connection with servers, send and receive python objects.
    Args:
        ip(str): The ip address (IPV4) of the server.
        port(int): The port the server is hosted on.
        background(bool): Whether the server runs in a separate thread or not.
    Attributes:
        background(bool): Whether the server runs in a separate thread or not.
        connection_thread(Union[None,threading.Thread]): The thread in which the connection is made and server
                                                         communication is done if background is set to True. Initially
                                                         set to None,the thread object is made when the start method
                                                         is called.
    """

    def __init__(self, ip: str, port: int, background: bool = True):
        self.background: bool = background
        if self.background:
            self.connection_thread: Union[None, threading.Thread] = None
        self.ip: str = ip
        self.port: int = port
        logger.log("Creating server socket")
        self.socket: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def on_connection(self, func: Callable) -> None:
        """
        The decorator for setting the start_connection.
        Args:
            func(Callable): The start_connection method for the client.

        Returns:
            None
        """
        # noinspection PyAttributeOutsideInit
        self.start_connection = func

    def start_connection(self) -> None:
        """
        The method that is called to handle the connection with the server.
        Returns:
            None
        """
        raise Exception("No Connection Handler Set")

    def main_connection(self) -> None:
        """
        This method is used to create the connection_thread. It calls the start_connection method then closes
        the connection.
        Returns:
            None
        """
        self.start_connection()
        self.close()

    def close(self) -> None:
        """
        Method used to close the connection
        Returns:
            None
        """
        self.socket.close()
        logger.close_log_files()

    def connect(self) -> None:
        """
        Method to start connection with server.
        Returns:
            None
        """
        logger.log(f"Connecting to {self.ip} at {self.port}")
        self.socket.connect((self.ip, self.port))
        logger.log(f"Connection Successful")
        self.connection_thread = threading.Thread(target=self.main_connection)
        if self.background:
            self.connection_thread.start()
        else:
            self.start_connection()

    def send(self, obj: Any) -> None:
        """
        Send a python object that can be pickled to the server. First sends a fixed length header defined in
        tcpsockets.settings giving the size of outgoing message then sends the pickled object. default_header_size
        can be set by using tcpsockets.settings.set_default_header_size function.

        Args:
            obj(Any): The Object that has to be sent to the server that can be pickled.

        Returns:
            None

        """
        pickled_obj = pickle.dumps(obj)
        pickled_obj_size = len(pickled_obj)
        header = str(pickled_obj_size).ljust(default_header_size).encode("utf-8")
        self.socket.send(header)
        self.socket.send(pickled_obj)

    def receive(self, chunk_size: int = None) -> Any:
        """
        Receive a python object sent by the server. First receive a fixed length header then receive the pickled object
        chunk by chunk using the chunk_size argument.
        Args:
            chunk_size(int): The amount of bytes to receive at once. Defaults to tcpsockets.settings.default_chunk_size.
        Returns:
            Any: The object sent by the server
        """
        if chunk_size is None:
            chunk_size = default_chunk_size
        obj_size_header: str = self.socket.recv(default_header_size).decode("utf-8")
        obj_size: int = int(obj_size_header.strip())
        obj_pickled = b""
        for _ in range(obj_size // chunk_size):
            obj_pickled += self.socket.recv(chunk_size)
        obj_pickled += self.socket.recv(obj_size % chunk_size)
        return pickle.loads(obj_pickled)
    
    def send_file(self, file_location:Path, chunk_size:int) -> Generator[Tuple[int, int], None, None]:
        """
        Send a file object in small chunks whose sizes are "chunk_size" each.
        Args:
            file_location(Path): Path object representing file location of the file to be sent.
            chunk_size(int): Size of 1 chunk.
        Returns:
            Generator[Tuple[int, int], None, None]: A Generator containing bytes sent and total bytes to be sent.
        """
        file_size = file_location.stat().st_size
        self.send((file_location.name, file_size))
        sent_size = 0
        with open(file_location, "rb") as file:
            file_chunk = file.read(chunk_size)
            self.socket.send(file_chunk)
            sent_size += len(file_chunk)
            yield sent_size, file_size
            while file_chunk:
                file_chunk = file.read(chunk_size)
                self.socket.send(file_chunk)
                sent_size += len(file_chunk)
                yield sent_size, file_size
    
    def receive_file(self, file_save_location:Path, chunk_size:int) -> Generator[Tuple[int, int], None, None]:
        """
        Receive a file object in small chunks whose sizes are "chunk_size" each.
        Args:
            file_location(Path): Path object representing location of the folder where the file is to be saved.
            chunk_size(int): Size of 1 chunk.
        Returns:
            Generator[Tuple[int, int], None, None]: A Generator containing bytes received and total bytes to be received.
        """
        name, size = self.receive()
        with open(file_save_location / name, "wb") as file:
            byte_number = 0
            while byte_number < size:
                byte_chunk = self.socket.recv(chunk_size)
                byte_number += len(byte_chunk)
                file.write(byte_chunk)
                yield byte_number, size
