import math
from typing import List, Optional, Tuple

import pandas as pd
import numpy as np
from matplotlib.axes import Axes
from matplotlib.patches import Circle
from matplotlib.quiver import Quiver

from carball.game_visualiser.color_scheme import *
from carball.game_visualiser.overlays.base_overlay import BaseOverlay
from carball.output_generation.data_frame_generation.prefixes import DF_BALL_PREFIX


class Minimap(BaseOverlay):
    def __init__(self, ax: Axes, df: pd.DataFrame, player_names: List[str], player_is_oranges: List[bool],
                 offset: Tuple[float, float] = (0, 0), scale: float = 1):
        super().__init__(ax, df, player_names, player_is_oranges, offset, scale)

        self.player_quivers: List[Quiver] = []
        self.ball: Optional[Circle] = None

    def setup(self):
        self._plot_stadium()
        self._create_player_quivers()
        self._create_ball()

    def _plot_stadium(self):
        points = np.array([
            [-4096, 0],
            [-4096, -3904],
            [-2880, -5120],
            [-893, -5120],
            [-893, -6000],
            [893, -6000],
            [893, -5120],
            [2880, -5120],
            [4096, -3904],
            [4096, 0],
        ]) * self.scale + self.offset
        blue_color = BLUE_COLOR
        self.ax.plot(points[:, 0], points[:, 1], '-', color=blue_color)
        self.ax.fill_between(points[:, 0], points[:, 1], '-', color=blue_color, alpha=0.1)

        orange_color = ORANGE_COLOR
        self.ax.plot(points[:, 0], -points[:, 1], '-', color=orange_color)
        self.ax.fill_between(points[:, 0], -points[:, 1], '-', color=orange_color, alpha=0.1)

    def _create_player_quivers(self):
        for player_is_orange in self.player_is_oranges:
            player_color = ORANGE_COLOR if player_is_orange else BLUE_COLOR
            quiver = self.ax.quiver(0, 0, 0, 1,
                                    color=player_color,
                                    scale=30,
                                    width=0.015,
                                    headlength=0.5,
                                    headwidth=1, pivot='mid')
            self.player_quivers.append(quiver)

    def _create_ball(self):
        self.ball = Circle((0, 0), radius=100 * self.scale, color='grey')
        self.ax.add_patch(self.ball)

    def update(self, frame: int):
        for i, player_name in enumerate(self.player_names):
            quiver = self.player_quivers[i]
            car_exists = not np.isnan(self.df.loc[frame, (player_name, 'pos_x')])
            if car_exists:
                quiver.set_alpha(1)
                positions = self.df.loc[frame, (player_name, ['pos_x', 'pos_y'])] * self.scale + self.offset
                quiver.set_offsets(positions)
                yaw = self.df.loc[frame, (player_name, 'rot_y')]
                x = math.cos(yaw)
                y = math.sin(yaw)
                quiver.set_UVC(x, y)
            else:
                quiver.set_alpha(0)

        ball_position = self.df.loc[frame, (DF_BALL_PREFIX, ['pos_x', 'pos_y'])] * self.scale + self.offset
        self.ball.center = ball_position


if __name__ == '__main__':
    import matplotlib.pyplot as plt

    plt.figure()
    ax = plt.gca()
    ax.set_aspect("equal")

    # Test stadium
    mm = Minimap(ax, None, [], [])
    mm._plot_stadium()
    plt.show()
