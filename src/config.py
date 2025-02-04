from typing import NamedTuple
import tomllib


class AxisConfig(NamedTuple):
    x: str
    signals: list[str]
    colors: list[str]
    limits: tuple[float, float]
    title: str
    ylabel: str


class PlotConfig(NamedTuple):
    time_window: int
    dt: float
    size: tuple[int, int]
    upper_left: AxisConfig
    lower_left: AxisConfig
    right: AxisConfig


class ServerConfig(NamedTuple):
    ip: str
    port: int
    timeout: float


class DataConfig(NamedTuple):
    save: bool
    path: str
    date_format: str


class FigureConfig(NamedTuple):
    save: bool
    path: str
    date_format: str
    format: str


class Config(NamedTuple):
    server: ServerConfig
    data: DataConfig
    figure: FigureConfig
    plot: PlotConfig


def load_config(path: str) -> Config:
    with open(path, "rb") as f:
        config = tomllib.load(f)

    colors = {
        "red": config["colors"]["red"],
        "green": config["colors"]["green"],
        "blue": config["colors"]["blue"],
        "yellow": config["colors"]["yellow"],
        "purple": config["colors"]["purple"],
        "black": config["colors"]["black"],
    }

    server = ServerConfig(
        ip=config["server"]["ip"],
        port=config["server"]["port"],
        timeout=config["server"]["timeout"],
    )

    data = DataConfig(
        save=config["data"]["save"],
        path=config["data"]["path"],
        date_format=config["data"]["date_format"],
    )

    figure = FigureConfig(
        save=config["figure"]["save"],
        path=config["figure"]["path"],
        date_format=config["figure"]["date_format"],
        format=config["figure"]["format"],
    )

    upper_left = AxisConfig(
        x=config["plot"]["upper_left"]["x"],
        signals=config["plot"]["upper_left"]["signals"],
        colors=[colors[color] for color in config["plot"]["upper_left"]["colors"]],
        limits=config["plot"]["upper_left"]["limits"],
        title=config["plot"]["upper_left"]["title"],
        ylabel=config["plot"]["upper_left"]["ylabel"],
    )

    lower_left = AxisConfig(
        x=config["plot"]["lower_left"]["x"],
        signals=config["plot"]["lower_left"]["signals"],
        colors=[colors[color] for color in config["plot"]["lower_left"]["colors"]],
        limits=config["plot"]["lower_left"]["limits"],
        title=config["plot"]["lower_left"]["title"],
        ylabel=config["plot"]["lower_left"]["ylabel"],
    )

    right = AxisConfig(
        x=config["plot"]["right"]["x"],
        signals=config["plot"]["right"]["signals"],
        colors=[colors[color] for color in config["plot"]["right"]["colors"]],
        limits=config["plot"]["right"]["limits"],
        title=config["plot"]["right"]["title"],
        ylabel=config["plot"]["right"]["ylabel"],
    )

    plot = PlotConfig(
        time_window=config["plot"]["time_window"],
        dt=config["plot"]["dt"],
        size=config["plot"]["size"],
        upper_left=upper_left,
        lower_left=lower_left,
        right=right,
    )

    return Config(
        server=server,
        data=data,
        figure=figure,
        plot=plot,
    )
