from unittest import TestCase
import unittest
import warnings
from .. import client, server, logger, settings
from time import sleep

settings.set_default_port(0)

msg = ["a", range(10), {(1, 2, 3): 2 + 5j}]


class SequentialServerReceiveTest(TestCase):
    def setUp(self) -> None:
        self.srvr = server.SequentialServer()
        self.srvr.start()

        @self.srvr.client_handler
        def clnt_hndlr(clnt: server.Client):
            recv_msg = clnt.receive()
            self.assertEqual(recv_msg, msg)
            clnt.send(msg)

    def test_sending_receiving(self):
        test_conn = client.ConnectedServer(self.srvr.ip, self.srvr.port, background=False)

        @test_conn.on_connection
        def on_connect():
            test_conn.send(msg)
            recv_msg = test_conn.receive()
            self.assertEqual(recv_msg, msg)

        test_conn.connect()

    def tearDown(self) -> None:
        self.srvr.closing = True
        self.srvr.stop_running()
        while self.srvr.closing:
            pass
        print("Done")


if __name__ == '__main__':
    warnings.simplefilter("ignore", ResourceWarning)
    unittest.main()
