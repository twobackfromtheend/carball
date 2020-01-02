import logging

from api.game.game_pb2 import Game
from carball.json_parser.game import Game as JsonParserGame

logger = logging.getLogger(__name__)


def set_metadata(json_parser_game: JsonParserGame, game: Game):
    metadata = game.game_metadata

    metadata.id = json_parser_game.id
    metadata.name = json_parser_game.name if json_parser_game.name is not None else "None"
    metadata.map = json_parser_game.map
    metadata.team_size = json_parser_game.team_size

    metadata.time = int(json_parser_game.datetime.timestamp())
    metadata.frames = json_parser_game.frames.index.max()
    metadata.duration = json_parser_game.frames.delta.sum()

    metadata.game_server_id = json_parser_game.game_info.server_id
    metadata.server_name = json_parser_game.game_info.server_name

    if json_parser_game.replay_version is not None:
        metadata.version = json_parser_game.replay_version

    try:
        metadata.primary_player.id = json_parser_game.primary_player['id']
    except TypeError as e:
        logger.warning(f"Could not set primary_player.id: {e}")

    try:
        metadata.playlist = json_parser_game.game_info.playlist
    except:
        metadata.playlist = 0
        metadata.unknown_playlist = int(json_parser_game.game_info.playlist)

    try:
        if json_parser_game.game_info.match_guid == "":
            raise ValueError("match_guid from JsonParserGame is empty string.")
        metadata.match_guid = json_parser_game.game_info.match_guid
    except Exception as e:
        logger.warning(f"Could not set match_guid: {e}")

    set_game_score(json_parser_game, game)
    add_goals(json_parser_game, game)


def set_game_score(json_parser_game: JsonParserGame, game: Game):
    game_score = game.game_metadata.score
    for team in json_parser_game.teams:
        if team.is_orange:
            game_score.team_1_score = team.score
        else:
            game_score.team_0_score = team.score


def add_goals(json_parser_game: JsonParserGame, game: Game):
    goals = game.game_metadata.goals
    for json_parser_goal in json_parser_game.goals:
        goal = goals.add()
        goal.frame_number = json_parser_goal.frame_number
        goal.player_id.id = json_parser_goal.player.online_id

