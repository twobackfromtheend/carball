from collections import defaultdict
from typing import List

import pandas as pd

from api.events.hit_pb2 import Hit
from api.game.game_pb2 import Game
from carball.analysis2.hits.hit_types.aerials import set_aerials_and_wall_hits
from carball.analysis2.hits.hit_types.dependent_hit_types import set_hit_type_dependent_on_previous_hit
from carball.analysis2.hits.hit_types.goals import set_goals
from carball.analysis2.hits.hit_types.shots import set_shots
from carball.analysis2.timer import timer


def calculate_hit_types(hits: List[Hit], game: Game, df: pd.DataFrame):
    hits_by_goal_number = defaultdict(list)
    for hit in hits:
        hits_by_goal_number[hit.goal_number].append(hit)

    with timer("\tCalculating shots"):
        set_shots(hits_by_goal_number, game, df)
    with timer("\tCalculating goals"):
        set_goals(hits_by_goal_number, game)
    with timer("\tCalculating dependent hit types"):
        set_hit_type_dependent_on_previous_hit(hits_by_goal_number, game)

    set_aerials_and_wall_hits(hits_by_goal_number, df)
