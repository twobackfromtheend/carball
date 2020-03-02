import pandas as pd

from api.analysis.ball_stats_pb2 import BallStats
from carball.analysis2.data_frame_filters.data_frame_filters import sum_delta, get_high_in_air, get_in_air, \
    get_on_ground, get_attacking_half, get_defending_half, get_attacking_third, get_neutral_third, get_defending_third
from carball.output_generation.data_frame_generation.prefixes import DF_BALL_PREFIX


def set_ball_stats(ball_stats: BallStats, data_frame: pd.DataFrame):
    ball_df = data_frame.loc[:, DF_BALL_PREFIX]

    ball_stats.time_high_in_air = sum_delta(data_frame[get_high_in_air(ball_df)])
    ball_stats.time_in_air = sum_delta(data_frame[get_in_air(ball_df)])
    ball_stats.time_on_ground = sum_delta(data_frame[get_on_ground(ball_df)])
    ball_stats.time_in_orange_half = sum_delta(data_frame[get_attacking_half(ball_df)])
    ball_stats.time_in_blue_half = sum_delta(data_frame[get_defending_half(ball_df)])
    ball_stats.time_in_orange_third = sum_delta(data_frame[get_attacking_third(ball_df)])
    ball_stats.time_in_neutral_third = sum_delta(data_frame[get_neutral_third(ball_df)])
    ball_stats.time_in_blue_third = sum_delta(data_frame[get_defending_third(ball_df)])
