from typing import List

import numpy as np
import pandas as pd

from api.analysis.hit_pb2 import Hit
from carball.analysis2.constants.constants import FIELD_Y_THIRD
from carball.json_parser.game import Game as JsonParserGame
from carball.output_generation.data_frame_generation.prefixes import DF_GAME_PREFIX, DF_BALL_PREFIX


def calculate_pressures(hits: List[Hit], json_parser_game: JsonParserGame, df: pd.DataFrame):
    ball_y = df[(DF_BALL_PREFIX, 'pos_y')].rename('ball_y')
    goal_number = df[(DF_GAME_PREFIX, 'goal_number')].rename('goal_number')
    previous_goal_number = goal_number.shift(1).rename('previous_goal_number')

    current_pressure = None
    pressures = {}
    _df = pd.concat([ball_y, goal_number, previous_goal_number], axis=1)
    for row_tuple in _df.itertuples():
        if not np.isnan(row_tuple.goal_number) and row_tuple.goal_number == row_tuple.previous_goal_number:
            if current_pressure is None:
                if row_tuple.ball_y > FIELD_Y_THIRD:
                    current_pressure = 1
                elif row_tuple.ball_y < -FIELD_Y_THIRD:
                    current_pressure = -1
            else:
                if current_pressure == 1:
                    if row_tuple.ball_y < 0:
                        current_pressure = None
                elif current_pressure == -1:
                    if row_tuple.ball_y > 0:
                        current_pressure = None
        else:
            current_pressure = None

        pressures[row_tuple.Index] = current_pressure

    _df['pressures'] = pd.Series(pressures, dtype='Int8')

    print("hi")
