import socket
from . import logger
from .settings import default_header_size, default_chunk_size, default_port, default_queue
from abc import ABC, abstractmethod
import threading
from typing import Tuple, Any, Callable, List
import pickle
import traceback


class Server(ABC):
    """
    An Abstract Server object containing the ip and port it is bound to.

    Args:
        ip (str): The ip address(IPV4) of the server. Defaults to local machine's ip
        port(int): The port the server must be bound to. Defaults to tcpsockets.settings.default_port if it is not set
                   to None else raises Exception.
        queue(int): The waiting queue length of the server. Defaults to tcpsockets.settings.default_queue if it is not
                    set to None else raises Exception.
        background(bool): Whether the server runs in background (in separate thread) or not. Defaults to True
    Attributes:
        ip (str): The ip address(IPV4) of the server.
        port(str): The port the server is bound to.
        socket(socket.socket): Reference to the socket object.
        background(bool): Whether the server runs in separate thread or not.
        running(bool): Whether the server is running or not.
        server_thread(threading.Thread): The Thread in which the server will run if background is True.
    """

    def __init__(self, ip: str = socket.gethostbyname(socket.gethostname()), port: int = None, queue: int = None,
                 background: bool = True):
        self.background: bool = background
        self.running: bool = False
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
        if self.background:
            self.server_thread = threading.Thread(target=self.starter)

    def handler(self, client: "Client") -> None:
        """
        The Function called when the client connects to the server. Must be overridden by inheritance or by calling
        the client_handler decorator.

        Args:
            client(Client): The Client object that has connected to the server.

        Returns:
            None
        """
        raise Exception("No Handler set")

    def client_handler(self, func: Callable) -> None:
        """

        Args:
            func(Callable): The User Defined Client Handler function that must take one positional argument of type
            tcpsockets.server.Client.

        Returns:
            None
        """
        # noinspection PyAttributeOutsideInit
        self.handler = func

    def start(self) -> None:
        """
        Returns:
            None
        """
        if self.background:
            self.server_thread.start()
        else:
            self.starter()

    @abstractmethod
    def starter(self):
        pass

    def stop_running(self) -> None:
        """
        Calling this function stops the Server.
        Returns: None
        """
        self.running = False


class Client:
    """
    A Client Class which represents a client a they connect to the server. Provides methods to send and receive any
    python object that can be pickled.

    Args:
        sckt(socket.socket): reference to the client's socket returned by socket.accept()
        address(Tuple[str,int]): a tuple containing the ip and the port.
    Attributes:
        total_client_connections(int): A Class variable which tracks the total number of client by tracking all its
                                       Objects.
        client_connection_id(int): An id uniquely identifying one instance of a connection. It is an int set to the
                                   total number of connections made just after the client joins.
        socket(socket.socket): reference to the client's socket returned by socket.accept()
        ip(str): The ip address(IPV4) of the client returned by socket.accept()
        port(int): The port the client is connected to.


    """
    total_client_connections: int = 0

    def __init__(self, sckt: socket.socket, address: Tuple[str, int]):
        Client.total_client_connections += 1
        self.client_connection_id: int = Client.total_client_connections
        self.socket: socket.socket = sckt
        self.ip: str = address[0]
        self.port: int = address[1]

    def close(self) -> None:
        """
        Closes the socket.
        Returns:
            None

        """
        self.socket.close()

    def send(self, obj: Any) -> None:
        """
        Send a python object that can be pickled to the client. First sends a fixed length header defined in
        tcpsockets.settings giving the size of incoming message then sends the pickled object. default_header_size
        can be set by using tcpsockets.settings.set_default_header_size function.

        Args:
            obj(Any): The Object that has to be sent to the client that can be pickled.

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
        Receive a python object sent by the client. First receive a fixed length header then receive the pickled object
        chunk by chunk using the chunk_size argument.
        Args:
            chunk_size(int): The amount of bytes to receive at once. Defaults to tcpsockets.settings.default_chunk_size.
        Returns:
            Any
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

    def __eq__(self, other: "Client") -> bool:
        """
        Checks if the client objects have same client_connection_id
        Args:
            other(Client): The other client object to be compared with.
        Returns:
            bool: bool saying whether both client objects have the same client_connection_id.
        """
        return self.client_connection_id == other.client_connection_id


class SequentialServer(Server):
    def __init__(self, ip: str = socket.gethostbyname(socket.gethostname()), port: int = None, queue: int = None,
                 background: bool = True):
        super(SequentialServer, self).__init__(ip, port, queue, background)
        self.handling = False
        self.stopper_thread = threading.Thread(target=self.stopper)

        self.current_client = None

    def stopper(self):
        while self.running or self.handling:
            pass
        closer_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            closer_socket.connect((self.ip, self.port))
        except ConnectionRefusedError:
            pass
        logger.close_log_files()
        closer_socket.close()

    def starter(self):
        self.running = True
        self.stopper_thread.start()
        logger.log(f"Listening for connections on {self.ip} at {self.port}")
        self.socket.listen(self.queue)
        client, address = self.socket.accept()
        while self.running:
            self.handling = True
            self.current_client = Client(client, address)
            logger.log(f"Connection from {address}")
            try:
                self.handler(self.current_client)
            except BaseException:
                logger.log(f"Client from {address} got disconnected due to an error: {traceback.format_exc()}")
            logger.log(f"Client from {address} disconnected")
            self.handling = False
            self.current_client = None
            client, address = self.socket.accept()
        self.socket.close()


class ParallelServer(Server):
    def __init__(self, ip: str = socket.gethostbyname(socket.gethostname()), port: int = None, queue: int = None,
                 background: bool = True):
        super(ParallelServer, self).__init__(ip, port, queue, background)
        self.client_threads: List[threading.Thread] = []
        self.clients: List[Client] = []
        self.stopper_thread = threading.Thread(target=self.stopper)
        if self.background:
            self.server_thread = threading.Thread(target=self.starter)

    def client_func(self, client: Client):
        try:
            self.handler(client)
        except BaseException:
            logger.log(
                f"Client from {(client.ip, client.port)} got disconnected due to an error:\n{traceback.format_exc()}")
        for index, other_clnt in enumerate(self.clients):
            if other_clnt == client:
                self.clients[index].close()
                del self.clients[index]
                logger.log(f"Client from {(client.ip, client.port)} disconnected")
                return

    def starter(self):
        self.running = True
        self.stopper_thread.start()
        logger.log(f"Listening for connections on {self.ip} at {self.port}")
        self.socket.listen(self.queue)
        client, address = self.socket.accept()
        while self.running:
            new_client = Client(client, address)
            self.clients.append(new_client)
            logger.log(f"Connection from {address}")
            handler_thread = threading.Thread(target=lambda: self.client_func(new_client))
            self.client_threads.append(handler_thread)
            handler_thread.start()
            client, address = self.socket.accept()
        while self.handling:
            pass
        self.socket.close()

    @property
    def handling(self):
        return any([i.is_alive() for i in self.client_threads])

    def stopper(self):
        while 1:
            if not self.running and not self.handling:
                closer_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                try:
                    closer_socket.connect((self.ip, self.port))
                except ConnectionRefusedError:
                    logger.close_log_files()
                    return
                logger.close_log_files()
                closer_socket.close()
                break
