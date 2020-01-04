from typing import Dict

import pandas as pd

from api.events.hit_pb2 import Hit
from carball.analysis2.data_frame_filters.data_frame_filters import get_high_in_air, get_near_surface
from carball.output_generation.data_frame_generation.prefixes import DF_BALL_PREFIX


def set_aerials_and_wall_hits(hits_by_goal_number: Dict[int, Hit], df: pd.DataFrame):
    ball_df = df[DF_BALL_PREFIX]

    for hits_list in hits_by_goal_number.values():
        for hit in hits_list:
            ball_data = ball_df.loc[hit.frame_number]

            if get_high_in_air(ball_data):
                hit.aerial = True
            if get_near_surface(ball_data):
                hit.wall_hit = True
