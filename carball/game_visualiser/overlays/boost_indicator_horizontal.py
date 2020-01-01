from typing import List, Tuple

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.axes import Axes
from matplotlib.patches import Rectangle

from carball.game_visualiser.color_scheme import *
from carball.game_visualiser.overlays.base_overlay import BaseOverlay


class BoostIndicatorHorizontal(BaseOverlay):
    width: int = 4500
    height: int = 300

    x_offset = 300
    y_offset = 750
    player_name_offset = 200

    def __init__(self, ax: Axes, df: pd.DataFrame, player_names: List[str], player_is_oranges: List[bool],
                 offset: Tuple[float, float] = (0, 0), scale: float = 1):
        super().__init__(ax, df, player_names, player_is_oranges, offset, scale)
        self.base_rectangles: List[Rectangle] = []
        self.boost_indicators: List[Rectangle] = []
        self.collect_highlights: List[Rectangle] = []

    def setup(self):
        self._setup_boost_indicators()

    def _setup_boost_indicators(self):
        orange_players = 0
        blue_players = 0
        for i, player_name in enumerate(self.player_names):
            player_is_orange = self.player_is_oranges[i]
            rect_xy = np.array(self.offset)
            if player_is_orange:
                rect_xy += (self.x_offset, self.y_offset * orange_players)

                plt.text(rect_xy[0] + self.width + self.player_name_offset,
                         rect_xy[1] + self.height / 2,
                         player_name,
                         ha='left', va='center', color=ORANGE_COLOR)
                base_rectangle = Rectangle(rect_xy, self.width, self.height, facecolor='grey', zorder=-1)

                outline = Rectangle(rect_xy, self.width, self.height, facecolor='#00000000',
                                    joinstyle="round", linewidth=2, edgecolor='k', zorder=100)
                orange_players += 1
            else:
                rect_xy += (-self.x_offset, self.y_offset * blue_players)

                plt.text(rect_xy[0] - self.width - self.player_name_offset,
                         rect_xy[1] + self.height / 2,
                         player_name,
                         ha='right', va='center', color=BLUE_COLOR)
                base_rectangle = Rectangle(rect_xy, -self.width, self.height, facecolor='grey', zorder=-1)

                outline = Rectangle(rect_xy, -self.width, self.height, facecolor='#00000000',
                                    joinstyle="round", linewidth=2, edgecolor='k', zorder=100)
                blue_players += 1

            collect_highlight = Rectangle(rect_xy, 0, self.height, facecolor='white', zorder=2, alpha=0)
            boost_indicator = Rectangle(tuple(rect_xy), 0, self.height, color='yellow', alpha=0.8, zorder=1, hatch="//")

            self.ax.add_patch(base_rectangle)
            self.base_rectangles.append(base_rectangle)
            self.ax.add_patch(outline)
            self.base_rectangles.append(outline)
            self.ax.add_patch(collect_highlight)
            self.collect_highlights.append(collect_highlight)

            self.ax.add_patch(boost_indicator)
            self.boost_indicators.append(boost_indicator)

    def update(self, frame: int):
        for i, player_name in enumerate(self.player_names):
            player_is_orange = self.player_is_oranges[i]

            boost_amount = self.df.loc[frame, (player_name, 'boost')] / 100
            new_width = boost_amount * self.width * self.scale

            player_boost_indicator = self.boost_indicators[i]
            current_width = player_boost_indicator.get_width()

            if not player_is_orange:
                new_width = -new_width
            player_boost_indicator.set_width(new_width)

            player_collect_highlight = self.collect_highlights[i]
            boost_diff_threshold = 0.05 * self.width
            # Only show highlight if boost amount increases by more than 5
            if abs(new_width) > abs(current_width) + boost_diff_threshold:
                player_collect_highlight.set_alpha(0.95)
                if player_is_orange:
                    player_collect_highlight.set_x(self.x_offset + current_width)
                    player_collect_highlight.set_width(new_width - current_width)
                else:
                    player_collect_highlight.set_x(-self.x_offset - abs(current_width))
                    player_collect_highlight.set_width(-abs(new_width - current_width))
            else:
                player_collect_highlight.set_alpha(player_collect_highlight.get_alpha() * 0.4)
