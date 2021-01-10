from tcpsockets import client
from pathlib import Path

chat_srvr = client.ConnectedServer("192.168.1.3", 1234)


@chat_srvr.on_connection
def on_connection():
    for done, total in chat_srvr.send_file(Path("Log.txt"), 50):
        print(f"{done}/{total}")
    print("Done 1")
    for done, total in chat_srvr.receive_file(Path(".\\downloaded"), 15):
        print(f"{done}/{total}")
    print("Done 2")

chat_srvr.connect()