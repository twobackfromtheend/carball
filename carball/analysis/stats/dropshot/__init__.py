from carball.json_parser.game import Game
from carball.generated.api.metadata.game_metadata_pb2 import RANKED_DROPSHOT, UNRANKED_DROPSHOT


def is_dropshot(game: Game):
    return game.game_info.playlist in [RANKED_DROPSHOT, UNRANKED_DROPSHOT] or game.map == 'ShatterShot_P'
