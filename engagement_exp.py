
import os
import datetime
import itertools
import interactions
import numpy as np
from numpy import random
import ratcave
import ratcave.graphics as graphics
from psychopy import event, sound, gui
import sys

#import motive
import natnetclient

# Script

# Note: Collect Metadata (subject, mainly, and Session Parameters) for the log
metadata = {'Experiment': 'VR_Engagement',
            'nPhases': 2,
            'Phase Time':  60.,#5 * 60.  # 5 minutes,
            'Corner ID': [random.randint(1, 5), 1, 2, 3, 4], # Select which corner everything appears in.
            'Interaction Level': [random.randint(0, 3), 0, 1, 2], # Three different levels
            'Interaction Distance': .15,  # In meters (I think)
            'Experimenter': 'Nicholas A. Del Grosso',
            'Rat': ['Test', 'Nessie', 'FuzzPatch', 'FlatWhite', 'Bridger']
            }

dlg = gui.DlgFromDict(metadata, 'Input Parameters:')
if dlg.OK:
    metadata['Interaction Level'] = int(metadata['Interaction Level'])
    metadata['Corner ID'] = int(metadata['Corner ID'])
else:
    sys.exit()

# Note: Connect to Motive, and get rigid bodies to track
# NatNetClient code
tracker = natnetclient.NatClient()
arena_rb = tracker.rigid_bodies['Arena']
additional_rotation = ratcave.utils.correct_orientation_natnet(arena_rb)
rat_rb = tracker.rigid_bodies['CalibWand']

# Note: Get Arena and locations for meshes to appear in the arena
arena = ratcave.utils.get_arena_from(cubemap=True)
vir_arena = ratcave.utils.get_arena_from(os.path.join('obj', 'VR_Playground.blend'), cubemap=False)
vir_arena.load_texture(graphics.resources.img_uvgrid)
vir_arena.material.spec_weight = 0.

# Note: Only for interaction levels 1 and 2 (No Virtual Meshes in interaction level 0)
mesh_groups = []
if metadata['Interaction Level'] > 0:

    # Generate list of dict of position-triples (4 corners, paired with 4 sides, each with a center)
    reader =graphics.WavefrontReader(os.path.join('obj', 'VR_Playground.obj'))
    mesh_pos = {'Center': None, 'Side': None, 'Corner': None}
    for coord in mesh_pos:
        mesh_name = 'Pos' + coord + str(metadata['Corner ID']) if coord is not 'Center' else 'Pos' + coord
        mesh = reader.get_mesh(mesh_name)
        mesh.local.y += .015
        mesh_pos[coord] = mesh.local.position

    # Note: Import Mesh Objects (randomly chosen) and put in groups of three, one group for each phase
    vir_reader = graphics.WavefrontReader(os.path.join('obj', 'NOP_Primitives.obj'))
    for phase in range(metadata['nPhases']):
        meshes = []
        for pos_coords in mesh_pos.values():
            # Read Mesh
            mesh = vir_reader.get_mesh(random.choice(vir_reader.mesh_names), position=pos_coords, centered=True, scale=.02)

            # Randomly Set Color
            mesh.material.diffuse.rgb = random.rand(3).tolist()
            mesh.material.spec_color.rgb = random.rand(3).tolist()
            mesh.material.spec_weight = random.choice([0., 1., 3., 20.])

            mesh.local.rot_y = float(random.randint(0, 360))

            # Append to List
            meshes.append(mesh)
        mesh_groups.append(meshes)

    # Note: Interaction Level 2: Assign Object Properties (based on Interaction Level)
    if metadata['Interaction Level'] > 1:
        interact_opts = [interactions.Spinner, interactions.Scaler, interactions.Jumper]
        for group in mesh_groups:
            for mesh in group:
                mesh.local = random.choice(interact_opts)(position=mesh.local.position, scale=mesh.local.scale)

# Note: Build Scenes (1st half, 2nd half) and window
active_scene = graphics.Scene([arena], camera=graphics.projector, light=graphics.projector, bgColor=(0., 0., .2, 1.))
vir_scenes = [graphics.Scene([vir_arena], light=graphics.projector, bgColor=(0., .2, 0., 1.)) for phase in range(metadata['nPhases'])]
if metadata['Interaction Level'] > 0:
    for meshes, scene in zip(mesh_groups, vir_scenes):
        scene.meshes.extend(meshes)

window = graphics.Window(active_scene, fullscr=True, screen=1)

# Note: Wait for recording to start in Motive before starting the session.
tone = sound.Sound()
tone.play()  # Just to get the experimenter's attention
tracker.set_take_file_name(metadata['Experiment'] + datetime.datetime.today().strftime('_%Y-%m-%d_%H-%M-%S') + '.take')
tracker.wait_for_recording_start(debug_mode=metadata['Rat']=='Test')

# Note: Main Experiment Loop
with graphics.Logger(scenes=[active_scene], exp_name=metadata['Experiment'], log_directory=os.path.join('.', 'logs'),
                     metadata_dict=metadata) as logger:

    for phase in xrange(metadata['nPhases']):

        # Assign new virtual scene, and make its (and only its) meshes visible.
        window.virtual_scene = vir_scenes[phase]
        for mesh in [mesh for mesh_list in mesh_groups for mesh in mesh_list]:
            mesh.visible = True if mesh in window.virtual_scene.meshes else False

        ratcave.utils.update_world_position_natnet(window.virtual_scene.meshes + [arena], arena_rb, additional_rotation)

        logger.write('Start of Phase {}'.format(phase))

        for _, dt in itertools.izip(ratcave.utils.timers.countdown_timer(metadata['Phase Time'], stop_iteration=True),
                                    ratcave.utils.timers.dt_timer()):

            # Note: Update Data
            window.virtual_scene.camera.position = rat_rb.position
            window.virtual_scene.camera.rotation = rat_rb.rotation

            # Activate the mesh's custom physics, or start it if the rat gets close
            if metadata['Interaction Level'] > 1:
                for mesh in window.virtual_scene.meshes + [arena]:
                    mesh.local.update(dt)
                    if np.linalg.norm(np.subtract(window.virtual_scene.camera.position, mesh.position)[::2]) < metadata['Interaction Distance']:
                        mesh.local.start()


            # Draw and Flip
            window.draw()
            logger.write(':'.join(["Motive iFrame", str(tracker.iFrame)]))
            window.flip()

            # Give keyboard option to cleanly break out of the nested for-loop
            if 'escape' in event.getKeys():
                break
        else:
            continue
        break


# Note: Clean-Up Section
window.close()
tone.play()