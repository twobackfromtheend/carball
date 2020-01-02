from api.game.game_pb2 import Game
from carball.json_parser.game import Game as JsonParserGame


def add_demos(json_parser_game: JsonParserGame, game: Game):
    demos = game.events.demos
    for json_parser_demo in json_parser_game.demos:
        demo = demos.add()
        demo.frame_number = json_parser_demo['frame_number']
        demo.attacker_id.id = json_parser_demo['attacker'].online_id
        demo.victim_id.id = json_parser_demo['victim'].online_id
