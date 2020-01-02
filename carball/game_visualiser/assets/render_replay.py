import logging
import time
from math import cos, sin
from pathlib import Path
from threading import Thread

import pandas as pd
import numpy as np
import pyrender
import trimesh

from carball.analysis2.replay_analysis import analyse_replay
from carball.output_generation.data_frame_generation.prefixes import DF_BALL_PREFIX, DF_GAME_PREFIX

logging.getLogger('trimesh').setLevel(logging.INFO)
logging.getLogger('PIL').setLevel(logging.INFO)


def load_scene():
    ball_scene = trimesh.load("Ball.glb")
    octane_blue_scene = trimesh.load("Octane_ZXR_Blue.glb")
    octane_orange_scene = trimesh.load("Octane_ZXR_Orange.glb")
    field_scene = trimesh.load("Field.glb")

    def scale_and_roll_objects(trimesh_scene, scale: float):
        for name, trimesh_ in trimesh_scene.geometry.items():
            transformation_matrix = np.identity(4)

            # Rotate objects by pi / 2 around X (RH)
            roll = np.pi / 2
            transformation_matrix[:3, :3] = np.array(
                [[1, 0, 0],
                 [0, cos(roll), -sin(roll)],
                 [0, sin(roll), cos(roll)]]
            )

            # Scale objects
            transformation_matrix[:3, :3] *= scale
            trimesh_.apply_transform(transformation_matrix)

    scale_and_roll_objects(octane_blue_scene, 1 / 100)
    scale_and_roll_objects(octane_orange_scene, 1 / 100)
    scale_and_roll_objects(ball_scene, 1.1)
    scale_and_roll_objects(field_scene, 4)

    # Yaw field by pi to swap blue and orange.
    transformation_matrix = np.identity(4)
    pitch = np.pi
    transformation_matrix[:3, :3] = np.array(
        [[cos(pitch), 0, sin(pitch)],
         [0, 1, 0],
         [-sin(pitch), 0, cos(pitch)]]
    )
    for name, trimesh_ in field_scene.geometry.items():
        trimesh_.apply_transform(transformation_matrix)

    # Preview objects using trimesh's render
    # _scene = (ball_scene + field_scene + octane_blue_scene)
    # _scene.show()

    def as_pyrender_mesh(trimesh_scene):
        meshes = []
        for name, trimesh_ in trimesh_scene.geometry.items():
            # NOTE: Textures can be loaded through the fix in this PR
            # https://github.com/mmatl/pyrender/pull/94
            mesh = pyrender.Mesh.from_trimesh(trimesh_)
            meshes.append(mesh)
        return meshes

    ball_meshes = as_pyrender_mesh(ball_scene)
    octane_blue_meshes = as_pyrender_mesh(octane_blue_scene)
    octane_orange_meshes = as_pyrender_mesh(octane_orange_scene)
    # field_mesh = pyrender.Mesh.from_trimesh(field_mesh)

    scene = pyrender.Scene.from_trimesh_scene(field_scene)
    ball_nodes = [scene.add(mesh) for mesh in ball_meshes]

    def get_octane_nodes(is_orange: bool):
        if is_orange:
            return [scene.add(mesh) for mesh in octane_orange_meshes]
        else:
            return [scene.add(mesh) for mesh in octane_blue_meshes]

    def add_camera(scene):
        camera = pyrender.PerspectiveCamera(yfov=np.pi / 2)

        # Mostly taken from Viewer._compute_initial_camera_pose
        centroid = scene.centroid
        scale = scene.scale
        pose = np.identity(4)

        s2 = 1 / 2 ** 0.5
        pose_rotation = np.array([
            [0, -s2, s2],
            [1, 0, 0],
            [0, s2, s2]
        ])
        pose[:3, :3] = pose_rotation

        hfov = np.pi / 3
        dist = scale / (2 * np.tan(hfov))
        pose[:3, 3] = dist * np.array([1, 0, 1]) + centroid

        # Taken from trackball.rotate
        x_rot_mat = trimesh.transformations.rotation_matrix(3.1415926, [0, 0, 1], centroid)
        pose = x_rot_mat @ pose
        scene.add(camera, pose=pose)

    add_camera(scene)

    nodes = {'ball': ball_nodes, 'players': [get_octane_nodes(i < 3) for i in range(6)]}
    return scene, nodes


def get_rotation_matrix(pitch, yaw, roll):
    # pitch, yaw, roll = -pitch, -yaw, -roll
    R_pitch = np.array(
        [[cos(pitch), 0, sin(pitch)],
         [0, 1, 0],
         [-sin(pitch), 0, cos(pitch)]]
    )
    R_yaw = np.array(
        [[cos(yaw), -sin(yaw), 0],
         [sin(yaw), cos(yaw), 0],
         [0, 0, 1]]
    )
    R_roll = np.array(
        [[1, 0, 0],
         [0, cos(roll), -sin(roll)],
         [0, sin(roll), cos(roll)]]
    )

    return R_yaw @ R_pitch @ R_roll


def get_rotation_matrix_2(pitch, yaw, roll):
    CP = cos(pitch)
    SP = sin(pitch)
    CY = cos(yaw)
    SY = sin(yaw)
    CR = cos(roll)
    SR = sin(roll)

    # Chip's
    # theta = np.array(
    #     [[CP * CY, CY * SP * SR - CR * SY, -CR * CY * SP - SR * SY],
    #      [CP * SY, SY * SP * SR + CR * CY, -CR * SY * SP + SR * CY],
    #      [SP, -CP * SR, CP * CR]]
    # )

    # This agrees with get_rotation_matrix()
    # Wiki's: https://en.wikipedia.org/wiki/Euler_angles#Rotation_matrix See Z1 Y2 X3
    # negated cells [0, 2], [1, 2], [2, 0], [2, 1]
    theta = np.array(
        [[CP * CY, CY * SP * SR - CR * SY, CR * CY * SP + SR * SY],
         [CP * SY, SY * SP * SR + CR * CY, CR * SY * SP - SR * CY],
         [-SP, CP * SR, CP * CR]]
    )
    return theta


def get_transformation_matrix_from_frame(frame: pd.Series):
    pose = np.identity(4)
    positions = frame.loc[['pos_x', 'pos_y', 'pos_z']].values
    # positions[1] = -positions[1]  # y = -y to change LH axes to RH
    # positions[0] = -positions[0]  # x = -x to change LH axes to RH
    positions /= 100
    pose[:3, -1] = positions
    pose[:3, :3] = get_rotation_matrix(*frame.loc[['rot_x', 'rot_y', 'rot_z']].values)
    # pose[:3, :3] = get_rotation_matrix(*-frame.loc[['rot_x', 'rot_y', 'rot_z']].values)
    # pose[:3, :3] = get_rotation_matrix_2(*-frame.loc[['rot_x', 'rot_y', 'rot_z']].values)
    # print(pose)
    return pose


def event_loop():
    global v

    # player_names = list(set(df.columns.get_level_values(0).tolist()))
    # player_names.remove(DF_BALL_PREFIX)
    # player_names.remove(DF_GAME_PREFIX)

    blue_player_names = []
    orange_player_names = []
    for player in game.players:
        player_name = player.name
        if player.is_orange:
            orange_player_names.append(player_name)
        else:
            blue_player_names.append(player_name)

    player_names = orange_player_names + blue_player_names

    game_time_series = df[(DF_GAME_PREFIX, 'delta')].cumsum()
    start_time = time.time()
    previous_frame = -1
    i = 0
    while v.is_active:
        # time.sleep(0.016)
        # current_time = time.time() - start_time
        current_time = i * 1 / 30
        try:
            current_frame = game_time_series[game_time_series <= current_time].idxmax()
        except ValueError:
            current_frame = game_time_series.index.min()

        i += 1
        if current_frame == previous_frame:
            continue
        previous_frame = current_frame

        print(f"{current_frame}, {current_time:.1f}")

        v.render_lock.acquire()

        for player_nodes, player_name in zip(nodes['players'], player_names):
            player_frame = df.loc[current_frame, player_name]
            player_pose = get_transformation_matrix_from_frame(player_frame)
            for node in player_nodes:
                scene.set_pose(node, player_pose)

        ball_frame = df.loc[current_frame, DF_BALL_PREFIX]
        ball_pose = get_transformation_matrix_from_frame(ball_frame)
        for node in nodes['ball']:
            scene.set_pose(node, ball_pose)

        v.render_lock.release()
        # if current_frame > 100:
        #     break


if __name__ == '__main__':
    # replay = Path(r"D:\Replays\Replays\RLCS Season 8\RLCS\RLCS EU League Play\Week 3\M2 - FC Barcelona vs Dignitas\2CEB2CA94FD816017C48779C81793DA6.replay")

    # V7
    # replay = r"D:\Replays\Replays\RLCS Season 5\RLCS EU League Play\Week 4\FlipSid3 vs. Gale Force\2.replay"

    # V6
    # replay = r"D:\Replays\Replays\RLCS Season 5\RLCS EU League Play\Week 1\compLexity vs. Renault Vitality\3.replay"

    # V5
    # replay = r"D:\Replays\Replays\RLCS Season 4\3 - RLCS League Play\EU\Week 4\16DEDA5743657E626B2A33AC8E3EE603.replay"
    # replay = r"D:\Replays\Replays\RLCS Season 4\3 - RLCS League Play\EU\Week 1\02C04FEA48583FE6700D36AFA9411583.replay"
    # replay = r"D:\Replays\Replays\RLCS Season 3\2 - League Play\NA\Week 4\2F89292F42C2CF04DB352F8977661B9E.replay"
    # replay = r"D:\Replays\Replays\RLCS Season 3\2 - League Play\EU\Week 1\RLCS S3 - Week 1 - Cow Nose v PENTA - Game 1.replay"

    # V4
    # replay = r"D:\Replays\Replays\RLCS Season 2\2 - League Play\NA\Week 4\RLCS S2 - Week 4 - VindicatorGG v Take 3 - Game 2.replay"
    replay = r"D:\Replays\Replays\RLCS Season 2\2 - League Play\NA\Week 1\RLCS S2 - Week 1 - Exodus v Deception - Game 2.replay"

    # V2
    # replay = r"D:\Replays\Replays\RLCS Season 1\1 - Q2 Group Stage\NA\1B - Exodus vs Lucky Bounce - Game 2.replay"
    # replay = r"D:\Replays\Replays\RLCS Season 1\1 - Q2 Group Stage\NA\6B - Mock-It eSports NA vs Kings of Urban - Game 2.replay"
    # replay = r"D:\Replays\Replays\RLCS Season 1\3 - Live Finals\Day 2\RLCS S1 Finals - Match 9 - The Flying Dutchmen vs Genesis - Game 1.replay"

    json_parser_game, game, df, events, analysis = analyse_replay(str(replay))

    # df.to_pickle("2CEB2CA94FD816017C48779C81793DA6.df.pkl")
    # df.to_pickle("2.df.pkl")
    # df.to_pickle("3.df.pkl")

    # df = pd.read_pickle("2CEB2CA94FD816017C48779C81793DA6.df.pkl")
    # df = pd.read_pickle("2.df.pkl")

    scene, nodes = load_scene()

    # NOTE: Pyrender's run_in_thread does not work on Windows directly after installation (as of writing)
    # Use the workaround detailed in
    # https://github.com/mmatl/pyrender/issues/11#issuecomment-471390076
    v = pyrender.Viewer(
        scene,
        viewport_size=(1280, 720),
        use_raymond_lighting=True,
        lighting_intensity=5,
        refresh_rate=30,
        # rotate=True,
        run_in_thread=True
    )
    t = Thread(target=event_loop)
    t.start()
    v.start_app()
