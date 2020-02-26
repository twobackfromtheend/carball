import logging

import numpy as np
import pandas as pd

from carball.json_parser.game import Game as JsonParserGame
from carball.output_generation.data_frame_generation.prefixes import DF_GAME_PREFIX
from carball.output_generation.field_constants import get_boost_collect_is_big_boost

BOOST_PER_SECOND = 80 * 1 / .93 * 100 / 255  # boost used per second out of 100

logger = logging.getLogger(__name__)


def add_boost_to_df(df: pd.DataFrame, json_parser_game: JsonParserGame):
    player_names = [player.name for player in json_parser_game.players]

    for player_name in player_names:
        boost_temp_series = df[(player_name, 'boost_temp')]
        updated_boost_values = boost_temp_series[boost_temp_series.diff() != 0]
        frame_deltas = df[(DF_GAME_PREFIX, 'delta')]
        df[(player_name, 'boost')] = updated_boost_values
        boost_dict = updated_boost_values.to_dict()

        boost_active = df[(player_name, 'boost_active')].to_dict()
        for boost_tuple in boost_active.items():
            frame_number, boost_is_active = boost_tuple
            previous_frame_boost = boost_dict.get(frame_number - 1, np.nan)

            if frame_number not in boost_dict:
                boost_active_on_frame = boost_active.get(frame_number, False)
                if boost_active_on_frame:
                    frame_delta = frame_deltas.loc[frame_number]
                    boost_dict[frame_number] = max(0, previous_frame_boost - frame_delta * BOOST_PER_SECOND)
                else:
                    boost_dict[frame_number] = previous_frame_boost
        df[(player_name, 'boost')] = pd.Series(boost_dict).sort_index()


def add_boost_collect_to_df(df: pd.DataFrame, json_parser_game: JsonParserGame):
    player_names = [player.name for player in json_parser_game.players]

    for player_name in player_names:
        df[(player_name, 'boost_collect')] = np.nan
        player_boost_series = df[(player_name, 'boost')].fillna(0)
        player_boost_collect_frames = df.loc[
            ~df[(player_name, 'potential_boost_collect')].isna(),
            (player_name, 'potential_boost_collect')
        ]

        for boost_collect_tuple in player_boost_collect_frames.astype(int).iteritems():
            frame_number, boost_pad_id = boost_collect_tuple
            player_position = df.loc[frame_number, (player_name, ['pos_x', 'pos_y', 'pos_z'])].values.astype(np.float64)

            current_frame_boost = player_boost_series.loc[frame_number]
            previous_frame_number = frame_number - 1
            if previous_frame_number not in player_boost_series.index:
                logger.warning(f"Skipping possible boost collection on frame {frame_number} "
                               f"as previous frame not in index.")
                continue
            previous_frame_boost = player_boost_series.loc[previous_frame_number]
            previous_frame_boost_active = df.loc[previous_frame_number, (player_name, 'boost_active')]
            if (current_frame_boost > previous_frame_boost) or \
                    (current_frame_boost == 100 and previous_frame_boost == 100 and previous_frame_boost_active):
                try:
                    boost_collect_is_big_boost = get_boost_collect_is_big_boost(player_position, boost_pad_id)
                except ValueError as e:
                    logger.warning(f"Boost error for player {player_name} on frame {frame_number}: {e}")
                    continue
                df.loc[frame_number, (player_name, 'boost_collect')] = boost_collect_is_big_boost
            else:
                # Ghost pickup
                pass


def add_team_score_to_df(df: pd.DataFrame, json_parser_game: JsonParserGame):
    df[(DF_GAME_PREFIX, 'team_0_score')] = 0
    df[(DF_GAME_PREFIX, 'team_1_score')] = 0

    for goal in json_parser_game.goals:
        df.loc[goal.frame_number:, (DF_GAME_PREFIX, f'team_{goal.player_team}_score')] += 1


def add_goal_number_to_df(df: pd.DataFrame, json_parser_game: JsonParserGame):
    ball_has_been_hit = df[(DF_GAME_PREFIX, 'ball_has_been_hit')]
    last_frame_ball_has_been_hit = ball_has_been_hit.shift(1).rename('last_ball_has_been_hit')
    first_hit_frames = ball_has_been_hit.index[
        (ball_has_been_hit == True) & (last_frame_ball_has_been_hit != True)
        ].tolist()
    df[(DF_GAME_PREFIX, 'goal_number')] = np.nan
    df[(DF_GAME_PREFIX, 'goal_number')] = df[(DF_GAME_PREFIX, 'goal_number')].astype('Int8')
    for i, first_hit_frame in enumerate(first_hit_frames):
        try:
            goal = json_parser_game.goals[i]
        except IndexError:
            df.loc[first_hit_frame:, (DF_GAME_PREFIX, 'goal_number')] = -1
            break
        df.loc[first_hit_frame:goal.frame_number, (DF_GAME_PREFIX, 'goal_number')] = i


def add_player_is_demolished_to_df(df: pd.DataFrame, json_parser_game: JsonParserGame):
    player_names = [player.name for player in json_parser_game.players]
    player_columns = [
        f'pos_x',
        f'pos_y',
        f'pos_z',
        f'vel_x',
        f'vel_y',
        f'vel_z',
        f'pitch',
        f'yaw',
        f'roll',
        f'ang_vel_x',
        f'ang_vel_y',
        f'ang_vel_z',
    ]
    goal_number_not_nan = ~df[(DF_GAME_PREFIX, 'goal_number')].isna()
    for player_name in player_names:
        player_is_demoed = df.loc[:, (player_name, player_columns)].isna().all(axis=1)
        df[(player_name, 'is_demolished')] = (player_is_demoed & goal_number_not_nan)
