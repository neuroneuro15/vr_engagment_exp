
import os
import random
import interactions
import motive
import numpy as np
import ratcave.graphics as graphics
from ratcave.utils import timers, rotate_to_var

import ratcave.graphics.resources as resources


from psychopy import event


# Functions
def correct_orientation(rb, n_attempts=3):
    """Reset the orientation to account for between-session arena shifts"""
    for attempt in range(n_attempts):
            rb.reset_orientation()
            motive.update()
    arena_markers = np.array(arena_rb.point_cloud_markers)
    additional_rotation = rotate_to_var(arena_markers)
    return additional_rotation


def get_arena_from(file_name=graphics.resources.obj_arena, cubemap=True):
    """Just returns the arena mesh from a .obj file."""
    reader = graphics.WavefrontReader(file_name)
    arena = reader.get_mesh('Arena', lighting=True, centered=False)
    arena.cubemap = cubemap
    return arena

def update_world_position(meshes, arena_rb):
    """# Update the positions of everything, based on the Optitrack data"""
    for mesh in meshes:
        mesh.world.position = arena_rb.location
        mesh.world.rotation = arena_rb.rotation_global
        mesh.world.rot_y += additional_rotation


# Script

# Note: Collect Metadata (subject, mainly, and Session Parameters) for the log
nPhases = 2
total_phase_secs = 5 * 60.  # 5 minutes
corner_idx = 1 # random.randint(1, 4)  # Select which corner everything appears in.
interaction_level = 1 # random.randint(0, 2)  # Three different levels
interaction_distance = .05  # In meters (I think)

metadata = {'Total Phases: ': nPhases,
            'Phase Time (secs)': total_phase_secs,
            'Corner ID where Objects Appear:': corner_idx,
            'Interactivity Amount (0-2)': interaction_level,
            'Rat-Object Distance Where Interaction Activates (meters)': interaction_distance,
            'Experimenter': 'Nicholas A. Del Grosso'}



# Note: Connect to Motive, and get rigid bodies to track
# FIXME: Plan to use the NatNetClient, not MotivePy, for this experiment.

motive.load_project(os.path.join('..', 'vr_demo', 'vr_demo.ttp'))
motive.update()
arena_rb = motive.get_rigid_bodies()['Arena']
additional_rotation = correct_orientation(arena_rb)
rat_rb = motive.get_rigid_bodies()['CalibWand']


# Note: Get Arena and locations for meshes to appear in the arena
arena = get_arena_from(cubemap=True)

# Generate list of dict of position-triples (4 corners, paired with 4 sides, each with a center)
reader =graphics.WavefrontReader(os.path.join('obj', 'VR_Playground.obj'))
mesh_pos = {'Center': None, 'Side': None, 'Corner': None}
for coord in mesh_pos:
    mesh_name = 'Pos' + coord + str(corner_idx) if coord is not 'Center' else 'Pos' + coord
    mesh = reader.get_mesh(mesh_name)
    mesh_pos[coord] = mesh.local.position # TODO: Make sure this is the correct position
del reader



# Note: Only for interaction levels 1 and 2 (No Virtual Meshes in interaction level 0)
mesh_groups = []
if interaction_level > 0:

    # Note: Import Mesh Objects (randomly chosen) and put in groups of three, one group for each phase
    vir_reader = graphics.WavefrontReader(os.path.join('obj', 'NOP_Primitives.obj'))
    for phase in range(nPhases):
        meshes = []
        for pos_coords in mesh_pos.values():
            meshes.append(vir_reader.get_mesh(random.choice(vir_reader.mesh_names), position=pos_coords, centered=True, scale=.01))
        mesh_groups.append(meshes)

    # Note: Interaction Level 2: Assign Object Properties (based on Interaction Level)
    if interaction_level > 1:
        interact_opts = [interactions.Jumper, interactions.Scaler, interactions.Spinner]
        for group in mesh_groups:
            for mesh in group:
                mesh.local = random.choice(interact_opts)(position=mesh.local.position) # TODO: Check


# Note: Build Scenes (1st half, 2nd half) and window
vir_scenes = [graphics.Scene(meshes) for meshes in mesh_groups]

active_scene = graphics.Scene([arena])
active_scene.camera = graphics.projector
active_scene.camera.fov_y = 27.8
active_scene.bgColor.b = .5

for scene in vir_scenes + [active_scene]:
    scene.light.position = active_scene.camera.position

window = graphics.Window(active_scene, fullscr=True, screen=1)
window.virtual_scene = vir_scenes[0]
window.virtual_scene.bgColor.r = .5

update_world_position(window.virtual_scene.meshes + [arena], arena_rb)

while True:
    motive.update()
    window.virtual_scene.camera.position = rat_rb.location
    window.draw()
    window.flip()
    if 'escape' in event.getKeys():
                break

"""
# dt_timer = timers.dt_timer()
with graphics.Logger(scenes=active_scene, exp_name='VR_Engagement', log_directory=os.path.join('.', 'logs'),
                     metadata_dict=metadata) as logger:

    # for phase in xrange(nPhases):

        # window.virtual_scene = vir_scenes[phase]


        # logger.write('Start of Phase {}'.format(phase))

        while True: #for _ in timers.countdown_timer(total_phase_secs, stop_iteration=True):

            # Update Data
            motive.update()

            # Update the Rat's position on the virtual scene's camera
            window.virtual_scene.camera.position = rat_rb.location  # FIXME: Fix when adding in tracking!
            #window.virtual_scene.camera.rotation = rat_rb.rotation_global

            # for mesh in window.virtual_scene.meshes + [arena]:
            #
                # Activate the mesh's custom physics if the rat gets close
                # if np.linalg.norm(np.subtract(window.virtual_scene.camera.position, mesh.position)) < interaction_distance:
                #     mesh.local.start()

                # # Update all mesh's physics
                # mesh.local.update(dt=dt_timer.next())

            # Draw and Flip
            window.draw()
            # logger.write()
            window.flip()


            # Give keyboard option to cleanly break out of the nested for-loop
            if 'escape' in event.getKeys():
                break
        # else:
        #     continue
        # break

"""


# Note: Clean-Up Section
window.close()