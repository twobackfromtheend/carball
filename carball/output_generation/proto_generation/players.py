from api.game.game_pb2 import Game
from api.game.player_pb2 import Player
from carball.json_parser.game import Game as JsonParserGame
from carball.json_parser.player import Player as JsonParserPlayer


def add_players(json_parser_game: JsonParserGame, game: Game):
    for json_parser_player in json_parser_game.players:
        player = game.players.add()

        set_camera_settings(json_parser_player, player)
        set_loadout(json_parser_player, player)

        player.id.id = json_parser_player.online_id

        if json_parser_player.party_leader is not None:
            player.party_leader.id = json_parser_player.party_leader

        attributes = [
            'name', 'title', 'score', 'goals', 'assists', 'saves', 'shots', 'is_bot'
        ]
        for attribute in attributes:
            json_parser_value = getattr(json_parser_player, attribute, None)
            if json_parser_value is not None:
                setattr(player, attribute, json_parser_value)


def set_camera_settings(json_parser_player: JsonParserPlayer, player: Player):
    json_parser_camera_settings = json_parser_player.camera_settings
    camera_settings = player.camera_settings
    attributes = [
        'stiffness', 'height', 'transition_speed', 'pitch', 'swivel_speed', 'field_of_view', 'distance'
    ]
    for attribute in attributes:
        try:
            json_parser_value = json_parser_camera_settings.get(attribute, None)
            setattr(camera_settings, attribute, json_parser_value)
        except TypeError as e:
            print(f"Could not set camera_settings attribute: {attribute}: {e}")


def set_loadout(json_parser_player: JsonParserPlayer, player: Player):
    try:
        json_parser_loadout = json_parser_player.loadout[player.is_orange]
        json_parser_paints = json_parser_player.paint[player.is_orange]
        json_parser_user_colors = json_parser_player.user_colors[player.is_orange]
    except IndexError:
        return

    loadout = player.loadout
    loadout_attributes = [
        'banner', 'boost', 'car', 'goal_explosion', 'skin', 'trail', 'version',
        'wheels', 'topper', 'antenna', 'engine_audio', 'avatar_border',
        'primary_color', 'accent_color', 'primary_finish', 'accent_finish',
    ]
    for attribute in loadout_attributes:
        json_parser_value = json_parser_loadout.get(attribute, None)
        if json_parser_value is not None:
            setattr(loadout, attribute, json_parser_value)

    paint_attributes = [
        'banner', 'boost', 'car', 'goal_explosion', 'skin', 'trail', 'wheels', 'topper', 'antenna',
    ]
    for attribute in paint_attributes:
        json_parser_value = json_parser_paints.get(attribute, None)
        if json_parser_value is not None:
            setattr(loadout, f"{attribute}_paint", json_parser_value)

    user_colour_attributes = [
        'banner', 'avatar_border',
    ]
    for attribute in user_colour_attributes:
        json_parser_value = json_parser_user_colors.get(attribute, None)
        if json_parser_value is not None:
            setattr(loadout, f"{attribute}_user_color", json_parser_value)
