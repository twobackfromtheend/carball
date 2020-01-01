from collections import defaultdict
from typing import Dict, List

import pandas as pd

from api.events.hit_pb2 import Hit
from api.analysis.stats_pb2 import PlayerStats
from carball.output_generation.data_frame_generation.prefixes import DF_GAME_PREFIX


def set_possession_stats(player_stats: Dict[str, PlayerStats], hits: List[Hit], data_frame: pd.DataFrame):
    delta = data_frame.loc[:, (DF_GAME_PREFIX, 'delta')]
    possession_durations = defaultdict(lambda: 0)
    for hit in hits:
        hit_player_id = hit.player_id.id
        hit_frame_number = hit.frame_number
        next_hit_frame_number = hit.next_hit_frame_number
        if next_hit_frame_number is not None:
            hit_duration = delta.loc[hit_frame_number:next_hit_frame_number].sum()
            possession_durations[hit_player_id] += hit_duration

    for player_id, possession_duration in possession_durations.items():
        _player_stats = player_stats[player_id]
        _player_stats.possession_duration = possession_duration
