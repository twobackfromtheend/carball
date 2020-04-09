import numpy as np
import pandas as pd

from api.events.events_pb2 import Events
from api.game.game_pb2 import Game
from carball.analysis2.constants.constants import FIELD_Y_THIRD
from carball.output_generation.data_frame_generation.prefixes import DF_GAME_PREFIX, DF_BALL_PREFIX


def calculate_pressures(events: Events, game: Game, df: pd.DataFrame):
    ball_y = df[(DF_BALL_PREFIX, 'pos_y')].rename('ball_y')
    goal_number = df[(DF_GAME_PREFIX, 'goal_number')].rename('goal_number')
    previous_goal_number = goal_number.shift(1).rename('previous_goal_number')

    def add_pressure(start_frame: int, end_frame: int, team_is_orange: bool, goal_number: int):
        pressure = events.pressures.add()
        pressure.start_frame_number = start_frame
        pressure.end_frame_number = end_frame
        pressure.is_orange = team_is_orange
        pressure.goal_number = goal_number

    current_pressure = None
    pressure_start_frame = None
    _df = pd.concat([ball_y, goal_number, previous_goal_number], axis=1)
    for row_tuple in _df.itertuples():
        frame = row_tuple.Index
        goal_number = row_tuple.goal_number
        previous_goal_number = row_tuple.previous_goal_number
        if not pd.isna(goal_number) and goal_number == previous_goal_number:
            if current_pressure is None:
                if row_tuple.ball_y > FIELD_Y_THIRD:
                    current_pressure = False
                    pressure_start_frame = frame
                elif row_tuple.ball_y < -FIELD_Y_THIRD:
                    current_pressure = True
                    pressure_start_frame = frame
            else:
                if current_pressure is False:
                    if row_tuple.ball_y < 0:
                        add_pressure(pressure_start_frame, frame, current_pressure, previous_goal_number)
                        current_pressure = None
                elif current_pressure is True:
                    if row_tuple.ball_y > 0:
                        add_pressure(pressure_start_frame, frame, current_pressure, previous_goal_number)
                        current_pressure = None
        else:
            if current_pressure is not None:
                add_pressure(pressure_start_frame, frame, current_pressure, previous_goal_number)
                current_pressure = None

    previous_pressure = None
    for pressure in events.pressures:
        pressure_df = df.loc[pressure.start_frame_number:pressure.end_frame_number]

        pressure.duration = pressure_df.loc[:, (DF_GAME_PREFIX, 'delta')].sum()
        if previous_pressure is not None and pressure.goal_number == previous_pressure.goal_number:
            pressure.time_since_last_pressure = df.loc[
                                                previous_pressure.end_frame_number:pressure.start_frame_number,
                                                (DF_GAME_PREFIX, 'delta')
                                                ].sum()
            pressure.previous_pressure_is_orange = previous_pressure.is_orange
        # Add player pressure stats
        player_pressure_stats_dict = {}
        for player in game.players:
            player_id = player.id.id
            player_name = player.name
            player_pressure_stats = pressure.player_stats.add()
            player_pressure_stats.player_id.id = player_id

            player_pressure_stats_dict[player_id] = player_pressure_stats

            player_boost_diff = pressure_df.loc[:, (player_name, 'boost')].diff()
            player_pressure_stats.boost_used = abs(player_boost_diff[player_boost_diff < 0].sum())

            player_speed = ((pressure_df.loc[:, (player_name, ['vel_x', 'vel_y', 'vel_z'])] ** 2).sum(axis=1) ** 0.5)
            player_pressure_stats.average_speed = player_speed.values.mean()

        for hit in events.hits:
            if pressure.start_frame_number <= hit.frame_number <= pressure.end_frame_number:
                hit_player_id = hit.player_id.id
                hit_player_pressure_stats = player_pressure_stats_dict[hit_player_id]
                hit_player_pressure_stats.hits += 1
                if hit.goal:
                    hit_player_pressure_stats.goal = True
                if hit.assist:
                    hit_player_pressure_stats.assist = True
                if hit.shot:
                    hit_player_pressure_stats.shots += 1
                if hit.save:
                    hit_player_pressure_stats.saves += 1
                if hit.pass_:
                    hit_player_pressure_stats.passes += 1
                if hit.dribble:
                    hit_player_pressure_stats.dribbles += 1

        previous_pressure = pressure
    # pressure_frames = []
    # previous_pressure = None
    # pressure_start_frame = None
    # for row in pressures_series.iteritems():
    #     print(row)
    # pressure_durations = [pressure.duration for pressure in events.pressures]
    # print("hi")
