from enum import Enum
from typing import Optional

import numpy as np

STANDARD_FIELD_LENGTH_HALF = 5120
STANDARD_FIELD_WIDTH_HALF = 4096
STANDARD_GOAL_WIDTH_HALF = 893

BALL_SIZE = 92.75
HEIGHT_0_BALL_LIM = 95  # Height of ball when on ground
HEIGHT_0_LIM = 20  # Height of car when on ground
HEIGHT_1_LIM = 840  # Goal height

MAP_THIRD = STANDARD_FIELD_LENGTH_HALF * 2 / 6

BIG_BOOSTS = {
    4: np.array([-3072, -4096]),
    5: np.array([3072, -4096]),
    16: np.array([-3584, 0]),
    19: np.array([3584, 0]),
    30: np.array([3072, 4096]),
    31: np.array([-3072, 4096]),
}

BIG_BOOST_RADIUS = 208
BIG_BOOST_HEIGHT = 168

SMALL_BOOSTS = {
    1: np.array([0, -4240]), 2: np.array([-1792, -4184]), 3: np.array([1792, -4184]),
    6: np.array([-940, -3308]), 7: np.array([940, -3308]), 8: np.array([0, -2816]),
    9: np.array([-3584, -2484]), 10: np.array([3584, -2484]), 11: np.array([-1788, -2300]),
    12: np.array([1788, -2300]), 13: np.array([-2048, -1036]), 14: np.array([0, -1024]),
    15: np.array([2048, -1036]), 17: np.array([-1024, 0]), 18: np.array([1024, 0]),
    20: np.array([-2048, 1036]), 21: np.array([0, 1024]), 22: np.array([2048, 1036]),
    23: np.array([-1788, 2300]), 24: np.array([1788, 2300]), 25: np.array([-3584, 2484]),
    26: np.array([3584, 2484]), 27: np.array([0, 2816]), 28: np.array([-940, 3310]),
    29: np.array([940, 3308]), 32: np.array([-1792, 4184]), 33: np.array([1792, 4184]),
    34: np.array([0, 4240])
}

SMALL_BOOST_RADIUS = 144
SMALL_BOOST_HEIGHT = 165


# Boost pad radii above are for moving cars.
# Stationary cars interact with a actual rectangular hitbox of 96uu for small pads, and 160uu for big pads.
# Vertical component for stationary-car-interaction is around 130uu (+- 10)

# https://www.youtube.com/watch?v=xgfa-qZyInw Boostpad hitboxes explained in Rocket Science


def get_boost_collect_is_big_boost_old(position: np.array, boost_pad_id: int) -> bool:
    HORIZONTAL_BUFFER = 100
    VERTICAL_BUFFER = 100

    if boost_pad_id in BIG_BOOSTS:
        horizontal_distance = np.sqrt(((position[:2] - BIG_BOOSTS[boost_pad_id]) ** 2).sum())
        vertical_distance = position[2]
        if horizontal_distance > BIG_BOOST_RADIUS + HORIZONTAL_BUFFER:
            raise ValueError(f"Boost collection happens too far from boost pad: {horizontal_distance:.0f}uu.")
        elif vertical_distance > BIG_BOOST_HEIGHT + VERTICAL_BUFFER:
            raise ValueError(f"Boost collection happens too far from boost pad: {vertical_distance:.0f}uu.")
        return True
    elif boost_pad_id in SMALL_BOOSTS:
        horizontal_distance = np.sqrt(((position[:2] - SMALL_BOOSTS[boost_pad_id]) ** 2).sum())
        vertical_distance = position[2]
        if horizontal_distance > SMALL_BOOST_RADIUS + HORIZONTAL_BUFFER:
            raise ValueError(f"Boost collection happens too far from boost pad: {horizontal_distance:.0f}uu.")
        elif vertical_distance > SMALL_BOOST_HEIGHT + VERTICAL_BUFFER:
            raise ValueError(f"Boost collection happens too far from boost pad: {vertical_distance:.0f}uu.")
        return True
    else:
        pass


BIG_BOOSTS_ARRAY = np.array(list(BIG_BOOSTS.values()))
SMALL_BOOSTS_ARRAY = np.array(list(SMALL_BOOSTS.values()))


def get_boost_collect_is_big_boost(position: np.array, boost_pad_id: int) -> bool:
    HORIZONTAL_BUFFER = 180
    VERTICAL_BUFFER = 100

    position_xy = position[:2]
    big_boost_distances = np.sqrt(((BIG_BOOSTS_ARRAY - position_xy) ** 2).sum(axis=1))
    small_boost_distances = np.sqrt(((SMALL_BOOSTS_ARRAY - position_xy) ** 2).sum(axis=1))

    if big_boost_distances.min() < small_boost_distances.min():
        # Big boost
        horizontal_distance = big_boost_distances.min()
        vertical_distance = position[2]
        if horizontal_distance > BIG_BOOST_RADIUS + HORIZONTAL_BUFFER:
            raise ValueError(f"Boost collection happens too far from big boost pad: {horizontal_distance:.0f}uu (H).")
        elif vertical_distance > BIG_BOOST_HEIGHT + VERTICAL_BUFFER:
            raise ValueError(f"Boost collection happens too far from big boost pad: {vertical_distance:.0f}uu (V).")
        return True
    else:
        # Small boost
        horizontal_distance = small_boost_distances.min()
        vertical_distance = position[2]
        if horizontal_distance > SMALL_BOOST_RADIUS + HORIZONTAL_BUFFER:
            raise ValueError(f"Boost collection happens too far from small boost pad: {horizontal_distance:.0f}uu (H).")
        elif vertical_distance > SMALL_BOOST_HEIGHT + VERTICAL_BUFFER:
            raise ValueError(f"Boost collection happens too far from small boost pad: {vertical_distance:.0f}uu (V).")
        return False
