from collections import defaultdict
from typing import List, Dict

import pandas as pd

from api.analysis.hit_pb2 import Hit
from carball.json_parser.game import Game as JsonParserGame


def set_hit_type_dependent_on_previous_hit(hits_by_goal_number: Dict[int, Hit], json_parser_game: JsonParserGame,
                                           df: pd.DataFrame):
    player_id_to_team = {player.online_id: player.is_orange for player in json_parser_game.players}

    for hits_list in hits_by_goal_number.values():
        previous_hit = None
        previous_previous_hit = None
        for hit in hits_list:
            if previous_hit is None:
                previous_hit = hit
                continue

            hit_player_id = hit.player_id.id
            previous_hit_player_id = previous_hit.player_id.id
            if hit_player_id == previous_hit_player_id:
                # Dribbles + dribble_continuations
                if previous_hit.dribble_continuation:
                    hit.dribble_continuation = True
                else:
                    previous_hit.dribble = True
                    hit.dribble_continuation = True
            else:
                if player_id_to_team[hit_player_id] == player_id_to_team[previous_hit_player_id]:
                    # Passes
                    previous_hit.pass_ = True
                    hit.passed = True

                    if hit.goal:
                        # Assists
                        previous_hit.assist = True

                        # Secondary assists
                        previous_previous_hit_player_id = previous_previous_hit.player_id.id
                        if previous_previous_hit_player_id != previous_hit_player_id and \
                                player_id_to_team[previous_previous_hit_player_id] == player_id_to_team[
                            previous_hit_player_id]:
                            previous_previous_hit.secondary_assist = True
                else:
                    # Saves
                    if previous_hit.shot and not previous_hit.goal:
                        hit.save = True

            previous_previous_hit = previous_hit
            previous_hit = hit
