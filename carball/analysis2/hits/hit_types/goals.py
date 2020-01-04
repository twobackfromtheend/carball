import logging
from typing import Dict

from api.events.hit_pb2 import Hit
from api.game.game_pb2 import Game

logger = logging.getLogger(__name__)


def set_goals(hits_by_goal_number: Dict[int, Hit], game: Game):
    goals = sorted(game.game_metadata.goals, key=lambda goal: goal.frame_number)

    for i, goal in reversed(list(enumerate(goals))):  # list() required as enumerate() is not reversible
        hits_this_goal = hits_by_goal_number[i]
        goal_scorer_id = goal.player_id.id
        last_hit_by_player = None
        goal_hit = None
        for hit in reversed(hits_this_goal):
            if hit.player_id.id == goal_scorer_id:
                if hit.shot:
                    goal_hit = hit
                    break
                else:
                    last_hit_by_player = hit
                    break
        if goal_hit is None:
            if last_hit_by_player is not None:
                logger.warning(f"Could not find shot for goal on frame {goal.frame_number}. "
                               f"Using last hit by goalscorer (on frame {last_hit_by_player.frame_number}).")
                goal_hit = last_hit_by_player
            else:
                logger.warning(f"Could not find hit for goal on frame {goal.frame_number}")
                continue
        goal_hit.goal = True
