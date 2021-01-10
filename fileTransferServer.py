from tcpsockets import server
from pathlib import Path

srvr = server.ParallelServer(port=1234)

@srvr.client_handler
def handler(clnt:server.Client):
    clnt.receive_file(Path(".\\downloaded"), 50)
    clnt.send_file(Path("setup.py"), 12)

srvr.start()

while input() != "q":
    pass
srvr.stop_running()
