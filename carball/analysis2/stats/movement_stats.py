from typing import Dict

import pandas as pd

from api.analysis.stats_pb2 import PlayerStats
from api.game.game_pb2 import Game
from carball.analysis2.data_frame_filters.data_frame_filters import sum_delta
from carball.output_generation.data_frame_generation.prefixes import DF_GAME_PREFIX


def set_movement_stats(player_stats: Dict[str, PlayerStats], player_blue_data_frames: Dict[str, pd.DataFrame],
                       game: Game):
    player_id_to_name: Dict[str, str] = {player.id.id: player.name for player in game.players}

    for player_id, blue_df in player_blue_data_frames.items():
        player_name = player_id_to_name[player_id]
        _player_stats = player_stats[player_id]
        player_df = player_blue_data_frames[player_id].loc[:, player_name]

        player_distance_moved = (player_df.loc[:, ['pos_x', 'pos_y', 'pos_z']].diff() ** 2).sum(axis=1) ** 0.5
        _player_stats.distance_travelled = (player_distance_moved[player_distance_moved < 500]).sum()
        # Clip to max of 500 to limit effect of "usage" detected due to teleportation after demo and at kickoff
        # Histogram plot shows cutoff at around 250.
        player_speed = (player_df.loc[:, ['vel_x', 'vel_y', 'vel_z']] ** 2).sum(axis=1) ** 0.5
        _player_stats.average_speed = \
            (player_speed * blue_df.loc[:, (DF_GAME_PREFIX, 'delta')]).sum() / _player_stats.time_in_game

        _player_stats.time_at_supersonic = sum_delta(blue_df[player_speed > 2200])
        _player_stats.time_at_boost_speed = sum_delta(blue_df[player_speed > 1450])
        _player_stats.time_at_slow_speed = sum_delta(blue_df[player_speed < 700])
