from typing import Dict

import pandas as pd

from api.analysis.hit_pb2 import Hit
from carball.json_parser.game import Game as JsonParserGame


def set_goals(hits_by_goal_number: Dict[int, Hit], json_parser_game: JsonParserGame, df: pd.DataFrame):
    goals = sorted(json_parser_game.goals, key=lambda goal: goal.frame_number)

    for i, goal in reversed(list(enumerate(goals))):  # list() required as enumerate() is not reversible
        hits_this_goal = hits_by_goal_number[i]
        goal_scorer_id = goal.player.online_id
        last_hit_by_player = None
        goal_hit = None
        for hit in reversed(hits_this_goal):
            if hit.player_id.id == goal_scorer_id:
                if hit.shot:
                    goal_hit = hit
                    break
                if last_hit_by_player is None:
                    last_hit_by_player = hit
        if goal_hit is None:
            if last_hit_by_player is not None:
                print(f"Could not find shot for goal: {goal}. Using last hit by goalscorer...")
                goal_hit = last_hit_by_player
            else:
                print(f"Could not find hit for goal: {goal}")

            continue
        goal_hit.goal = True
