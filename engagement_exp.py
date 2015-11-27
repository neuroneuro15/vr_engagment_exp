
import os

import itertools
import interactions
import motive
import numpy as np
from numpy import random
import ratcave
import ratcave.graphics as graphics
from psychopy import event, sound, gui
import sys

# Script

# Note: Collect Metadata (subject, mainly, and Session Parameters) for the log
nPhases = 2
total_phase_secs = 5 * 60.  # 5 minutes
corner_idx = random.randint(1, 5)  # Select which corner everything appears in.
interaction_level = random.randint(0, 3)  # Three different levels
interaction_distance = .15  # In meters (I think)

metadata = {'Total Phases: ': nPhases,
            'Phase Time (secs)': total_phase_secs,
            'Corner ID where Objects Appear:': corner_idx,
            'Interactivity Amount (0-2)': interaction_level,
            'Rat-Object Distance Where Interaction Activates (meters)': interaction_distance,
            'Experimenter': 'Nicholas A. Del Grosso'}

info = {'Rat': ['Nessie', 'FuzzPatch', 'FlatWhite', 'Bridger']}
dlg = gui.DlgFromDict(info, 'Input Rat Name:')
if dlg.OK:
    metadata.update(info)
else:
    print("User Cancelled. Exiting...")
    sys.exit()

# Note: Connect to Motive, and get rigid bodies to track
# FIXME: Plan to use the NatNetClient, not MotivePy, for this experiment.

motive.load_project(os.path.join('..', 'vr_demo', 'vr_demo.ttp'))
motive.update()
arena_rb = motive.get_rigid_bodies()['Arena']
additional_rotation = ratcave.utils.correct_orientation(arena_rb)
rat_rb = motive.get_rigid_bodies()['CalibWand']


# Note: Get Arena and locations for meshes to appear in the arena
arena = ratcave.utils.get_arena_from(cubemap=True)
vir_arena = ratcave.utils.get_arena_from(os.path.join('obj', 'VR_Playground.blend'), cubemap=False)
vir_arena.load_texture(graphics.resources.img_uvgrid)

# Generate list of dict of position-triples (4 corners, paired with 4 sides, each with a center)
reader =graphics.WavefrontReader(os.path.join('obj', 'VR_Playground.obj'))
mesh_pos = {'Center': None, 'Side': None, 'Corner': None}
for coord in mesh_pos:
    mesh_name = 'Pos' + coord + str(corner_idx) if coord is not 'Center' else 'Pos' + coord
    mesh = reader.get_mesh(mesh_name)
    mesh.local.y += .02
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
            # Read Mesh
            mesh = vir_reader.get_mesh(random.choice(vir_reader.mesh_names), position=pos_coords, centered=True, scale=.02)

            # Randomly Set Color
            mesh.material.diffuse.rgb = random.rand(3).tolist()
            mesh.material.spec_color.rgb = random.rand(3).tolist()
            mesh.material.spec_weight = random.choice([0., 1., 3., 20.])

            # Append to List
            meshes.append(mesh)
        mesh_groups.append(meshes)

    # Note: Interaction Level 2: Assign Object Properties (based on Interaction Level)
    if interaction_level > 1:
        interact_opts = [interactions.Spinner, interactions.Scaler, interactions.Jumper]
        for group in mesh_groups:
            for mesh in group:
                mesh.local = random.choice(interact_opts)(position=mesh.local.position, scale=mesh.local.scale)


# Note: Build Scenes (1st half, 2nd half) and window
vir_scenes = [graphics.Scene([vir_arena]) for phase in range(nPhases)]
if interaction_level > 0:
    for meshes, scene in zip(mesh_groups, vir_scenes):
        scene.meshes.extend(meshes)

active_scene = graphics.Scene([arena])
active_scene.camera = graphics.projector
active_scene.camera.fov_y = 27.8
active_scene.bgColor.b = .2

for scene in vir_scenes + [active_scene]:
    scene.light.position = active_scene.camera.position

window = graphics.Window(active_scene, fullscr=True, screen=1)

# tone = sound.Sound()
with graphics.Logger(scenes=active_scene, exp_name='VR_Engagement', log_directory=os.path.join('.', 'logs'),
                     metadata_dict=metadata) as logger:

    for phase in xrange(nPhases):

        window.virtual_scene = vir_scenes[phase]
        window.virtual_scene.bgColor.g = .2
        ratcave.utils.update_world_position(window.virtual_scene.meshes + [arena], arena_rb, additional_rotation)

        logger.write('Start of Phase {}'.format(phase))

        for _, dt in itertools.izip(ratcave.utils.timers.countdown_timer(total_phase_secs, stop_iteration=True),
                                    ratcave.utils.timers.dt_timer()):

            # Update Data
            motive.update()

            # Update the Rat's position on the virtual scene's camera
            window.virtual_scene.camera.position = rat_rb.location  # FIXME: Fix when adding in tracking!
            window.virtual_scene.camera.rotation = rat_rb.rotation_global

            # dt = dt_timer.next()
            for mesh in window.virtual_scene.meshes + [arena]:

                # Activate the mesh's custom physics if the rat gets close
                if np.linalg.norm(np.subtract(window.virtual_scene.camera.position, mesh.position)[::2]) < interaction_distance:
                    # tone.play()
                    mesh.local.start()


                # Update all mesh's physics
                mesh.local.update(dt)

            # Draw and Flip
            window.draw()
            logger.write()
            window.flip()


            # Give keyboard option to cleanly break out of the nested for-loop
            if 'escape' in event.getKeys():
                break
        else:
            continue
        break




# Note: Clean-Up Section
window.close()