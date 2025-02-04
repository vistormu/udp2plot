import os
import datetime
import pandas as pd
import numpy as np

from echro import echo


class Data:
    def __init__(self, path: str, save: bool, date_format: str) -> None:
        self.data: dict[str, list[float]] = {}
        self.save_ = save
        self.date_format = date_format

        self.path = path
        if not os.path.exists(self.path) and self.save_:
            os.makedirs(self.path)

    def update(self, d: dict[str, float]) -> None:
        for k, v in d.items():
            if k in self.data:
                self.data[k].append(v)
            else:
                self.data[k] = [v]

    def save(self) -> None:
        if not self.save_ or not self.data:
            return

        date = datetime.datetime.now().strftime(self.date_format)
        filename = os.path.join(self.path, f"{date}.csv")
        pd.DataFrame(self.data).to_csv(filename, index=False)

        echo(
            "-> data saved\n",
            f"   |> path: {filename}\n",
            pipeline="green,0,reset,1",
        )

    def clear(self) -> None:
        self.data.clear()

    def __getitem__(self, key: str) -> np.ndarray:
        data = self.data.get(key, [])
        if not data:
            echo(
                "-> unknown key recieved\n",
                f"   |>{key}\n\n",
                pipeline="yellow,0,reset,1",
            )

        return np.array(data)
