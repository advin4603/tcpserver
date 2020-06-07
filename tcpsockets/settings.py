default_header_size: int = 16
default_chunk_size: int = 64
default_port: int = 1234
default_queue: int = 5


def set_default_port(port: int):
    """Set the global value of the default port to use. Should only be called just after imports."""
    global default_port
    default_port = port


def set_default_queue(queue: int):
    """Set the global value of the default queue length to use. Should only be called just after imports."""
    global default_queue
    default_queue = queue


def set_default_header_size(header_size: int):
    """Set the global value of the default header_size to use. Should only be called just after imports."""
    global default_header_size
    default_header_size = header_size


def set_default_chunk_size(chunk_size: int):
    """Set the global value of the default chunk_size to use. Should only be called just after imports."""
    global default_chunk_size
    default_chunk_size = chunk_size
