from collections import defaultdict, Counter
from typing import List

import pandas as pd

from api.analysis.hit_pb2 import Hit
from carball.analysis2.hits.hit_types.aerials import set_aerials_and_wall_hits
from carball.analysis2.hits.hit_types.goals import set_goals
from carball.analysis2.hits.hit_types.dependent_hit_types import set_hit_type_dependent_on_previous_hit
from carball.analysis2.hits.hit_types.shots import set_shots
from carball.analysis2.timer import timer
from carball.json_parser.game import Game as JsonParserGame


def calculate_hit_types(hits: List[Hit], json_parser_game: JsonParserGame, df: pd.DataFrame):
    hits_by_goal_number = defaultdict(list)
    for hit in hits:
        hits_by_goal_number[hit.goal_number].append(hit)

    with timer("\tCalculating shots"):
        set_shots(hits_by_goal_number, json_parser_game, df)
    with timer("\tCalculating goals"):
        set_goals(hits_by_goal_number, json_parser_game, df)
    with timer("\tCalculating dependent hit types"):
        set_hit_type_dependent_on_previous_hit(hits_by_goal_number, json_parser_game, df)

    set_aerials_and_wall_hits(hits_by_goal_number, json_parser_game, df)
