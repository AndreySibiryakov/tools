import skin_import_export as sie
reload(sie)
import maya.cmds as cmds
import maya.mel as mel
import sys
import os
import re
import functions as f
import batch_skin_eyes
reload(batch_skin_eyes)
import DLS
DLS.launch()


def set_fxgraph(head_mesh='', teeth_mesh='', sex='', skeleton=''):

    def namespaced(n):
        return '%s:%s' % (name_space, n)

    def compared_equal_vtxs(a, b):
        if cmds.polyEvaluate(a, vertex=True) == cmds.polyEvaluate(b, vertex=True):
            return True

    def import_biped_joints():
        import_file = cmds.fileDialog2(dialogStyle=2, fm=1)[0]
        cmds.file(import_file, i=True, namespace=name_space)
        # Delete all imported geometry except joints
        ns_objects = cmds.namespaceInfo(name_space, ls=True)
        ns_joints = cmds.listRelatives(
            namespaced(root_joint), type='joint', ad=True)
        ns_joints += [namespaced(root_joint)]
        ns_other_objects = [o for o in ns_objects if o not in ns_joints]
        cmds.delete(ns_other_objects)
        # Merge namespace with root
        cmds.namespace(rm=name_space, mnr=True)

    root_joint = 'Bip01'
    if skeleton == 'new':
        head_joint = 'driv_Bip01_Head'
    elif skeleton == 'old':
        head_joint = 'Bip01_Head'
    else:
        sys.exit('Skeleton should be defined')

    solved_pr = '_solved'
    mesh_solved = head_mesh + solved_pr
    name_space = 'tmp_ns_for_biped'
    if sex == 'male' and skeleton != 'old':
        template_mesh = 'male_head'
        teeth_template = 'male_teeth'
    elif sex == 'male' and skeleton == 'old':
        template_mesh = 'male_head_old'
        teeth_template = 'old_teeth'
    elif sex == 'female' and skeleton != 'old':
        template_mesh = 'female_head'
        teeth_template = 'female_teeth'
    elif sex == 'female' and skeleton == 'old':
        template_mesh = 'female_head_old'
        teeth_template = 'female_teeth_old'
    else:
        sys.exit('Sex not recognized. Should be "male" or "female".')

    teeth_bls = ['Teeth_Backwards',
                 'Teeth_Forwards',
                 'Teeth_Left',
                 'Teeth_Open',
                 'Teeth_Right',
                 'Tongue_Down',
                 'Tongue_In',
                 'Tongue_Narrow',
                 'Tongue_Out',
                 'Tongue_Pressed_Upwards',
                 'Tongue_Rolled_Down',
                 'Tongue_Rolled_Up',
                 'Tongue_Up',
                 'Tongue_Wide']

    while not f.exists(root_joint):
        import_biped_joints()
    # Redo with detailed missing messages
    if not f.exists(head_mesh):
        print head_mesh
        sys.exit('Some of objects are not present in scene.')
    if not f.exists(head_joint):
        print head_joint
        sys.exit('Some of objects are not present in scene.')
    if not f.exists(teeth_mesh):
        print teeth_mesh
        sys.exit('Some of objects are not present in scene.')
    if not f.exists(teeth_bls):
        print teeth_bls
        sys.exit('Some of objects are not present in scene.')

    if not compared_equal_vtxs(teeth_mesh, teeth_bls[0]):
        sys.exit('Blendshapes vertices quantity do not match the source mesh.')
    # ns = cmds.namespaceInfo(lon=True)[-1]

    # Makes shure head mesh has blendshapes keyed only with envelope turned on'
    head_blendshape = f.get_blendshape_node(head_mesh)
    if not head_blendshape:
        sys.exit('Head mesh has no blendshapes.')
    else:
        cmds.setAttr('%s.envelope' % head_blendshape, 1)

    # Deletes root joint
    root_joint = 'root'
    try:
        cmds.delete(root_joint)
    except Exception:
        print '# No root joint found to delete. Maybe is was deleted already.'

    cmds.currentTime(0)
    cmds.select(f.get_joints())
    cmds.cutKey()
    sy = batch_skin_eyes.SkinEyes(skeleton=skeleton)
    sy.set_skin()

    if cmds.objExists(head_mesh) and f.get_skin_cluster(head_mesh):
        used_biped_joints = f.set_auto_to_biped(head_mesh, skeleton=skeleton)
        # Deletes skin cluster with temporary auto joints from DLS
        cmds.skinCluster(f.get_skin_cluster(head_mesh), unbind=True, edit=True)
    elif cmds.objExists(mesh_solved) and f.get_skin_cluster(mesh_solved):
        used_biped_joints = f.set_auto_to_biped(mesh_solved, skeleton=skeleton)
    else:
        sys.exit('Both, base and solved head meshes have no skin cluster.')

    keyed_frames = cmds.keyframe(
        used_biped_joints[0], query=True, timeChange=True)
    sc = cmds.skinCluster(used_biped_joints +
                          [head_joint], head_mesh, tsb=True)[0]
    # Turns off skin cluster envelope for skin computation
    cmds.setAttr('%s.envelope' % sc, 0)
    # Add check for blendshape node to be turned on
    # Executes DLS for skin recomputation

    face_fxgraph = f.get_fxgraph(obj=head_mesh, print_fxgraph=False)
    f.dls(head_mesh)
    cmds.select(head_mesh)
    sie.export_weights_sp()
    # Removes blendshapes from head mesh.
    cmds.delete(head_mesh, ch=True)
    # Imports template weights for neck and head
    cmds.select(head_mesh)
    sie.import_weights_sp(remapped_name=template_mesh)
    # Imports weights on selected joints only
    cmds.select(head_mesh, used_biped_joints)
    sie.import_weights_sp()
    # Exports combined skin. Compluted on face and template on biped.
    cmds.select(head_mesh)
    sie.export_weights_sp()
    # Prepares teeth for fxgraph
    if not f.get_skin_cluster(teeth_mesh):
        cmds.select(teeth_mesh)
        sie.import_weights_sp(remapped_name=teeth_template)
    # Removes all unused joints. For DLS computation.
    cmds.select(teeth_mesh)
    mel.eval('removeUnusedInfluences;')
    teeth_mesh_bls = cmds.duplicate(teeth_mesh, n=teeth_mesh + '_bl')[0]
    last_biped_keyed_frame = max(keyed_frames)
    cmds.blendShape(teeth_bls, teeth_mesh_bls)
    end_teeth_frame = f.key_blendshapes(
        teeth_mesh_bls, start=last_biped_keyed_frame)
    # Sets timeline range to compute joints poses from teeth blendshapes
    cmds.playbackOptions(min=last_biped_keyed_frame, max=end_teeth_frame)
    # Target mesh is mesh with blendshapes
    f.dls(teeth_mesh, target_mesh=teeth_mesh_bls)
    end_eyes_frame = f.set_eyes_rom(
        start=end_teeth_frame, fxgraph=False, skeleton=skeleton)
    end_bip_frame = f.set_bip_rom(
        start=end_eyes_frame, fxgraph=False, skeleton=skeleton)
    # Gets fxgraph value:keys for FaceFX
    cmds.playbackOptions(min=min(keyed_frames), max=end_bip_frame)
    teeth_fxgraph = f.get_fxgraph(obj=teeth_mesh_bls, print_fxgraph=False)
    biped_fxgraph = f.set_bip_rom(
        start=end_eyes_frame, fxgraph=True, skeleton=skeleton)
    eyes_fxgraph = f.set_eyes_rom(
        start=end_teeth_frame, fxgraph=True, skeleton=skeleton)
    general_fxgraph = face_fxgraph + teeth_fxgraph + biped_fxgraph + eyes_fxgraph
    general_fxgraph = re.sub(
        ur'_(?=[0-9]\n|[0-9]{2}\n|[0-9]{3}\n|[0-9]{4}\n)', ' ', general_fxgraph)
    # Saves fxgraphw
    file_name = cmds.file(sceneName=True, query=True)
    file_dir = os.path.split(file_name)[0]
    fxgraph_prefix = '_fxgraph.txt'
    fxgraph_path = os.path.join(file_dir, head_mesh + fxgraph_prefix)

    cmds.keyTangent(head_joint, inTangentType='linear', outTangentType='linear')
    cmds.delete(teeth_mesh + '_bl')
    # Remove underscores _(?=[0-9]$|[0-9]{2}$|[0-9]{3}$|[0-9]{4}$)
    with open(fxgraph_path, 'w+') as fx:
        fx.write(general_fxgraph)
