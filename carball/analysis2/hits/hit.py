import logging
from typing import List, Dict

import numpy as np
import pandas as pd
from rlutilities.linear_algebra import vec3
from rlutilities.simulation import Ball, Game as RLUGame

from api.events.events_pb2 import Events
from api.game.game_pb2 import Game
from carball.output_generation.data_frame_generation.prefixes import DF_GAME_PREFIX, DF_BALL_PREFIX

logger = logging.getLogger(__name__)


def get_hits(events: Events, game: Game, df: pd.DataFrame):
    hit_frame_numbers = get_hit_frame_numbers(df)
    player_names = [player.name for player in game.players]
    hit_frames_df = df.loc[hit_frame_numbers, :]
    ball_df = hit_frames_df[DF_BALL_PREFIX].loc[:, ['pos_x', 'pos_y', 'pos_z']]
    player_distances = {}
    for player_name in player_names:
        player_df = hit_frames_df[player_name].loc[:, ['pos_x', 'pos_y', 'pos_z']]
        player_distance = (((player_df - ball_df) ** 2).sum(axis=1, skipna=False) ** 0.5).rename(player_name)
        player_distances[player_name] = player_distance
    player_distances_df = pd.DataFrame.from_dict(player_distances)

    player_name_to_team: Dict[str, int] = {player.name: int(player.is_orange) for player in
                                           game.players}
    columns = [(player_name_to_team[player_name], player_name)
               for player_name in player_distances_df.columns]
    player_distances_df.columns = pd.MultiIndex.from_tuples(columns)

    player_distances_df[('closest_player', 'name')] = None

    for hit_team_no in [0, 1]:
        try:
            player_distances_for_team = player_distances_df[hit_team_no].loc[
                df[(DF_BALL_PREFIX, 'hit_team_no')] == hit_team_no]

            small_player_distances_for_team = player_distances_for_team[(player_distances_for_team < 350).any(axis=1)]

            player_distances_df[('closest_player', 'name')].fillna(
                small_player_distances_for_team.idxmin(axis=1),
                inplace=True
            )
        except KeyError as e:
            if e.args[0] == hit_team_no:
                logger.warning(f"Team {hit_team_no} did not hit the ball")
            else:
                raise e

    hits_data = player_distances_df['closest_player'].dropna()
    # dropped_frames = [frame for frame in player_distances_df.index if frame not in hits_data.index]
    # print("dropped", dropped_frames)
    player_name_to_id: Dict[str, str] = {player.name: player.id.id for player in game.players}
    goal_numbers = df.loc[hits_data.index, (DF_GAME_PREFIX, 'goal_number')].to_dict()

    previous_hit = None
    for frame_number, player_name in hits_data.name.iteritems():
        goal_number = goal_numbers[frame_number]
        if pd.isna(goal_number):
            continue
        hit = events.hits.add()
        hit.frame_number = frame_number
        hit.player_id.id = player_name_to_id[player_name]
        hit.goal_number = goal_number
        if previous_hit is not None:
            if previous_hit.goal_number == hit.goal_number:
                previous_hit.next_hit_frame_number = frame_number
                hit.previous_hit_frame_number = previous_hit.frame_number
        previous_hit = hit


def get_hit_frame_numbers(df: pd.DataFrame):
    ball_df = df[DF_BALL_PREFIX]

    hit_frame_numbers = get_hit_frame_numbers_by_ball_ang_vel(df)
    # Filter by hit_team_no
    hit_frame_numbers = ball_df.loc[hit_frame_numbers].index[
        ~ball_df.loc[hit_frame_numbers, "hit_team_no"].isna()].tolist()
    logger.info(f"hit: {hit_frame_numbers}")

    delta_df = df.loc[:, (DF_GAME_PREFIX, 'delta')]
    RLUGame.set_mode("soccar")
    filtered_hit_frame_numbers = []
    for frame_number in hit_frame_numbers:
        previous_frame_number = frame_number - 1
        ball_previous_frame = ball_df.loc[previous_frame_number, :]
        initial_ang_vel = ball_previous_frame.loc[['ang_vel_x', 'ang_vel_y', 'ang_vel_z']].values

        ball = Ball()
        # noinspection PyPropertyAccess
        ball.location = vec3(*ball_previous_frame.loc[['pos_x', 'pos_y', 'pos_z']])
        # noinspection PyPropertyAccess
        ball.velocity = vec3(*ball_previous_frame.loc[['vel_x', 'vel_y', 'vel_z']])
        # noinspection PyPropertyAccess
        ball.angular_velocity = vec3(*initial_ang_vel)

        frame_delta = delta_df[frame_number]
        delta_simulated = 0
        while delta_simulated < frame_delta:
            dt = 1 / 120
            time_to_simulate = min(dt, frame_delta - delta_simulated)
            ball.step(time_to_simulate)
            delta_simulated += time_to_simulate

        simulated_ball_ang_vel = np.array([ball.angular_velocity[0],
                                           ball.angular_velocity[1],
                                           ball.angular_velocity[2]])
        actual_ball_ang_vel = ball_df.loc[frame_number, ['ang_vel_x', 'ang_vel_y', 'ang_vel_z']].values
        actual_ang_vel_change = ((actual_ball_ang_vel - initial_ang_vel) ** 2).sum() ** 0.5
        end_ang_vel_difference = ((simulated_ball_ang_vel - actual_ball_ang_vel) ** 2).sum() ** 0.5

        relative_ang_vel_difference = end_ang_vel_difference / actual_ang_vel_change
        if relative_ang_vel_difference > 0.8:
            filtered_hit_frame_numbers.append(frame_number)
    return filtered_hit_frame_numbers


def get_hit_frame_numbers_by_ball_ang_vel(data_frame: pd.DataFrame) -> List[int]:
    ball_ang_vels = data_frame.loc[:, (DF_BALL_PREFIX, ['ang_vel_x', 'ang_vel_y', 'ang_vel_z'])]
    diff_series = ball_ang_vels.diff().any(axis=1)  # Does not include where changing to or from NaN
    indices = diff_series.index[diff_series].tolist()
    return indices
