from typing import Dict

import pandas as pd

from api.analysis.stats_pb2 import PlayerStats
from api.game.game_pb2 import Game
from carball.analysis2.data_frame_filters.data_frame_filters import sum_delta, get_high_in_air, get_in_air, \
    get_on_ground, get_attacking_half, get_defending_half, get_attacking_third, get_neutral_third, get_defending_third


def set_positioning_stats(player_stats: Dict[str, PlayerStats], player_blue_data_frames: Dict[str, pd.DataFrame],
                          game: Game):
    player_id_to_name: Dict[str, str] = {player.id.id: player.name for player in game.players}

    for player_id, blue_df in player_blue_data_frames.items():
        player_name = player_id_to_name[player_id]
        _player_stats = player_stats[player_id]
        player_df = player_blue_data_frames[player_id].loc[:, player_name]

        _player_stats.time_high_in_air = sum_delta(blue_df[get_high_in_air(player_df)])
        _player_stats.time_in_air = sum_delta(blue_df[get_in_air(player_df)])
        _player_stats.time_on_ground = sum_delta(blue_df[get_on_ground(player_df)])

        _player_stats.time_in_attacking_half = sum_delta(blue_df[get_attacking_half(player_df)])
        _player_stats.time_in_defending_half = sum_delta(blue_df[get_defending_half(player_df)])
        _player_stats.time_in_attacking_third = sum_delta(blue_df[get_attacking_third(player_df)])
        _player_stats.time_in_neutral_third = sum_delta(blue_df[get_neutral_third(player_df)])
        _player_stats.time_in_defending_third = sum_delta(blue_df[get_defending_third(player_df)])

    player_name_to_id: Dict[str, str] = {player.name: player.id.id for player in game.players}

    player_names_by_team = [[], []]
    for player in game.players:
        player_names_by_team[player.is_orange].append(player.name)
    for team_is_orange in [False, True]:
        player_names = player_names_by_team[team_is_orange]
        first_player_id = player_name_to_id[player_names[0]]
        blue_df = player_blue_data_frames[first_player_id]
        pos_y_rank = blue_df.loc[:, (player_names_by_team[0], 'pos_y')].rank(axis=1)

        for player_name in player_names:
            player_id = player_name_to_id[player_name]
            _player_stats = player_stats[player_id]
            _player_stats.time_most_back = sum_delta(blue_df.loc[pos_y_rank[player_name, 'pos_y'] == 1])
            _player_stats.time_between_players = sum_delta(blue_df.loc[pos_y_rank[player_name, 'pos_y'] == 2])
            _player_stats.time_most_forward = sum_delta(blue_df.loc[pos_y_rank[player_name, 'pos_y'] == 3])
            # print(player_name)
            # print(_player_stats)
