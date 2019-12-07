from typing import Dict

import pandas as pd

from api.analysis.stats_pb2 import PlayerStats
from api.game.game_pb2 import Game
from carball.analysis2.data_frame_filters.data_frame_filters import get_attacking_third, \
    sum_delta
from carball.output_generation.data_frame_generation.prefixes import DF_GAME_PREFIX


def set_boost_stats(player_stats: Dict[str, PlayerStats], player_blue_data_frames: Dict[str, pd.DataFrame], game: Game):
    player_id_to_name: Dict[str, str] = {player.id.id: player.name for player in game.players}

    for player_id, blue_df in player_blue_data_frames.items():
        player_name = player_id_to_name[player_id]
        _player_stats = player_stats[player_id]
        player_df = player_blue_data_frames[player_id].loc[:, player_name]

        _player_stats.big_pads_collected = (player_df.boost_collect == True).sum()
        _player_stats.small_pads_collected = (player_df.boost_collect == False).sum()
        _player_stats.stolen_boosts = ((player_df.boost_collect == True) & get_attacking_third(player_df)).sum()

        boost_change = player_df.boost.diff()
        _player_stats.boost_used = boost_change[(-5 < boost_change) & (boost_change < 0)].abs().sum()
        # Clip to max of 5 to limit effect of "usage" detected due to boost amount reset at kickoff

        _player_stats.time_full_boost = sum_delta(blue_df[player_df.boost > 99])
        _player_stats.time_high_boost = sum_delta(blue_df[player_df.boost > 70])
        _player_stats.time_low_boost = sum_delta(blue_df[player_df.boost < 25])
        _player_stats.time_no_boost = sum_delta(blue_df[player_df.boost < 1])

        _player_stats.time_in_game = (blue_df.loc[:, (DF_GAME_PREFIX, 'delta')] * ~player_df.is_demolished).sum()
        _player_stats.average_boost_level = \
            (player_df.boost * blue_df.loc[:, (DF_GAME_PREFIX, 'delta')]).sum() / _player_stats.time_in_game
