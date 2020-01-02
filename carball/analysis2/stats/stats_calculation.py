from collections import defaultdict
from typing import List, Counter, Dict

import pandas as pd

from api.analysis.analysis_pb2 import Analysis
from api.events.hit_pb2 import Hit
from api.analysis.stats_pb2 import PlayerStats
from api.events.events_pb2 import Events
from api.game.game_pb2 import Game
from carball.analysis2.data_frame_filters.data_frame_filters import get_flipped_data_frame
from carball.analysis2.stats.boost_stats import set_boost_stats
from carball.analysis2.stats.demo_stats import set_demo_stats
from carball.analysis2.stats.movement_stats import set_movement_stats
from carball.analysis2.stats.positioning_stats import set_positioning_stats
from carball.analysis2.stats.possession_stats import set_possession_stats
from carball.analysis2.timer import timer
from carball.output_generation.data_frame_generation.prefixes import DF_GAME_PREFIX


def calculate_stats(events: Events, game: Game, df: pd.DataFrame):
    hits = events.hits

    analysis = Analysis()
    player_stats: Dict[str, PlayerStats] = {}
    for player in game.players:
        player_id = player.id.id
        _player_stats = analysis.player_stats.add()
        _player_stats.id.id = player_id
        player_stats[player_id] = _player_stats

    with timer("\tCalculating hit counts"):
        set_hit_counts(hits, player_stats)

    active_frames_df = df[~df[(DF_GAME_PREFIX, 'goal_number')].isna()]

    player_blue_data_frames: Dict[str, pd.DataFrame] = {}
    flipped_df = get_flipped_data_frame(active_frames_df)
    for player in game.players:
        player_id = player.id.id
        if player.is_orange:
            player_df = flipped_df
        else:
            player_df = active_frames_df
        player_blue_data_frames[player_id] = player_df

    with timer("\tCalculating boost stats"):
        set_boost_stats(player_stats, player_blue_data_frames, game)
    with timer("\tCalculating movement stats"):
        set_movement_stats(player_stats, player_blue_data_frames, game)
    with timer("\tCalculating positioning stats"):
        set_positioning_stats(player_stats, player_blue_data_frames, game)
    with timer("\tCalculating possession stats"):
        set_possession_stats(player_stats, hits, df)
    with timer("\tCalculating demo stats"):
        set_demo_stats(player_stats, game, player_blue_data_frames)

    for player in game.players:
        player_name = player.name
    return analysis


def set_hit_counts(hits: List[Hit], player_stats: Dict[str, PlayerStats]):
    hit_counter = defaultdict(Counter)
    hit_types = [
        'goal', 'assist', 'save', 'shot', 'secondary_assist', 'pass_', 'passed', 'dribble', 'dribble_continuation',
        'aerial', 'wall_hit'
    ]
    for hit in hits:
        player_counter = hit_counter[hit.player_id.id]
        player_counter['hit'] += 1
        for hit_type in hit_types:
            if getattr(hit, hit_type):
                player_counter[hit_type] += 1

    for player_id, player_counter in hit_counter.items():
        player_hit_counts = player_stats[player_id].hit_counts
        for hit_type, hit_type_count in player_counter.items():
            setattr(player_hit_counts, hit_type, hit_type_count)
