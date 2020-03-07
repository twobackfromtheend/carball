import numpy as np
import pandas as pd

from carball.json_parser.game import Game as JsonParserGame


def add_team_score_to_df(df: pd.DataFrame, json_parser_game: JsonParserGame):
    df[('game__', 'team_0_score')] = 0
    df[('game__', 'team_1_score')] = 0

    for goal in json_parser_game.goals:
        df.loc[goal.frame_number:, ('game__', f'team_{goal.player_team}_score')] += 1


def add_goal_number_to_df(df: pd.DataFrame, json_parser_game: JsonParserGame):
    ball_has_been_hit = df.game__.ball_has_been_hit
    last_frame_ball_has_been_hit = ball_has_been_hit.shift(1).rename('last_ball_has_been_hit')
    first_hit_frames = ball_has_been_hit.index[
        (ball_has_been_hit == True) & (last_frame_ball_has_been_hit != True)
        ].tolist()
    df[('game__', 'goal_number')] = np.nan
    df[('game__', 'goal_number')] = df[('game__', 'goal_number')].astype('Int8')
    for i, first_hit_frame in enumerate(first_hit_frames):
        try:
            goal = json_parser_game.goals[i]
        except IndexError:
            df.loc[first_hit_frame:, ('game__', 'goal_number')] = -1
            break
        df.loc[first_hit_frame:goal.frame_number, ('game__', 'goal_number')] = i
