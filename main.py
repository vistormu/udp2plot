import queue
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
    plotter = Plotter(config)

    # data
    data = Data(config.data.path, config.data.save, config.data.date_format)

    client_connected = False

    while True:
        try:
            event = get(event_queue)

            # continue until a client connects
            if event != "connected" and not client_connected:
                plotter.draw()
                continue

            # client has just connected
            if event == "connected" and not client_connected:
                client_connected = True
                data.clear()
                plotter.clear()

            # client has just disconnected
            if event == "disconnected" and client_connected:
                client_connected = False

                data.save()
                plotter.save()

                continue

            # while client is connected
            while not data_queue.empty():
                data.update(data_queue.get())

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
