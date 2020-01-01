import trimesh
from pygltflib import GLTF2


# ball_glb = GLTF2().load("Ball.glb")
# octane_glb = GLTF2().load("Octane_ZXR_Blue.glb")

mesh = trimesh.load("Ball.glb")

mesh.show()


print("hi")

