from api.game.game_pb2 import Game
from carball.json_parser.game import Game as JsonParserGame
from carball.output_generation.proto_generation.demos import add_demos
from carball.output_generation.proto_generation.game_metadata import set_metadata
from carball.output_generation.proto_generation.parties import add_parties
from carball.output_generation.proto_generation.players import add_players
from carball.output_generation.proto_generation.teams import add_teams


def create_game(json_parser_game: JsonParserGame) -> Game:
    game = Game()
    set_metadata(json_parser_game, game)
    add_teams(json_parser_game, game)
    add_parties(json_parser_game, game)
    add_players(json_parser_game, game)

    add_demos(json_parser_game, game)

    return game
