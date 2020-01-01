import logging
from math import pi

import numpy as np
import pandas as pd

from carball.output_generation.data_frame_generation.prefixes import DF_GAME_PREFIX, DF_BALL_PREFIX

logger = logging.getLogger(__name__)


def check_columns(df: pd.DataFrame):
    player_names = set(df.columns.levels[0].tolist())
    player_names.remove(DF_GAME_PREFIX)
    player_names.remove(DF_BALL_PREFIX)

    required_player_columns = [
        'pos_x', 'pos_y', 'pos_z',
        'vel_x', 'vel_y', 'vel_z',
        'rot_x', 'rot_y', 'rot_z',
        'ang_vel_x', 'ang_vel_y', 'ang_vel_z',
        'throttle', 'steer', 'handbrake', 'ball_cam',
        'boost',
        'boost_active', 'jump_active', 'dodge_active', 'double_jump_active',
        'boost_collect',
        'ping'
    ]

    for player_name in player_names:
        player_df = df[player_name]
        player_df_columns = player_df.columns.tolist()
        missing_columns = [column for column in required_player_columns if column not in player_df_columns]
        try:
            assert len(missing_columns) == 0
        except AssertionError:
            logger.error(
                f"Missing columns for {player_name}:",
                missing_columns
            )
            for column in missing_columns:
                df[(player_name, column)] = np.nan


def check_value_ranges(df: pd.DataFrame):
    # Check values are normalised properly
    player_names = set(df.columns.levels[0].tolist())
    player_names.remove(DF_GAME_PREFIX)
    player_names.remove(DF_BALL_PREFIX)

    # Position
    pos_limits = [
        ('pos_x', (-4102, 4102)),
        ('pos_y', (-6200, 6200)),  # Addition over 5120 to account for goal depth
        ('pos_z', (0, 2044))
    ]
    for pos_name, limits in pos_limits:
        pos_df = df.loc[:, (slice(None), pos_name)].fillna(0)
        try:
            assert ((limits[0] <= pos_df) & (pos_df <= limits[1])).all(axis=None)
        except AssertionError:
            logger.error(
                f"Assertion failed: {pos_name}\n"
                f"\tLimits: {limits}\n"
                f"\tRange: \n{pos_df.min()}, \n{pos_df.max()}\n"
            )

    # Rotation
    rot_limits = [
        ('rot_x', (-pi / 2, pi / 2)),
        ('rot_y', (-pi, pi)),
        ('rot_z', (-pi, pi)),
    ]
    for rot_name, limits in rot_limits:
        rot_df = df.loc[:, (slice(None), rot_name)].fillna(0)
        assert ((limits[0] <= rot_df) & (rot_df <= limits[1])).all(axis=None)

    # Velocity
    for player_name in player_names:
        player_vel_df = df.loc[:, (player_name, ['vel_x', 'vel_y', 'vel_z'])].fillna(0)
        player_speed = (player_vel_df ** 2).sum(axis=1) ** 0.5
        assert (player_speed <= 2300 + 1e-2).all()  # 2300 technically the limit, account for rounding errors

    ball_vel_df = df.loc[:, (DF_BALL_PREFIX, ['vel_x', 'vel_y', 'vel_z'])].fillna(0)
    ball_speed = (ball_vel_df ** 2).sum(axis=1) ** 0.5
    assert (ball_speed <= 6000 + 1e-3).all()

    # Angular velocity
    for player_name in player_names:
        ang_vel_df = df.loc[:, (player_name, ['ang_vel_x', 'ang_vel_y', 'ang_vel_z'])].fillna(0)
        assert ((-5.5 <= ang_vel_df) & (ang_vel_df <= 5.5)).all(axis=None)

        ang_speed = (ang_vel_df ** 2).sum(axis=1) ** 0.5
        assert (ang_speed < 5.5 + 1e-3).all()

    ball_ang_vel_df = df.loc[:, (DF_BALL_PREFIX, ['ang_vel_x', 'ang_vel_y', 'ang_vel_z'])].fillna(0)
    assert ((-6 <= ball_ang_vel_df) & (ball_ang_vel_df <= 6)).all(axis=None)
    ball_ang_speed = (ball_ang_vel_df ** 2).sum(axis=1) ** 0.5
    assert (ball_ang_speed < 6 + 1e-3).all()

    # boost
    boost_df = df.loc[:, (slice(None), 'boost')].fillna(0)
    assert ((0 <= boost_df) & (boost_df <= 100)).all(axis=None)

    return df
