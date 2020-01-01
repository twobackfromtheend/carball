from typing import List, Tuple

import pandas as pd
from matplotlib.axes import Axes


class BaseOverlay:
    def __init__(self, ax: Axes, df: pd.DataFrame, player_names: List[str], player_is_oranges: List[bool],
                 offset: Tuple[float, float] = (0, 0), scale: float = 1):
        self.ax = ax
        self.df = df

        self.player_names = player_names
        self.player_is_oranges = player_is_oranges
        assert (len(player_names) == len(player_is_oranges)), "Lengths of player_names and player_is_oranges must match"

        self.offset = offset
        self.scale = scale

    def setup(self):
        raise NotImplementedError

    def update(self, frame: int):
        raise NotImplementedError
