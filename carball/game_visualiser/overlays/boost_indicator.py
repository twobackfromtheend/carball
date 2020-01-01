from typing import List, Tuple

import pandas as pd
from matplotlib.axes import Axes
from matplotlib.patches import Rectangle
import matplotlib.pyplot as plt
import numpy as np

from carball.game_visualiser.color_scheme import *
from carball.game_visualiser.overlays.base_overlay import BaseOverlay


class BoostIndicator(BaseOverlay):
    width: int = 300
    height: int = 20

    def __init__(self, ax: Axes, df: pd.DataFrame, player_names: List[str], player_is_oranges: List[bool],
                 offset: Tuple[float, float] = (0, 0), scale: float = 1):
        super().__init__(ax, df, player_names, player_is_oranges, offset, scale)
        self.base_rectangles: List[Rectangle] = []
        self.boost_indicators: List[Rectangle] = []
        self.collect_highlights: List[Rectangle] = []

    def setup(self):
        self._setup_boost_indicators()

    def _setup_boost_indicators(self):
        y_offset = (self.height * 1.5 + 20) * self.scale
        rect_xy = np.array(self.offset, dtype=np.float)
        width = self.width * self.scale
        height = self.height * self.scale
        for i, player_name in enumerate(self.player_names):
            text_color = ORANGE_COLOR if self.player_is_oranges[i] else BLUE_COLOR
            plt.text(rect_xy[0] - 50 * self.scale, rect_xy[1] + height / 2,
                     player_name,
                     ha='right', va='center', color=text_color)

            base_rectangle = Rectangle(tuple(rect_xy), width, height, facecolor='grey', zorder=-1)
            self.ax.add_patch(base_rectangle)
            self.base_rectangles.append(base_rectangle)
            outline = Rectangle(tuple(rect_xy), width, height, facecolor='#00000000',
                                joinstyle="round", linewidth=2, edgecolor='k', zorder=100)
            self.ax.add_patch(outline)
            self.base_rectangles.append(outline)

            collect_highlight = Rectangle(tuple(rect_xy), width, height, facecolor='white', zorder=2, alpha=0)
            self.ax.add_patch(collect_highlight)
            self.collect_highlights.append(collect_highlight)

            boost_indicator = Rectangle(tuple(rect_xy), 0, height, color='yellow', alpha=0.8, zorder=1, hatch="//")
            self.ax.add_patch(boost_indicator)
            self.boost_indicators.append(boost_indicator)

            rect_xy += [0., y_offset]

    def update(self, frame: int):
        for i, player_name in enumerate(self.player_names):
            boost_amount = self.df.loc[frame, (player_name, 'boost')] / 100
            new_width = boost_amount * self.width * self.scale

            player_boost_indicator = self.boost_indicators[i]
            current_width = player_boost_indicator.get_width()
            player_boost_indicator.set_width(new_width)

            player_collect_highlight = self.collect_highlights[i]

            boost_diff_threshold = 0.05 * self.width * self.scale
            # Only show highlight if boost amount increases by more than 5
            if new_width > current_width + boost_diff_threshold:
                player_collect_highlight.set_alpha(0.95)
                player_collect_highlight.set_x(self.offset[0] + current_width)
                player_collect_highlight.set_width(new_width - current_width)
            else:
                player_collect_highlight.set_alpha(player_collect_highlight.get_alpha() * 0.4)
