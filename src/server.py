import socket
import queue
import json
import threading
import time

from echro import echo


def exception_handler(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            return e
    return wrapper


class Server:
    def __init__(self,
                 data_queue: queue.Queue,
                 event_queue: queue.Queue,
                 timeout: float,
                 ) -> None:
        self.socket = None
        self.data_queue = data_queue
        self.event_queue = event_queue

        self.timeout = timeout
        self.client_address = None
        self.last_data_time = 0.0

        self.running = False

    def start(self, host: str, port: int) -> None:
        self.server_thread = threading.Thread(target=self._start, args=(host, port))
        self.server_thread.start()

    @exception_handler
    def _start(self, host: str, port: int) -> Exception | None:
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind((host, port))

        echo(
            "-> server started\n",
            f"   |> host: {host}\n",
            f"   |> port: {port}\n\n",
            pipeline="blue,0,reset,1,2",
        )

        self.socket.settimeout(0.1)

        self.running = True
        while self.running:
            try:
                data, addr = self.socket.recvfrom(4096)
                now = time.time()
                self.last_data_time = now

                # new client connects
                if self.client_address is None:
                    self.client_address = addr

                    echo(
                        "-> client connected\n",
                        f"  |> ip: {addr[0]}\n",
                        f"  |> port: {addr[1]}\n\n",
                        pipeline="green,0,reset,1,2",
                    )

                    self.event_queue.put("connected")

                self.data_queue.put(json.loads(data.decode('utf-8')))

            except socket.timeout:
                if self.client_address is not None:
                    now = time.time()
                    if now - self.last_data_time > self.timeout:
                        self.event_queue.put("disconnected")

                        echo(
                            "-> client disconnected\n",
                            f"  |> ip: {self.client_address[0]}\n",
                            f"  |> port: {self.client_address[1]}\n\n",
                            pipeline="red,0,reset,1,2",
                        )

                        self.client_address = None

                continue

    def stop(self) -> None:
        self.running = False
        if not self.socket:
            return

        self.socket.close()
        self.socket = None
        self.server_thread.join()
