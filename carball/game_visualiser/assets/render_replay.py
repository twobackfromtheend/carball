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
    octane_scene = trimesh.load("Octane_ZXR_Blue.glb")
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

    scale_and_roll_objects(octane_scene, 1 / 100)
    scale_and_roll_objects(ball_scene, 1.1)
    scale_and_roll_objects(field_scene, 4)

    scene_ = (ball_scene + field_scene + octane_scene)
    scene_.show()

    def as_pyrender_mesh(trimesh_scene):
        meshes = []
        for name, trimesh_ in trimesh_scene.geometry.items():
            # material = {
            #     k: v
            #     for k, v in trimesh_.visual.material.__dict__.items()
            #     # if v is not None and v != 0
            # }
            material = pyrender.MetallicRoughnessMaterial(**trimesh_.visual.material.__dict__)
            mesh = pyrender.Mesh.from_trimesh(trimesh_, material=material)
            # mesh = pyrender.Mesh.from_trimesh(trimesh_)
            meshes.append(mesh)
        return meshes

    ball_meshes = as_pyrender_mesh(ball_scene)
    octane_meshes = as_pyrender_mesh(octane_scene)
    # field_mesh = pyrender.Mesh.from_trimesh(field_mesh)

    scene = pyrender.Scene.from_trimesh_scene(field_scene)
    ball_nodes = [scene.add(mesh) for mesh in ball_meshes]

    def get_octane_nodes():
        return [scene.add(mesh) for mesh in octane_meshes]

    nodes = {'ball': ball_nodes, 'players': [get_octane_nodes() for _ in range(6)]}
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

    return R_pitch @ R_yaw @ R_roll


def get_rotation_matrix_2(pitch, yaw, roll):
    CP = cos(pitch)
    SP = sin(pitch)
    CY = cos(yaw)
    SY = sin(yaw)
    CR = cos(roll)
    SR = sin(roll)

    theta = np.array(
        [[CP * CY, CY * SP * SR - CR * SY, -CR * CY * SP - SR * SY],
         [CP * SY, SY * SP * SR + CR * CY, -CR * SY * SP + SR * CY],
         [SP, -CP * SR, CP * CR]]
    )
    return theta


def get_transformation_matrix_from_frame(frame: pd.Series):
    pose = np.identity(4)
    positions = frame.loc[['pos_x', 'pos_y', 'pos_z']].values
    positions[1] = -positions[1]  # y = -y to change LH axes to RH
    positions /= 100
    pose[:3, -1] = positions
    pose[:3, :3] = get_rotation_matrix_2(*-frame.loc[['rot_x', 'rot_y', 'rot_z']].values)
    # print(pose)
    return pose

    print("hi")


def event_loop():
    global v

    player_names = list(set(df.columns.get_level_values(0).tolist()))
    player_names.remove(DF_BALL_PREFIX)
    player_names.remove(DF_GAME_PREFIX)

    game_time_series = df[(DF_GAME_PREFIX, 'delta')].cumsum()
    start_time = time.time()
    previous_frame = -1
    while v.is_active:
        time.sleep(0.016)
        current_time = time.time() - start_time
        try:
            current_frame = game_time_series[game_time_series <= current_time].idxmax()
        except ValueError:
            current_frame = game_time_series.index.min()

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
    replay = r"D:\Replays\Replays\RLCS Season 5\RLCS EU League Play\Week 4\FlipSid3 vs. Gale Force\2.replay"
    json_parser_game, game, df, events, analysis = analyse_replay(str(replay))

    # df.to_pickle("2CEB2CA94FD816017C48779C81793DA6.df.pkl")
    df.to_pickle("2.df.pkl")

    # df = pd.read_pickle("2CEB2CA94FD816017C48779C81793DA6.df.pkl")
    # df = pd.read_pickle("2.df.pkl")

    scene, nodes = load_scene()
    # v = pyrender.Viewer(scene, use_raymond_lighting=True)
    # v.start_app()

    # r = pyrender.OffscreenRenderer(viewport_width=800,
    #                                viewport_height=600,
    #                                point_size=1.0)

    v = pyrender.Viewer(scene, use_raymond_lighting=True, run_in_thread=True)
    t = Thread(target=event_loop)
    t.start()
    v.start_app()
