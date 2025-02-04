import datetime
import os
from dataclasses import dataclass

from matplotlib.axes import Axes
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import numpy as np

from .config import Config
from .data import Data


@dataclass
class PlotInfo:
    signals: list[str]
    limits: tuple[float, float]
    title: str
    y_label: str
    x_label: str
    color: list[str]


@dataclass
class AxInfo:
    ax: Axes
    lines: list
    signals: list[str]
    window: int

    def update(self, t: np.ndarray, y: list[np.ndarray]) -> None:
        # left pad with zeros if the new data is smaller than the window
        if len(t) < self.window:
            t = np.pad(t, (self.window - len(t), 0), mode="constant")
            y = [np.pad(y_, (self.window - len(y_), 0), mode="constant") for y_ in y]
        else:
            t = t[-self.window:]
            y = [y_[-self.window:] for y_ in y]

        for i in range(len(self.signals)):
            self.lines[i].set_xdata(t)
            self.lines[i].set_ydata(y[i])

        self.ax.relim()
        self.ax.autoscale_view(True, True, True)

    def clear(self) -> None:
        for i in range(len(self.signals)):
            self.lines[i].set_ydata(np.zeros(self.window))
            self.lines[i].set_xdata(np.zeros(self.window))


class Plotter:
    def __init__(self, config: Config) -> None:
        self.save_ = config.figure.save
        self.path = config.figure.path
        self.date_format = config.figure.date_format
        self.format = config.figure.format

        window = int(config.plot.time_window / config.plot.dt)
        upper_left = PlotInfo(
            signals=config.plot.upper_left.signals,
            limits=config.plot.upper_left.limits,
            title=config.plot.upper_left.title,
            y_label=config.plot.upper_left.ylabel,
            x_label="Time (s)",
            color=config.plot.upper_left.colors,
        )
        lower_left = PlotInfo(
            signals=config.plot.lower_left.signals,
            limits=config.plot.lower_left.limits,
            title=config.plot.lower_left.title,
            y_label=config.plot.lower_left.ylabel,
            x_label="Time (s)",
            color=config.plot.lower_left.colors,
        )
        right = PlotInfo(
            signals=config.plot.right.signals,
            limits=config.plot.right.limits,
            title=config.plot.right.title,
            y_label=config.plot.right.ylabel,
            x_label="Time (s)",
            color=config.plot.right.colors,
        )

        # init plots
        plt.figure(figsize=config.plot.size)
        plt.tight_layout()
        gs = gridspec.GridSpec(2, 2, width_ratios=[0.45, 0.55])

        self.up_left_ax = self._init_ax(upper_left, gs, 0, window)
        self.down_left_ax = self._init_ax(lower_left, gs, 1, window)
        self.right_ax = self._init_ax(right, gs, 2, window)

    def _init_ax(self, plot_info: PlotInfo, gs: gridspec.GridSpec, position: int, window: int) -> AxInfo:
        match position:
            case 0:
                ax = plt.subplot(gs[0, 0])
            case 1:
                ax = plt.subplot(gs[1, 0])
            case 2:
                ax = plt.subplot(gs[:, 1])
            case _:
                raise ValueError("wrong number of plots")

        n_signals = len(plot_info.signals)
        t = np.zeros(window)
        y = np.zeros(window)

        lines = []
        ys = []
        for i in range(n_signals):
            line, = ax.plot(t, y, label=plot_info.signals[i], color=plot_info.color[i])
            lines.append(line)
            ys.append(y)

        ax.set_title(plot_info.title)
        ax.set_ylabel(plot_info.y_label)
        ax.set_xlabel(plot_info.x_label)
        ax.set_ylim(plot_info.limits[0]-1, plot_info.limits[1]+1)
        ax.grid(alpha=0.5)
        ax.legend()
        ax.autoscale_view(True, True, True)

        return AxInfo(ax, lines, plot_info.signals, window)

    def update(self, data: Data) -> None:
        plt.ion()

        # update plots
        self.up_left_ax.update(data["time"], [data[s] for s in self.up_left_ax.signals])
        self.down_left_ax.update(data["time"], [data[s] for s in self.down_left_ax.signals])
        self.right_ax.update(data["time"], [data[s] for s in self.right_ax.signals])

        self.draw()

    def draw(self) -> None:
        plt.draw()
        plt.pause(0.001)

    def save(self) -> None:
        if not self.save_:
            return

        date = datetime.datetime.now().strftime(self.date_format)
        filename = os.path.join(self.path, f"{date}.{self.format}")
        plt.savefig(filename)

    def clear(self) -> None:
        self.up_left_ax.clear()
        self.down_left_ax.clear()
        self.right_ax.clear()

    def close(self):
        plt.ioff()
        plt.close()
