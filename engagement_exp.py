__author__ = 'nickdg'

import os
import random
import interactions
import ratcave.graphics as graphics
import ratcave.graphics.resources as resources


from psychopy import event

# Note: Collect Metadata (subject, mainly)

nPhases = 2
corner_idx = random.randint(1, 4)  # Select which corner everything appears in.
interaction_level = random.randint(0, 2)  # Three different levels

# Note: Connect to Motive, and get rigid bodies to track





# Note: Get Arena and locations for meshes to appear in the arena
arena_reader =graphics.WavefrontReader(os.path.join('obj', 'VR_Playground.obj'))
arena = arena_reader.get_mesh("Arena")


# Generate list of dict of position-triples (4 corners, paired with 4 sides, each with a center)
mesh_pos = {'Center': None, 'Side': None, 'Corner': None}
for coord in mesh_pos:
    mesh_name = 'Pos' + coord + str(corner_idx) if coord is not 'Center' else 'Pos' + coord
    mesh = arena_reader.get_mesh(mesh_name)
    mesh_pos[coord] = mesh.local.position


# Note: Only for interaction levels 1 and 2 (No Virtual Meshes in interaction level 0)
if interaction_level > 0:

    # Note: Import Mesh Objects (randomly chosen) and put in groups of three, one group for each phase
    vir_reader = graphics.WavefrontReader(os.path.join('obj', 'NOP_Primitives.obj'))
    mesh_groups = [[]] * nPhases
    for group in mesh_groups:
        mesh_list = []
        for pos_coords in mesh_pos.values():
            mesh_list.append(vir_reader.get_mesh(random.choice(vir_reader.mesh_names), position=pos_coords, centered=True))


    # Note: Interaction Level 2: Assign Object Properties (based on Interaction Level)
    if interaction_level == 2:
        interact_opts = [interactions.Jumper, interactions.Scaler, interactions.Spinner]
        for group in mesh_groups:
            for mesh, new_local in zip(mesh_list, [random.choice(interact_opts) for mesh in mesh_list]):
                mesh.local = new_local(position=mesh.local.position)


# Note: Build Scenes (1st half, 2nd half) and window


# Note: Main Experiment Logic