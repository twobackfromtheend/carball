import pandas as pd

from carball.json_parser.game import Game as JsonParserGame
from carball.output_generation.data_frame_generation.checks import check_value_ranges, check_columns
from carball.output_generation.data_frame_generation.additional_columns import add_team_score_to_df, \
    add_goal_number_to_df

DF_GAME_PREFIX = "game__"
DF_BALL_PREFIX = "ball__"


def create_data_frame(json_parser_game: JsonParserGame) -> pd.DataFrame:
    data_dict = {player.name: player.data for player in json_parser_game.players}

    data_dict[DF_BALL_PREFIX] = json_parser_game.ball
    initial_df = pd.concat(data_dict, axis=1)

    df = pd.concat([initial_df, json_parser_game.frames], axis=1)
    cols = []
    for c in df.columns.values:
        if isinstance(c, str):
            cols.append((DF_GAME_PREFIX, c))
        else:
            cols.append(c)
    df.columns = pd.MultiIndex.from_tuples(cols)

    add_team_score_to_df(df, json_parser_game)
    add_goal_number_to_df(df, json_parser_game)

    check_columns(df)
    check_value_ranges(df)
    return df
