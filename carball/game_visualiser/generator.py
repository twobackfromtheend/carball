import logging
import math
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import tqdm

from api.events.events_pb2 import Events
from api.game.game_pb2 import Game
from carball.analysis2.replay_analysis import analyse_replay
from carball.game_visualiser.overlays.boost_indicator import BoostIndicator
from carball.game_visualiser.overlays.boost_indicator_horizontal import BoostIndicatorHorizontal
from carball.game_visualiser.overlays.minimap import Minimap
from carball.game_visualiser.overlays.timer import Timer
from matplotlib.animation import FFMpegWriter

from carball.output_generation.data_frame_generation.prefixes import DF_GAME_PREFIX

plt.rcParams['animation.ffmpeg_path'] = str(Path(__file__).parent / "ffmpeg" / "ffmpeg.exe")
logging.getLogger('matplotlib').setLevel(logging.INFO)


def generate_video(game: Game, df: pd.DataFrame, events: Events):
    DPI = 300
    FPS = 10
    plt.rcParams['font.family'] = 'sans-serif'
    plt.rcParams['font.sans-serif'] = ['Lato']
    plt.rcParams['font.weight'] = 'heavy'

    # game_time_series = df[('game', 'time')]
    game_time_series = df[(DF_GAME_PREFIX, 'delta')].cumsum()
    # game_time_series = game_time_series[game_time_series < 30]

    player_id_to_name = {
        player.id.id: player.name
        for player in game.players
    }
    game_hits = events.hits
    hit_frame_numbers = np.array([
        hit.frame_number
        for hit in game_hits
    ])

    def get_last_hit(current_frame_number: int) -> str:
        if current_frame_number < hit_frame_numbers[0]:
            return "None"
        if current_frame_number >= hit_frame_numbers[-1]:
            hit_index = len(hit_frame_numbers) - 1
        else:
            hit_index = (hit_frame_numbers > current_frame_number).argmax() - 1

        hit_player_id = game_hits[hit_index].player_id.id
        return player_id_to_name[hit_player_id]

    total_duration = game_time_series.max() - game_time_series.min()
    # total_frames = math.ceil(total_duration * FPS)
    total_frames = 500

    metadata = dict(title='Movie Test', artist='twobackfromtheend', comment='hello there')
    writer = FFMpegWriter(fps=FPS, metadata=metadata)

    fig = plt.figure(figsize=(8, 8), dpi=DPI)
    # fig = plt.figure(figsize=(8, 2), dpi=DPI)

    player_names = []
    player_is_oranges = []
    for player in game.players:
        player_names.append(player.name)
        player_is_oranges.append(player.is_orange)
    ax = plt.gca()
    minimap = Minimap(ax, df, player_names, player_is_oranges, offset=(0, 0))
    minimap.setup()

    # boost_indicator = BoostIndicator(ax, df, player_names, player_is_oranges,
    #                                  offset=(-300 * 15 / 2 + 1000, -8000), scale=15)
    boost_indicator = BoostIndicatorHorizontal(ax, df, player_names, player_is_oranges,
                                               offset=(0, -8000), scale=1)
    boost_indicator.setup()

    timer = Timer(ax, df, player_names, player_is_oranges, offset=(0, 7000))
    timer.setup()

    ax.set_aspect('equal', 'datalim')
    plt.axis('off')
    ax.set_ylim((-8200, 6000))
    # ax.set_ylim((-8200, -5000))

    # current_frame = 1
    current_time = game_time_series.min()
    # seconds_remaining_series = df[(DF_GAME_PREFIX, 'seconds_remaining')]
    last_hit = plt.text(0, 6500, "None", ha='center')

    with writer.saving(fig, "output.mp4", dpi=DPI):
        for i in tqdm.trange(total_frames):
            # print(current_time, current_frame, total_frames)
            current_frame = game_time_series[game_time_series <= current_time].idxmax()

            minimap.update(current_frame)
            boost_indicator.update(current_frame)
            timer.update(current_frame)

            last_hit.set_text(get_last_hit(current_frame))
            current_time += 1 / FPS
            writer.grab_frame()


if __name__ == '__main__':
    # replay = r"D:\Replays\Replays\RLCS Season 8\RLCS\RLCS EU League Play\Week 3\M2 - FC Barcelona vs Dignitas\2CEB2CA94FD816017C48779C81793DA6.replay"
    replay = r"D:\Replays\Replays\RLCS Season 5\RLCS EU League Play\Week 4\FlipSid3 vs. Gale Force\2.replay"
    json_parser_game, game, df, events, analysis = analyse_replay(str(replay))

    generate_video(game, df, events)
