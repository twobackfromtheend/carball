import numpy as np
import pandas as pd

from carball.analysis2.constants.constants import FIELD_X_LIM, FIELD_Y_LIM, FIELD_Y_THIRD, GOAL_HEIGHT
from carball.output_generation.data_frame_generation.prefixes import DF_GAME_PREFIX


def get_flipped_data_frame(data_frame: pd.DataFrame):
    df = data_frame.copy()
    df.loc[:, (slice(None), 'pos_y')] *= -1
    df.loc[:, (slice(None), 'vel_y')] *= -1

    # No need to modify yaw as it's not used anywhere, but this is what should be done.
    # df.loc[:, (slice(None), 'rot_y')] += np.pi
    # df.loc[df.loc[:, (slice(None), 'rot_y')] > np.pi, (slice(None), 'rot_y')] -= 2 * np.pi
    # And ang_vel_y
    return df


def sum_delta(data_frame: pd.DataFrame):
    return data_frame.loc[:, (DF_GAME_PREFIX, 'delta')].sum()


def get_attacking_half(data_frame: pd.DataFrame):
    return data_frame.pos_y > 0


def get_defending_half(data_frame: pd.DataFrame):
    return data_frame.pos_y < 0


def get_attacking_third(data_frame: pd.DataFrame):
    return data_frame.pos_y > FIELD_Y_THIRD


def get_neutral_third(data_frame: pd.DataFrame):
    return data_frame.pos_y.abs() < FIELD_Y_THIRD


def get_defending_third(data_frame: pd.DataFrame):
    return data_frame.pos_y < -FIELD_Y_THIRD


def get_on_ground(data_frame: pd.DataFrame, buffer: float = 150):
    return data_frame.pos_z < buffer


def get_in_air(data_frame: pd.DataFrame, buffer: float = 100):
    return ~get_near_surface(data_frame, buffer)


def get_high_in_air(data_frame: pd.DataFrame, buffer: float = 100):
    return ~get_near_surface(data_frame, buffer) & (data_frame.pos_z > GOAL_HEIGHT + buffer)


def get_near_surface(data_frame: pd.DataFrame, buffer: float = 100):
    return (data_frame.pos_z > 150) \
           & (np.abs(data_frame.pos_x) > FIELD_X_LIM - buffer) \
           & (np.abs(data_frame.pos_y) > FIELD_Y_LIM - buffer)
