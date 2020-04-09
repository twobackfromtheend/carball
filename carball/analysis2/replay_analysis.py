import json
import logging
from pathlib import Path

from carball.analysis2.hits.hit import get_hits
from carball.analysis2.hits.hit_types.hit_type_calculation import calculate_hit_types
from carball.analysis2.pressure.pressure_calculation import calculate_pressures
from carball.analysis2.stats.stats_calculation import calculate_stats
from carball.analysis2.timer import timer
from carball.json_parser.game import Game as JsonParserGame
from carball.output_generation import create_data_frame, create_game
from carball.rattletrap.run_rattletrap import decompile_replay

logging.basicConfig(level=logging.DEBUG)


def analyse_replay(replay: str, output_path: str = None):
    json_ = None
    if output_path is not None:
        output_path_ = Path(output_path)
        if output_path_.is_file():
            with timer('Loading previously decompiled replay'):
                with output_path_.open("r") as f:
                    json_ = json.load(f)

    if json_ is None:
        with timer('Decompiling replay'):
            json_ = decompile_replay(replay, output_path=output_path)

    with timer('Parsing json'):
        json_parser_game = JsonParserGame()
        json_parser_game.initialize(loaded_json=json_)

    with timer('Creating protobuf game'):
        game = create_game(json_parser_game)
    # print(game)

    with timer('Creating full pandas DataFrame'):
        df = create_data_frame(json_parser_game)
    # print(df.memory_usage())

    events = game.events
    # with timer('Getting old hits'):
    #     # old hits
    #     old_hit_frames = BaseHit.get_hits_from_game(json_parser_game, None, None, df, None)

    with timer('Getting hits'):
        # new hits
        get_hits(events, game, df)

    with timer('Calculating hit types'):
        calculate_hit_types(events.hits, game, df)

    with timer('Calculating pressures'):
        calculate_pressures(events, game, df)

    with timer("Calculating stats"):
        analysis = calculate_stats(events, game, df)

    return json_parser_game, game, df, events, analysis
