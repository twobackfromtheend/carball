from api.game.game_pb2 import Game
from carball.json_parser.game import Game as JsonParserGame


def add_parties(json_parser_game: JsonParserGame, game: Game):
    parties = game.parties
    for leader_id, members in json_parser_game.parties.items():
        party = parties.add()
        party.leader_id.id = leader_id
        for member_id in members:
            player = party.members.add()
            player.id = member_id
