from collections import defaultdict, Counter
from typing import List

import pandas as pd

from api.analysis.hit_pb2 import Hit
from carball.analysis2.hits.hit_types.goals import set_goals
from carball.analysis2.hits.hit_types.passes import set_hit_type_dependent_on_previous_hit
from carball.analysis2.hits.hit_types.shots import set_shots
from carball.json_parser.game import Game as JsonParserGame


def calculate_hit_types(hits: List[Hit], json_parser_game: JsonParserGame, df: pd.DataFrame):
    hits_by_goal_number = defaultdict(list)
    for hit in hits:
        hits_by_goal_number[hit.goal_number].append(hit)

    set_shots(hits_by_goal_number, json_parser_game, df)
    set_goals(hits_by_goal_number, json_parser_game, df)
    set_hit_type_dependent_on_previous_hit(hits_by_goal_number, json_parser_game, df)

    count_hit_types = defaultdict(Counter)

    attributes = ['goal', 'assist', 'save', 'shot', 'secondary_assist', 'pass_', 'passed', 'dribble',
                  'dribble_continuation']
    for hit in hits:
        for attribute in attributes:
            if getattr(hit, attribute):
                count_hit_types[attribute][hit.player_id.id] += 1

    print(count_hit_types)
