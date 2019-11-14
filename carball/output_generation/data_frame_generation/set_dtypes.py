import logging

import pandas as pd

logger = logging.getLogger(__name__)

DTYPES = {
    # Player and Ball columns
    'pos_x': 'float32',
    'pos_y': 'float32',
    'pos_z': 'float32',
    'vel_x': 'float32',
    'vel_y': 'float32',
    'vel_z': 'float32',
    'rot_x': 'float16',
    'rot_y': 'float16',
    'rot_z': 'float16',
    'ang_vel_x': 'float16',
    'ang_vel_y': 'float16',
    'ang_vel_z': 'float16',

    # Player columns
    'boost': 'float16',  # 0-100
    'ping': 'UInt16',
    'throttle': 'UInt8',  # 0-255
    'steer': 'UInt8',  # 0-255
    'handbrake': 'UInt8',  # Nullable boolean
    'ball_cam': 'UInt8',  # Nullable boolean
    'boost_active': 'UInt8',  # Nullable boolean
    'boost_collect': 'UInt8',  # Nullable boolean
    'jump_active': 'UInt16',  # Incremental counter (True when odd)
    'double_jump_active': 'UInt16',  # Incremental counter (True when odd)
    'dodge_active': 'UInt16',  # Incremental counter (True when odd)

    # Game columns
    'time': 'float32',
    'delta': 'float32',
    'seconds_remaining': 'UInt16',  # 0-300 Game clock
    'replicated_seconds_remaining': 'UInt8',  # 0-3 Kickoff countdown
    'is_overtime': 'UInt8',  # Nullable boolean
    'ball_has_been_hit': 'UInt8',  # Nullable boolean

    # Ball columns
    'hit_team_no': 'UInt8',  # Nullable 0 or 1 (for blue or orange respectively)

    # Added columns
    'team_0_score': 'Int8',
    'team_1_score': 'Int8',

    'goal_number': 'UInt8',
    # 0-(N-1) for N goals scored, -1 after last kickoff if no goal at the end, nan before first touches

    'is_demolished': 'bool'  # Boolean
}


def set_dtypes(df: pd.DataFrame):
    original_memory_usage = df.memory_usage()

    # pd.concat([df.min(), df.max(), df.isna().any()], axis=1) to check range and presence of nulls

    for column in df.columns:
        second_level_index = column[1]
        new_dtype = DTYPES[second_level_index]
        try:
            if new_dtype == 'UInt8':
                # Handle conversion of nullable booleans to int
                df[column] = (df[column] * 1).astype(new_dtype)
            elif new_dtype == 'UInt16':
                # Handle conversion of nullable counters to int
                df[column] = (df[column] * 1).astype(new_dtype)
            else:
                df[column] = df[column].astype(new_dtype)
        except TypeError as e:
            logging.error(f"Could not set column {column} to dtype {new_dtype}: {e}")

    updated_memory_usage = df.memory_usage()

    logger.info(
        f"Updated dtypes. "
        f"Memory usage previously was {original_memory_usage.sum(axis=None)}, "
        f"now is {updated_memory_usage.sum(axis=None)} "
        f"({updated_memory_usage.sum(axis=None) / original_memory_usage.sum(axis=None) * 100:.2f}%)."
    )
