from typing import List, Tuple, Optional

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.axes import Axes

from carball.game_visualiser.overlays.base_overlay import BaseOverlay
from carball.output_generation.data_frame_generation.prefixes import DF_GAME_PREFIX


class Timer(BaseOverlay):

    def __init__(self, ax: Axes, df: pd.DataFrame, player_names: List[str], player_is_oranges: List[bool],
                 offset: Tuple[float, float] = (0, 0), scale: float = 1):
        super().__init__(ax, df, player_names, player_is_oranges, offset, scale)
        self.seconds_remaining = df[(DF_GAME_PREFIX, 'seconds_remaining')]
        self.timer: Optional[plt.Text] = None

    def setup(self):
        self.timer = plt.text(self.offset[0], self.offset[1],
                              self._get_text_from_seconds(self.seconds_remaining.iloc[0]), ha='center')

    def update(self, frame: int):
        self.timer.set_text(self._get_text_from_seconds(self.seconds_remaining[frame]))

    @staticmethod
    def _get_text_from_seconds(seconds_remaining: float) -> str:
        minutes = seconds_remaining // 60
        seconds = seconds_remaining - minutes * 60
        return f"{minutes:d}:{seconds:02}"
