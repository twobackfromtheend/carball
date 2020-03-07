from api.game.game_pb2 import Game
from carball.json_parser.game import Game as JsonParserGame


def add_teams(json_parser_game: JsonParserGame, game: Game):
    for json_parser_team in json_parser_game.teams:
        team = game.teams.add()
        if json_parser_team.name is not None:
            team.name = str(json_parser_team.name)
        for player in json_parser_team.players:
            player_id = team.player_ids.add()
            player_id.id = player.online_id
        team.is_orange = json_parser_team.is_orange
        team.score = json_parser_team.score
