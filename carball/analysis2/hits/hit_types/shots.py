from typing import Dict

import pandas as pd
from rlutilities.linear_algebra import vec3
from rlutilities.simulation import Ball

from api.events.hit_pb2 import Hit
from api.game.game_pb2 import Game
from carball.analysis2.constants.constants import FIELD_Y_LIM
from carball.output_generation.data_frame_generation.prefixes import DF_BALL_PREFIX

SHOT_SECONDS_SIMULATED = 5


def set_shots(hits_by_goal_number: Dict[int, Hit], game: Game, df: pd.DataFrame):
    ball_df = df[DF_BALL_PREFIX]
    player_id_to_team = {player.id.id: player.is_orange for player in game.players}

    for hits_list in hits_by_goal_number.values():
        for hit in hits_list:
            direction_factor = -1 ** player_id_to_team[hit.player_id.id]  # -1 if orange, 1 if blue
            ball_data = ball_df.loc[hit.frame_number]

            ball = Ball()
            # noinspection PyPropertyAccess
            ball_location = ball_data.loc[['pos_x', 'pos_y', 'pos_z']]
            ball.location = vec3(*ball_location)
            # noinspection PyPropertyAccess
            ball_velocity = ball_data.loc[['vel_x', 'vel_y', 'vel_z']]
            ball.velocity = vec3(*ball_velocity)
            # noinspection PyPropertyAccess
            ball_angular_velocity = ball_data.loc[['ang_vel_x', 'ang_vel_y', 'ang_vel_z']]
            ball.angular_velocity = vec3(*ball_angular_velocity)

            delta_simulated = 0
            while delta_simulated < SHOT_SECONDS_SIMULATED:
                dt = 1 / 120
                ball.step(min(dt, SHOT_SECONDS_SIMULATED - delta_simulated))
                delta_simulated += dt

                ball_y = ball.location[1]
                if ball_y * direction_factor > FIELD_Y_LIM:
                    hit.shot = True
                    break

