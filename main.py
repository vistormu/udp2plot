import queue
import os
import argparse

from src import (
    Server,
    Plotter,
    load_config,
    Data,
)


def get(data: queue.Queue):
    try:
        return data.get_nowait()
    except queue.Empty:
        return None


def main(path: str) -> None:
    config = load_config(path)

    # queue for data exchange between server and plotter
    data_queue = queue.Queue()
    event_queue = queue.Queue()

    # server
    server = Server(data_queue, event_queue, config.server.timeout)
    server.start(config.server.ip, config.server.port)

    # plots
    plotter = Plotter(config=config)

    # data
    data = Data(path=config.data.path, save=config.data.save)

    client_connected = False

    while True:
        try:
            event = get(event_queue)

            # continue until a client connects
            if event != "connected" and not client_connected:
                continue

            client_connected = True

            # reset plots and save data if the client just disconnected
            if event == "disconnected":
                client_connected = False
                plotter.clear()
                data.save(config.data.format)
                # plotter.show()
                continue

            # get data from the server
            while not data_queue.empty():
                data.update(data_queue.get())

            # update plots
            plotter.update(data)

        except KeyboardInterrupt:
            server.stop()
            plotter.close()
            break


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=str, default="config.toml")
    args = parser.parse_args()

    main(args.config)
