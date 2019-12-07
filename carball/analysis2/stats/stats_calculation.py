from collections import defaultdict
from typing import List, Counter, Dict

import numpy as np
import pandas as pd

from api.analysis.analysis_pb2 import Analysis
from api.analysis.hit_pb2 import Hit
from api.analysis.stats_pb2 import HitCounts, PlayerStats
from carball.analysis2.data_frame_filters.data_frame_filters import get_flipped_data_frame
from carball.analysis2.stats.boost_stats import set_boost_stats
from carball.analysis2.stats.movement_stats import set_movement_stats
from carball.analysis2.stats.positioning_stats import set_positioning_stats
from carball.json_parser.game import Game as JsonParserGame
from api.game.game_pb2 import Game

from carball.output_generation.data_frame_generation.prefixes import DF_GAME_PREFIX, DF_BALL_PREFIX


def calculate_stats(hits: List[Hit], game: Game, df: pd.DataFrame):
    analysis = Analysis()
    player_stats: Dict[str, PlayerStats] = {}
    for player in game.players:
        player_id = player.id.id
        _player_stats = analysis.player_stats.add()
        _player_stats.id.id = player_id
        player_stats[player_id] = _player_stats

    set_hit_counts(hits, player_stats)

    active_frames_df = df[~df.game__.goal_number.isna()]

    player_blue_data_frames: Dict[str, pd.DataFrame] = {}
    flipped_df = get_flipped_data_frame(active_frames_df)
    for player in game.players:
        player_id = player.id.id
        if player.is_orange:
            player_df = flipped_df
        else:
            player_df = active_frames_df
        player_blue_data_frames[player_id] = player_df

    set_boost_stats(player_stats, player_blue_data_frames, game)
    set_movement_stats(player_stats, player_blue_data_frames, game)
    set_positioning_stats(player_stats, player_blue_data_frames, game)

    for player in game.players:
        player_name = player.name


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
