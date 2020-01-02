from collections import Counter
from typing import Dict

import numpy as np
import pandas as pd

from api.analysis.stats_pb2 import PlayerStats
from api.game.game_pb2 import Game
from carball.analysis2.constants.constants import FIELD_Y_LIM, FIELD_X_LIM


def set_demo_stats(player_stats: Dict[str, PlayerStats], game: Game, player_blue_data_frames: Dict[str, pd.DataFrame]):
    player_id_to_name: Dict[str, str] = {player.id.id: player.name for player in game.players}

    demo_counts = Counter()
    demoed_counts = Counter()
    demos_near_opponent_goal_counts = Counter()
    demoed_near_own_goal_counts = Counter()
    active_frames = list(player_blue_data_frames.values())[0].index

    for demo in game.events.demos:
        frame_number = demo.frame_number
        if frame_number not in active_frames:
            continue
        attacker_id = demo.attacker_id.id
        victim_id = demo.victim_id.id

        demo_counts[attacker_id] += 1
        demoed_counts[victim_id] += 1

        victim_blue_df = player_blue_data_frames[victim_id]

        victim_name = player_id_to_name[victim_id]
        victim_position_at_demo = victim_blue_df.loc[frame_number - 1, (victim_name, ['pos_x', 'pos_y'])].values
        BLUE_GOAL_POSITION = np.array([0, -FIELD_Y_LIM])

        victim_distance_from_goal = ((victim_position_at_demo - BLUE_GOAL_POSITION) ** 2).sum() ** 0.5
        if victim_distance_from_goal < FIELD_X_LIM / 2:
            demos_near_opponent_goal_counts[attacker_id] += 1
            demoed_near_own_goal_counts[victim_id] += 1

    for player_id, _player_stats in player_stats.items():
        _player_stats.demos = demo_counts[player_id]
        _player_stats.demoed = demoed_counts[player_id]
        _player_stats.demos_near_opponent_goal = demos_near_opponent_goal_counts[player_id]
        _player_stats.demoed_near_own_goal = demoed_near_own_goal_counts[player_id]
