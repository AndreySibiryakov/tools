
import pickle
import sys
import maya.cmds as cmds
import os
# import DLS
from maya.api.OpenMaya import MVector
import xml.etree.ElementTree
import maya.mel as mel
import random
import DLS
import time
import re

mapping_folder = 'd:/.work/.chrs/.bone_mapping'
xml_folder = 'd:/.work/.chrs/.xml'
upper_lower_match = 'd:/.work/.chrs/.upper_lower_match/upper_lower_match.txt'
lps_path = 'd:/.work/.chrs/.lps/'


'''Gets or set bone mapping for a character, bone per vertex correspondance.
	Since bones are constrained to vertices.
	And vertices are driven with a blendshapes.

Args:
	folder (str): path to bone mapping files that contain dictionary,
		dumped with a pickle 
	set_mapping (bool, optional): used with cubes and mapping params.
		Defaults to False
		Sets custom mapping for a character
	cubes (list, optional): used with set and mapping params.
		Cubes that visualize joint placement
	mapping (dict, optional): used with set and cubes params.
		Bone per vertex correspondance

Returns:
	dict: default or custom bone per vertex correspondance for a '*_head' mesh

Examples:
	>>> print([i for i in example_generator(4)])
	[0, 1, 2, 3]

'''


def get_head(head=''):
    '''Searches for a transform node named '*_head' in the scene.
    Args:
            head (str, optional):

    Returns:
            str: mesh name with prefix "_head"

    '''
    if head:
        return head
    meshes = cmds.ls('*_head', tr=True)
    if meshes and len(meshes) == 1:
        head = meshes[0]
    elif not meshes:
        sys.exit('No mesh with the prefix _head in the scene')
    else:
        sys.exit(
            'More than one object with the prefix _head in the scene \n %s' % meshes)
    return head


def get_teeth(teeth=''):
    '''Searches for a transform node named '*_teeth' in the scene.

    Returns:
            str: mesh name with prefix "_teeth"

    '''
    if not teeth:
        meshes = cmds.ls('*_teeth', tr=True)
        if meshes and len(meshes) == 1:
            teeth = meshes[0]
        elif not meshes:
            sys.exit('No mesh with the prefix _teeth in the scene')
        else:
            sys.exit(
                'More than one object with the prefix _teeth in the scene \n %s' % meshes)
    return teeth


def mapping(mesh, folder, set_mapping=False, cubes=[], mapping={}, female=False):
    '''Gets or set bone mapping for a character, bone per vertex correspondance.
            Since bones are constrained to vertices.
            And vertices are driven with a blendshapes.

    Args:
            mesh (str): transform object name mapping will be applied to.
            folder (str): path to bone mapping files that contain dictionary,
                    dumped with a pickle 
            set_mapping (bool, optional): used with cubes and mapping params.
                    Defaults to False
                    Sets custom mapping for a character
            cubes (list, optional): used with set and mapping params.
                    Cubes that visualize joint placement
            mapping (dict, optional): used with set and cubes params.
                    Bone per vertex correspondance

    Returns:
            dict: default or custom bone per vertex correspondance for a '*_head' mesh

    if 'head' in mesh:
            default_map_name = 'head_bones_mapping.txt'

    elif 'teeth' or 'mouth' in mesh:
            default_map_name = 'teeth_bones_mapping.txt'

    else:
            sys.exit('No pattern for %s found' % mesh)
    '''
    if female:
        default_map_name = 'female_bones_mapping.txt'
    else:
        default_map_name = 'male_bones_mapping.txt'
    cur_map_name = '%s_%s' % (mesh.split('_')[0], default_map_name)

    default_map_path = os.path.join(folder, default_map_name)
    cur_map_path = os.path.join(folder, cur_map_name)

    if os.path.exists(cur_map_path):
        path = cur_map_path
    elif os.path.exists(default_map_path):
        path = default_map_path
    else:
        sys.exit('Neither Default nor Chr mapping file found')

    with open(path, 'rb') as bone_map:
        mapping = pickle.loads(bone_map.read())

    if set_mapping == True and cubes and mapping:

        upd_mapping = update_match(mapping, cubes)

        with open(cur_map_path, 'wb') as bone_map:
            pickle.dump(upd_mapping, bone_map)

        print 'Saved updated mapping to %s' % cur_map_path
        # return upd_mapping
    else:
        print 'Loaded mapping from %s' % path
        return mapping


def get_length(jnt_coord, vtx_coord):
    ''''''
    vtx_vector = MVector(vtx_coord)
    jnt_vector = MVector(jnt_coord)

    vector_position = vtx_vector - jnt_vector
    vector_length = vector_position.length()
    return vector_length


def set_cubes(mapping):
    cubes = []
    head = get_head()

    for vtx, jnt in mapping.iteritems():
        cube = cmds.polyCube(name=jnt + '_cube', d=0.15, w=0.15, h=0.15)[0]
        vtx_pos = cmds.pointPosition(head + vtx, world=True)
        cmds.xform(cube, t=vtx_pos, ws=True)
        cubes.append(cube)

    cubes_group = cmds.group(cubes, name='cubes')
    return cubes_group


def get_pos(a):
    a_pos = cmds.xform(a, translation=True,
                       query=True,
                       worldSpace=True)
    return a_pos


def get_coords(objects):
    pos = {}
    for o in objects:
        o_pos = cmds.xform(o, translation=True,
                           query=True,
                           worldSpace=True)
        pos[o] = o_pos
    return pos


def compare_pos(a, b):
    a_pos = cmds.xform(a, translation=True,
                       query=True,
                       worldSpace=True)
    b_pos = cmds.xform(b, translation=True,
                       query=True,
                       worldSpace=True)

    if MVector(a_pos) == MVector(b_pos):
        return True
    else:
        return False
    '''
	true_false = []
	for a_v, b_v in zip(a_pos, b_pos):
		if round(a_v, 2) == round(b_v, 2):
			true_false.append(True)
		elif round(a_v, 0) == round(b_v, 0):
			true_false.append(True)
			print 'Not certain about match'
		else:
			true_false.append(False)
	'''


def update_match(mapping, cubes):

    if not cubes:
        sys.exit('No Cubes found in scene.\nSet new bone position first.')

    head = get_head()
    upd_match = {}

    for vtx, jnt in mapping.iteritems():
        cube = jnt + '_cube'
        if cmds.objExists(cube):
            if compare_pos(head + vtx, cube) == True:
                upd_match[vtx] = jnt
            else:
                print 'cube %s moved' % cube
                vtx = '.vtx[%s]' % get_closest(cube)
                upd_match[vtx] = jnt
        else:
            sys.exit('Cube %s not found' % cube)
    return upd_match


def get_closest(element, obj=''):
    if not obj:
        obj = get_head()
    vtxs = cmds.polyEvaluate(obj, v=True)

    check_value = float('inf')
    current_vtx = ''
    element_pos = get_pos(element)

    for vtx in range(0, vtxs + 1):
        l = get_length(get_pos(obj + '.vtx[%s]' % vtx), element_pos)
        if l < check_value:
            check_value = l
            match_l = vtx

    return match_l


def set_bones(mesh, bone_mapping):
    '''Constrains facial bones to a certain vertices. 
                    Position is taken from bone per vertex mapping dictionary

    Args:
            mesh (str): transform object name.
            bone_mapping (dict): bone per vertex mapping dictionary

    Returns:
            list: temporary objects, locators, groups, to be deleted later

    '''
    tmp_stuff = []
    # Constrain joints to vertices
    for vtx, jnt in bone_mapping.iteritems():
        old_loc_list = cmds.ls('*LOC*', flatten=True)
        cmds.select(mesh + vtx)

        HZrivet.UI.HZrivet_finalCC()

        current_loc_list = cmds.ls('*LOC*', flatten=True, tr=True)
        loc = [loc for loc in current_loc_list if loc not in old_loc_list]

        vtx_pos = cmds.pointPosition(mesh + vtx, world=True)
        new_loc = cmds.spaceLocator()
        new_group = cmds.group(new_loc)

        tmp_stuff.append(loc[0])
        tmp_stuff.append(new_group)
        # Align joint to the world of the parent joint
        # Breaks the model in editor
        # cmds.joint(jnt, e=True, oj='none', zso=True)

        cmds.xform(jnt, t=vtx_pos, ws=True)
        cmds.xform(new_group, t=vtx_pos, ws=True)

        # Now, not needed, because bones often have connections
        # cmds.makeIdentity(jnt)

        cmds.pointConstraint(loc[0], new_group, mo=True)
        cmds.orientConstraint(loc[0], new_group, mo=True)
        cmds.parentConstraint(new_loc, jnt, mo=True)

    tmp = cmds.group(tmp_stuff, name='tmp')
    return tmp


def get_closest_vtx_bone_match(obj, jnts):
    ''''''
    vtxs_pos = get_vtxs_coords(obj)
    jnts_pos = get_coords(jnts)

    match = {}

    for jnt, jnt_pos in jnts_pos.iteritems():
        check_value = float('inf')
        current_vtx = ''

        for vtx, vtx_pos in vtxs_pos.iteritems():
            vtx_length = get_length(jnt_pos, vtx_pos)
            if vtx_length < check_value:
                check_value = vtx_length
                current_vtx = vtx
        match['.vtx[%s]' % current_vtx] = jnt
    return match


def set_bip_rom(start=0, angle=45, fxgraph=False, skeleton='new'):
    '''Sets rotation for each of the predefined joints at x,y,z axis.
                    Is a part of blendshapes to skin process.

    Returns:
       None

    '''
    if skeleton == 'new':
        jnts = ['driv_Bip01_Head',
                'driv_Bip01_Neck1',
                'driv_Bip01_Neck']
        head_mapping = ['head_yaw_right',
                        'head_yaw_left',
                        'head_roll_left',
                        'head_roll_right',
                        'head_pitch_up',
                        'head_pitch_down',
                        'neck1_yaw_right',
                        'neck1_yaw_left',
                        'neck1_roll_left',
                        'neck1_roll_right',
                        'neck1_pitch_up',
                        'neck1_pitch_down',
                        'neck_yaw_right',
                        'neck_yaw_left',
                        'neck_roll_left',
                        'neck_roll_right',
                        'neck_pitch_up',
                        'neck_pitch_down']
    elif skeleton == 'old':
        jnts = ['Bip01_Head',
                'Bip01_Neck']
        head_mapping = ['head_yaw_right',
                        'head_yaw_left',
                        'head_roll_left',
                        'head_roll_right',
                        'head_pitch_up',
                        'head_pitch_down',
                        'neck_yaw_right',
                        'neck_yaw_left',
                        'neck_roll_left',
                        'neck_roll_right',
                        'neck_pitch_up',
                        'neck_pitch_down']

    # Fedor's code eval(str(rotates).replace('90','60'))
    # Get nested list of rotates for attributes
    rotates = []

    for n in xrange(3):

        for mp in ['-', '']:
            temp = [0, 0, 0]
            temp[n] = int(mp + str(angle))
            rotates += [temp]

    ''' 
	rotates = [[-45,0,0],
				[45,0,0],
				[0,-45,0],
				[0,45,0],
				[0,0,-45],
				[0,0,45]]
	'''
    head_frames = range(start + 1, start + 1 + len(head_mapping))
    head_fxgraph = ''
    # Info for fxgraph. Placed in batch.txt.
    for head_name, head_frame in zip(head_mapping, head_frames):
        print head_name, head_frame
        head_fxgraph += '%s_%s\n' % (head_name, str(head_frame))

    if fxgraph:
        return head_fxgraph

    cmds.setKeyframe(jnts, time=start)
    frame = start + 1

    for jnt in jnts:

        for rot in rotates:
            cmds.xform(jnt, ro=(rot))
            cmds.setKeyframe(jnts, time=(frame, frame))
            frame += 1

        cmds.xform(jnt, ro=(0, 0, 0))
        cmds.setKeyframe(jnts, time=(frame, frame))

    return max(head_frames)



def set_eyes_rom(start=0, fxgraph=False, skeleton='new'):
    start = int(start)
    eye_mapping = ['Eyeball_L_Down',
                   'Eyeball_L_Up',
                   'Eyeball_L_In',
                   'Eyeball_L_Out',
                   'Eyeball_R_Down',
                   'Eyeball_R_Up',
                   'Eyeball_R_Out',
                   'Eyeball_R_In']
    if skeleton == 'new':
        jnts = ['bn_eye_l', 'bn_eye_r']
    elif skeleton == 'old':
        jnts = ['BN_Eyeball_L', 'BN_Eyeball_R']
    # jnts = ['BN_Eyeball_L', 'BN_Eyeball_R']
    rotates = [[-30, 0, 0],
               [30, 0, 0],
               [0, 0, -40],
               [0, 0, 40]]
    eye_frames = range(start + 1, start + 1 + len(eye_mapping))
    fxgraph_text = ''
    
    for eye_name, eye_frame in zip(eye_mapping, eye_frames):
        print eye_name, eye_frame
        fxgraph_text += '%s_%s\n' % (eye_name, str(eye_frame))

    if fxgraph:
        return fxgraph_text    
    cmds.setKeyframe(jnts, time=start)
    frame = start + 1

    for jnt in jnts:

        for rot in rotates:
            cmds.xform(jnt, ro=(rot))
            cmds.setKeyframe(jnts, time=(frame, frame))
            frame += 1

        cmds.xform(jnt, ro=(0, 0, 0))
        cmds.setKeyframe(jnts, time=(frame, frame))

    return max(eye_frames)



def set_tmp_skin():
    '''Set skin cluster for the head mesh only on the predefined joints.
                    Ommiting those, that not needed while skin calculation.
                    Is a part of blendshapes to skin process.

    Returns:
            str: skin cluster name

    '''
    head = get_head()
    tmp_bones = [u'Bip01_Spine3', u'driv_Bip01_Neck', u'driv_Bip01_Neck1', u'driv_Bip01_Head',
                 u'bn_lid_l_d_02', u'bn_lid_l_u_05', u'bn_lid_l_u_04', u'bn_lid_l_d_03', u'bn_lid_l_u_06',
                 u'bn_lid_l_u_07', u'bn_lid_l_d_04', u'bn_lid_l_d_05', u'bn_lid_l_u_08', u'bn_lid_l_u_03',
                 u'bn_br_l_08', u'bn_br_l_09', u'bn_lid_l_u_01', u'bn_lid_l_u_02', u'bn_br_l_04',
                 u'bn_br_l_05', u'bn_br_l_06', u'bn_br_l_07', u'bn_br_l_01', u'bn_br_l_02', u'bn_br_l_03',
                 u'bn_nose_l', u'bn_mouth_l_01', u'bn_cheek_l_04', u'bn_cheek_l_02', u'bn_cheek_l_03',
                 u'bn_cheek_l_05', u'bn_mouth_l_02', u'bn_mouth_l_03', u'bn_cheek_l_06', u'bn_cheek_l_07',
                 u'bn_mouth_l_04', u'bn_lip_l_u_02', u'bn_lip_l', u'bn_lip_l_u_04', u'bn_lip_l_u_05',
                 u'bn_lip_c_u_02', u'bn_lip_l_u_01', u'bn_lip_c_u', u'bn_lip_c_u_01', u'bn_lip_l_u_03',
                 u'bn_cheek_l_01', u'bn_cheek_r_06', u'bn_lip_r', u'bn_lip_r_u_04', u'bn_mouth_r_02',
                 u'bn_cheek_r_04', u'bn_cheek_r_07', u'bn_lip_r_u_01', u'bn_lip_r_u_05', u'bn_br_r_01',
                 u'bn_lid_r_d_05', u'bn_lid_r_d_03', u'bn_lid_r_d_02', u'bn_lid_r_u_02', u'bn_lid_r_d_04',
                 u'bn_lid_r_u_08', u'bn_lid_r_u_07', u'bn_lid_r_u_03', u'bn_br_r_02', u'bn_cheek_r_03',
                 u'bn_cheek_r_02', u'bn_mouth_r_01', u'bn_lid_r_u_01', u'bn_br_r_05', u'bn_br_r_04',
                 u'bn_br_r_07', u'bn_cheek_r_05', u'bn_nose_r', u'bn_lid_r_u_06', u'bn_lid_r_u_04',
                 u'bn_lid_r_u_05', u'bn_br_r_09', u'bn_br_r_08', u'bn_br_r_06', u'bn_br_r_03',
                 u'bn_lip_r_u_03', u'bn_mouth_r_03', u'bn_mouth_r_04', u'bn_lip_r_u_02', u'bn_cheek_r_01',
                 u'bn_lid_l_d_01', u'bn_nose_c', u'bn_br_c', u'bn_chin_l', u'bn_chin_r', u'bn_chin_c',
                 u'bn_lip_c_d_02', u'bn_lip_r_d_05', u'bn_lip_l_d_05', u'bn_lip_c_d_01', u'bn_lip_r_d_03',
                 u'bn_lip_l_d_03', u'bn_lip_l_d_04', u'bn_lip_r_d_04', u'bn_lip_r_d_01', u'bn_lip_l_d_01',
                 u'bn_lip_c_d', u'bn_lip_r_d_02', u'bn_lip_l_d_02', u'bn_lid_r_d_01', u'bn_lip_r_u_06',
                 u'bn_lip_l_u_06']

    sk = cmds.skinCluster(tmp_bones, head, tsb=True)
    cmds.setAttr("%s.envelope" % sk[0], 0)
    return sk


def get_joints(invert=False):
    '''Gets all the child joints from the 'Bip01'

    Returns:
            list: all joints in hierarchy

    '''
    root = 'Bip01'
    if not cmds.objExists(root):
        return
    cmds.select(root, hierarchy=True)
    selection = cmds.ls(sl=True, fl=True)
    nubs = cmds.ls('*Nub*', type='joint')
    if nubs:
        cmds.select(nubs, d=True)
    jnts = cmds.ls(type='joint', selection=True)
    cmds.select(clear=True)
    if invert:
        return [o for o in selection if o not in jnts]
    else:
        return jnts


def get_meshes():
    '''Gets all the transform meshes node names from a scene

    Returns:
            list: all meshes in scene

    '''
    objects = cmds.ls('*', type='mesh')
    meshes = cmds.listRelatives(objects, parent=True)
    if not meshes:
        return
    meshes = list(set(meshes))
    return meshes

def unlock_attributes(o):
        locked = cmds.listAttr(o, l=True)
        if locked:
            
            for atr in locked:
                cmds.setAttr('%s.%s' % (o, atr), lock=0)    


def reset(objects):
    '''Deletes all connections and history from a given objects.
                    And freezes transform.

    Args:
            objects (list): string list of objects

    Returns:
            None:

    '''
    axis = ['scaleX', 'scaleY', 'scaleZ', 'rotateX', 'rotateY',
            'rotateZ', 'translateX', 'translateY', 'translateZ']

    cmds.currentTime(0)

    for o in objects:
        cmds.delete(o, ch=True, cn=True, tac=True, e=True)
        unlock_attributes(o)

        sk = cmds.listConnections(o, type='skinCluster')
        if sk:
            cmds.delete(sk)

        bp = cmds.listConnections(o, type='dagPose')
        if bp:
            cmds.delete(bp)

        for a in axis:
            conn = cmds.listConnections(o + "." + a, s=True, p=True)
            if conn:
                cmds.disconnectAttr(conn[0], o + "." + a)

    cmds.delete(objects, c=True)
    cmds.delete(objects, ch=True)
    cmds.makeIdentity(objects, apply=True)


def add_zeroes(num, digits=2):
    '''Gerenerates zeroes in front of the given digit.

    Args:
            num (int): input digit that is processed.
            digits (int, optional): quantity of digits.

    Returns:
            str:

    Examples:
            >>> add_zeroes(2, digits=2)
            '02'
            >>> add_zeroes(2, digits=3)
            '002'

    '''
    if isinstance(num, int) and isinstance(digits, int):
        num = str(num)
        zeroes_quantity = digits - len(num)
        if zeroes_quantity > 0:
            zeroes = (str(0) * zeroes_quantity)
            return zeroes + num
        elif zeroes_quantity == 0:
            return num
        else:
            print 'digits', digits, 'less than', num, 'returning', num
            return num
    else:
        exit_message = str(
            ['"update_number()" accepts "int" only, got', type(num), type(digits)])
        sys.exit(exit_message)


def create_bip_blendshapes(start=1, end=19, head=''):
    if not head:
        head = get_head()

    for key in range(start, end):
        cmds.currentTime(key, edit=True)
        cmds.select(head)
        new_name = cmds.duplicate()
        cmds.rename(new_name[0], head + '_' + add_zeroes(key, digits=2))
        cmds.delete(ch=True)


def prepare_buttons(path):
    '''
    Take .py or .pyc path to script
    Return dictionary button label:function
    '''

    path = path.replace('.pyc', '.py')

    with open(path, 'r+') as cmds:
        commands = cmds.read().splitlines()

    defs = [d for d in commands if 'def ' in d]
    to_del = ['def ', '(*args):']
    buttons = []

    for d in defs:

        for i in to_del:
            d = d.replace(i, '')
        buttons.append(d)

    labeled_buttons = {}

    for b in buttons:
        labeled_buttons[b.replace('_', ' ')] = 'c.' + b

    return labeled_buttons


def get_blendshape_node(mesh):
    '''
    Description:
    Example:
    input: transform mesh
    output: blendshape name if connected
    '''
    bls_set = cmds.ls('blendShape*', type='objectSet')

    for bl_set in bls_set:
        conns = cmds.listConnections(bl_set)
        if mesh in conns:
            bl = cmds.ls(conns, type='blendShape')
            return bl[0]
    print 'No blendshape connected to', mesh


def duplicate_blendshapes(bl=''):
    '''Duplicates all blendshapes of a node by calling them one by one.
            Number prefix of duplicated mesh is taken from a blendshape name if present.
            Otherwise, Maya takes care of a prefix by itself.

    Args:
            None:

    Returns:
            list: duplicated meshes

    Examples:
            >>> duplicate_blendshapes()
            ['yermak_head_01', 'yermak_head_02']

    '''
    mesh = cmds.ls(sl=True, flatten=True)[0]
    if not bl:
        bl = get_blendshape_node(mesh)
    cmds.currentTime(0)
    targets = cmds.blendShape(bl, t=True, q=True)
    # If blendshape meshes were deleted from scene
    if not targets:
        targets = cmds.listAttr(bl + '.w', multi=True)
    # Generate dict for set each blendshapes in range to 1 infl per call
    weights_bls = {}
    renamed = []

    group_name = '%s_bls_duplicated' % mesh
    cmds.group(name=group_name, empty=True)
    # Get index mapping for blendshape targets.
    # Example: {0:'yermak_19', 1:'yermak_20'}
    for t in range(0, len(targets)):
        weight = [(i, 0) for i in range(0, len(targets))]
        weight[t] = (t, 1)
        weights_bls[targets[t]] = weight

    for bl_mesh, bl_weight in weights_bls.iteritems():
        cmds.blendShape(bl, w=bl_weight, edit=True)
        d_name = cmds.duplicate(mesh)
        cmds.parent(d_name, group_name)
        new_name = cmds.rename(d_name[0], bl_mesh)
        renamed.append(new_name)
    
    return renamed


def skin_eyes():
    '''
    Prepare eye for export to 4A engine
    Add the skin and the proper weights
    '''
    # Add check for skinscuster
    eyes = cmds.ls('*l_eye', '*r_eye')

    if not eyes:
        sys.exit('No match for the pattern *l_eye *r_eye')
    elif len(eyes) != 2:
        sys.exit('More or less than 2 objects match the pattern *l_eye *r_eye')

    reset(eyes)
    # Center pivot
    cmds.xform(eyes, cp=True, p=True)

    l_prefix = '_l'
    r_prefix = '_r'

    jnts_list = ['bn_eye_r', 'bn_eye_l', 'Bip01_Head', 'Bip01']

    for jnt in jnts_list:
        if not cmds.objExists(jnt):
            sys.exit('joint not found', jnt)

    for eye in eyes:
        jnts_hi = get_joints()

        if l_prefix in eye:
            eye_jnt = 'bn_eye_l'
        elif r_prefix in eye:
            eye_jnt = 'bn_eye_r'
        else:
            sys.exit('No prefix match')

        # Align bone to eyes
        # Should add a check tor keys and connections on bones
        # To prevent jumping thile grabbing timeline
        p_constr = cmds.pointConstraint(eye, eye_jnt)
        cmds.delete(p_constr)

        skin_cluster = cmds.skinCluster(jnts_hi, eye, tsb=True)
        # skin_cluster = mel.eval('findRelatedSkinCluster("%s")' % object)
        cmds.skinPercent(skin_cluster[0],
                         eye + '.vtx[*]',
                         transformValue=[(eye_jnt, 0.99),
                                         (jnts_list[2], 0.01)])
        print 'Prepared', eye


def dict_io(path, dict={}, get=False, set=False):
    if get:
        with open(path, 'rb') as dict_path:
            dict = pickle.loads(dict_path.read())
            print '# Loaded dictionary from', path
        return dict
    elif set and dict:
        with open(path, 'wb') as dict_path:
            pickle.dump(dict, dict_path)
            print '# Saved dictionary to', path
    else:
        sys.exit('Command not specified')


def add_bones_to_skin_cluster(mesh, skin_cluster):
    existing_bones = cmds.skinCluster(skin_cluster, query=True, inf=True)
    to_add_bones = [
        bone for bone in get_joints() if bone not in existing_bones]
    if to_add_bones:
        cmds.skinCluster(skin_cluster, edit=True, ai=to_add_bones, wt=0)


def get_info_from_xml(path):
    '''
    takes path to .xml file
    return dict 'skin cluster name':[jnts]
    '''

    root = xml.etree.ElementTree.parse(path).getroot()

    # set the header info
    for atype in root.findall('headerInfo'):
        fileName = atype.get('fileName')

    info = {}
    jnts = []
    for atype in root.findall('weights'):
        jnts.append(atype.get('source'))
        #shape = atype.get('shape')
        skin_cluster = atype.get('deformer')

    info[skin_cluster] = jnts
    return info


def get_skin_cluster(mesh):
    skin_cluster = mel.eval('findRelatedSkinCluster "%s"' % mesh)
    if not skin_cluster:
        skin_cluster = cmds.ls(cmds.listHistory(mesh), type='skinCluster')
        if skin_cluster:
            skin_cluster = skin_cluster[0]
        else:
            skin_cluster = None
    return skin_cluster


def set_skin_cluster(mesh):

    global xml_folder

    mesh_xml = os.path.join(xml_folder, mesh + '.xml')

    if not os.path.exists(mesh_xml):
        print 'No saved skin cluster found for %s' % mesh
        return None
    else:
        info = get_info_from_xml(mesh_xml)
    # No check for skin cluster name match in scene yet.
    jnts = info.values()[0]
    skin_cluster = info.keys()[0]

    if not exists(jnts):
        print 'Not enough joints to apply saved skin to'
        return None
    if exists(skin_cluster):
        print 'Skin cluster already exists with a given name'
        return None
    cmds.skinCluster(mesh, jnts, name=skin_cluster, mi=4)
    return skin_cluster


def exists(objects):
    '''
    Takes strings and lists
    Return True or False
    '''

    if isinstance(objects, str) or isinstance(objects, unicode):
        if cmds.objExists(objects):
            return True

    elif isinstance(objects, list):
        true_false = []
        for o in objects:
            if cmds.objExists(o):
                true_false.append(True)
            else:
                true_false.append(False)
        if False in true_false:
            return False
        else:
            return True
    else:
        print 'Types "str", "list" are accepted only'
        return False


def fix_skin_cluster_name(mesh, skin_cluster):
    '''Renames skin cluster with a mesh name + prefix "_sc"

    Args:
            mesh (str): transform object with a skin cluster
            skin_cluster (str): skin cluster node name

    Returns:
            str: updated mesh skin cluster name

    '''
    prefix = '_sc'
    if skin_cluster != mesh + prefix:
        skin_cluster_name = cmds.rename(skin_cluster, mesh + prefix)
        return skin_cluster_name
    else:
        return skin_cluster


def export_weights():

    global xml_folder

    cmds.currentTime(0)

    objects = cmds.ls(selection=True, transforms=True, flatten=True)

    if not objects:
        print 'Nothing is selected to save weights from'
        return

    object_and_skin_cluster = {}

    for o in objects:
        skin_cluster = get_skin_cluster(o)
        if skin_cluster:
            skin_cluster = fix_skin_cluster_name(o, skin_cluster)
            object_and_skin_cluster[o] = skin_cluster

    if not object_and_skin_cluster:
        print 'No skin cluster was found on selected'
        return

    for o, skin_cluster in object_and_skin_cluster.iteritems():
        add_bones_to_skin_cluster(o, skin_cluster)
        cmds.deformerWeights(o + '.xml',
                             path=xml_folder,
                             ex=True,
                             deformer=skin_cluster,
                             method='index')


def import_weights():

    global xml_folder

    cmds.currentTime(0)

    objects = cmds.ls(selection=True, transforms=True, flatten=True)

    if not objects:
        print 'Nothing is selected to import weights from'
        return

    for o in objects:
        skin_cluster = get_skin_cluster(o)
        if skin_cluster:
            cmds.skinCluster(skin_cluster, unbind=True, edit=True)
        skin_cluster = set_skin_cluster(o)
        if skin_cluster:
            cmds.deformerWeights(o + '.xml',
                                 path=xml_folder,
                                 im=True,
                                 deformer=skin_cluster,
                                 method='index')
            cmds.skinCluster(
                skin_cluster, forceNormalizeWeights=True, edit=True)
            add_bones_to_skin_cluster(o, skin_cluster)
            print "# Imported deformer weights from '%s'. #" % (os.path.join(xml_folder, o + '.xml'))


def get_num_prefix(s):
    bl_prefix = s.split('_')[-1]
    return int(''.join(chr for chr in bl_prefix if chr.isdigit()))


def set_blendshapes(head=''):

    if not head:
        head = get_head()
    bls = check_blendshapes(head)

    # Blendshapes may not be properly ordered. 1,2,3,5...
    # That is why a dictionary mapping is used
    bls_order = {}

    for i in range(0, len(bls)):
        bls_order[i] = bls[i]

    bl = cmds.blendShape(bls + [head])[0]
    zero_weights = [(i, 0) for i in range(0, len(bls))]
    cmds.blendShape(bl, w=zero_weights, edit=True)
    cmds.setKeyframe(bl, time=0)
    frames = []

    for key in bls_order.keys():
        frames.append(get_num_prefix(bls_order[key]))

    frame_range = [frame for frame in range(0, max(frames))]

    # Key all blendshapes along the timeline range
    for frame in frame_range:
        cmds.blendShape(bl, w=zero_weights, edit=True)
        cmds.setKeyframe(bl, time=frame)

    for key in bls_order.keys():
        bl_num = get_num_prefix(bls_order[key])
        cmds.blendShape(bl, w=zero_weights, edit=True)
        cmds.blendShape(bl, w=(key, 1.0), edit=True)
        cmds.setKeyframe(bl, time=bl_num)
    return bl


def check_blendshapes(head):
    # Find all blendshapes in scene
    #head = get_head()
    head_template = '_'.join(head.split('_')[:-1])
    head_template_match = cmds.ls(head_template + '*', tr=True)
    head_bl = [i for i in head_template_match if i.split('_')[-1].isdigit()]
    if not head_bl:
        sys.exit('No blendshapes')
    head_bl.sort()
    return head_bl


def get_vtxs_coords(mesh, relative=False):
    vtxs_coords = {}
    vtxs = cmds.ls(mesh + '.vtx[*]', fl=True)

    for vtx in vtxs:
        if relative:
            coord = cmds.xform(vtx, q=True, t=True, r=True)
        else:
            coord = cmds.xform(vtx, q=True, t=True, ws=True)
        vtx_id = ''.join(i for i in vtx.split('.')[1] if i.isdigit())
        vtxs_coords[vtx_id] = coord
    return vtxs_coords


def calc_coords(a_coords, b_coords, add=False, sub=False):
    '''
    Perfoms add or substract operations on a [x, y, z]
    input: [float, float, float]
    output: [float, float, float]
    '''
    a_vector = MVector(a_coords)
    b_vector = MVector(b_coords)
    if add:
        result = list(a_vector + b_vector)
    elif sub:
        result = list(b_vector - a_vector)
    else:
        sys.exit('Only "sub" or "add" flags supported')
    # Operations are correct even without float formatting
    #diff = [float('%.10f' % c) for c in diff]
    return result


def set_coords(mesh, coords):

    for vtx_id, coords in coords.iteritems():
        cmds.xform(mesh + '.vtx[%s]' % vtx_id, t=coords, ws=True)


def get_vtxs_delta(t_coords, a_coords, b_coords):
    delta = {}
    vtx_ids = [id for id in a_coords.keys()]

    for vtx_id in vtx_ids:
        if a_coords[vtx_id] == b_coords[vtx_id]:
            continue
        diff_coords = calc_coords(a_coords[vtx_id], b_coords[vtx_id], sub=True)
        delta_coords = calc_coords(t_coords[vtx_id], diff_coords, add=True)
        delta[vtx_id] = delta_coords

    return delta


def set_delta_mesh(t_mesh, a_mesh, b_mesh):

    a_coords = get_vtxs_coords(a_mesh)
    b_coords = get_vtxs_coords(b_mesh)
    t_coords = get_vtxs_coords(t_mesh)

    if len(a_coords) != len(b_coords) != len(t_coords):
        exit_message = 'Different length of dicts: %s, %s, %s' % (
            len(a_coords), len(b_coords), len(t_coords))
        sys.exit(exit_message)

    if a_coords == b_coords == t_coords:
        sys.exit('Compared dictionaries are identical')

    vtxs_delta = get_vtxs_delta(t_coords, a_coords, b_coords)
    delta_mesh = cmds.duplicate(t_mesh, n=b_mesh + '_delta')[0]
    set_coords(delta_mesh, vtxs_delta)
    print delta_mesh
    return delta_mesh


def calc_delta_on_meshes(mapping):
    '''
    eye_l_up_closed 64
    eye_r_up_closed 65
    eye_l_down_closed 66
    eye_r_down_closed 67
    eye_l_left_closed 68
    eye_r_left_closed 69
    eye_l_right_closed 70
    eye_r_right_closed 71
    delta_mapping = {57:64, 56:65, 54:66, 55:67, 59:68, 58:69, 60:70, 61:71}
    '''
    # delta_mapping = {57:64, 56:65, 54:66, 55:67, 59:68, 58:69, 60:70, 61:71}
    # calc_delta_on_meshes(delta_mapping)
    template_mesh = get_head()

    for a, b in delta_mapping.iteritems():
        a_mesh = cmds.listRelatives(
            cmds.ls('*%s*' % a, type='mesh'), parent=True)[0]
        b_mesh = cmds.listRelatives(
            cmds.ls('*%s*' % b, type='mesh'), parent=True)[0]
        if not a_mesh and not b_mesh:
            exit_message = 'Meshes not found with the %s or %s prefix' % (a, b)
            sys.exit(exit_message)
        delta_mesh = set_delta_mesh(template_mesh, a_mesh, b_mesh)
        cmds.rename(delta_mesh, b_mesh + '_delta')


def get_blend_multiplier(coords, threshold=3):
    '''Gets data for smooth dividing mesh on to symmetrical parts
            with a blend between parts given by threshold.
            Uses to divide a scanned emotion blendshapes on the left and the right sides.
            Default division axis is X.

    Args:
            coords (list): vertex coordinates [x,y,z]
            threshold (int, optional): blend half length. In units.
                    Counted from the center of a mesh

    Returns:
            dict, dict: blend mapping for both sides in a format:
            '1': 0.5, where key is vertex id in "str", 05 is blend value

    '''
    axis = 0  # x in x, y, z

    max_coord = max([x[axis] for x in coords.values()])
    min_coord = min([x[axis] for x in coords.values()])
    center_coord = (max_coord + min_coord) / 2

    blend_max = center_coord + threshold
    blend_min = center_coord - threshold
    blend_length = threshold * 2

    positive_blend = {}
    negative_blend = {}

    for id, coord in coords.iteritems():
        axis_coord = coord[axis]
        if axis_coord > blend_max:
            positive_blend[id] = 1
        elif axis_coord < blend_min:
            negative_blend[id] = 1
        else:
            positive_blend_value = (axis_coord - blend_min) / blend_length
            positive_blend[id] = positive_blend_value
            # Sinse a multiplier will never be greater than 1
            negative_blend[id] = 1 - positive_blend_value

    return positive_blend, negative_blend


def set_blend_coords(blend, diff, mesh):
    '''Applies a relative transform on a mesh with a multiplier

    Args:
            blend (dict): vtx id: multiplier based on distance.
            diff (dict): vtx id: [x,y,z] difference between tempate mesh,
                    and som emotion.
            mesh (str): mesh name transform are applied to.

    Returns:
            None:

    '''
    for vtx_id in blend.keys():
        pos_blend_coord = [x * blend[vtx_id] for x in diff]
        cmds.xform(mesh + '.vtx[%s]' % vtx_id, t=blend, r=True)


def divide_mesh(template_mesh, divided_mesh, threshold=3):
    '''Divides mesh on the left and the right symmetrical sides.
            With a smooth linear blend inbetween.
            Uses to divide a scanned emotion blendshapes.
            Template mesh is duplicated.

    Args:
            template_mesh (str):
            divided_mesh (str):

    Returns:
            list: divided meshes names

    '''
    l_mesh = cmds.duplicate(template_mesh, name=divided_mesh + '_l')[0]
    r_mesh = cmds.duplicate(template_mesh, name=divided_mesh + '_r')[0]

    template_coords = get_vtxs_coords(template_mesh, relative=True)
    div_coords = get_vtxs_coords(divided_mesh, relative=True)

    pos_blend_values, neg_blend_values = get_blend_multiplier(
        template_coords, threshold=threshold)

    for vtx_id in pos_blend_values.keys():
        diff_coords = calc_coords(
            template_coords[vtx_id], div_coords[vtx_id], sub=True)
        pos_blend_coord = [x * pos_blend_values[vtx_id] for x in diff_coords]
        cmds.xform(r_mesh + '.vtx[%s]' % vtx_id, t=pos_blend_coord, r=True)

    for vtx_id in neg_blend_values.keys():
        diff_coords = calc_coords(
            template_coords[vtx_id], div_coords[vtx_id], sub=True)
        neg_blend_coord = [x * neg_blend_values[vtx_id] for x in diff_coords]
        cmds.xform(l_mesh + '.vtx[%s]' % vtx_id, t=neg_blend_coord, r=True)
    print 'Divided', divided_mesh
    return [l_mesh, r_mesh]


def get_neibour_faces(face):
    edges = cmds.polyListComponentConversion(face, ff=True, te=True)
    # get neighbour faces
    faces = cmds.polyListComponentConversion(edges, fe=True, tf=True, bo=True)
    return faces


def check_bones_threshold(faces, skin_cluster):
    threshold = 80
    bones_on_faces = cmds.skinPercent(skin_cluster, faces,
                                      transform=None, q=1, ib=0.001)
    bones_quantity = int(len(set(bones_on_faces)))
    if bones_quantity <= threshold:
        return True
    else:
        return False


def get_faces():
    mesh = cmds.ls(sl=True)[0]
    # a_mat, b_mat = get_faces()
    max_iter = 100
    skin_cluster = get_skin_cluster(mesh)
    max_random = cmds.polyEvaluate(mesh, f=True)

    for i in range(0, max_iter):
        random_face = '%s.f[%s]' % (mesh, random.randrange(0, max_random))
        faces = []
        faces.append(random_face)
        # 100 iterations of grow selection is enough to cover even the most hi
        # poly mesh
        for i in range(0, 100):
            if check_bones_threshold(faces, skin_cluster):
                # new_faces = faces+get_neibour_faces(faces)
                # Slow but a selection is more elegant
                # Fits my needs because right now using only 81 bones
                cmds.select(faces)
                mel.eval('GrowPolygonSelectionRegion;')
                new_faces = cmds.ls(sl=True, fl=True)
                if check_bones_threshold(new_faces, skin_cluster):
                    faces = new_faces
                else:
                    break
            else:
                break
        # Get the other faces
        cmds.select(faces)
        mel.eval('InvertSelection')
        inverted_faces = cmds.ls(sl=True, flatten=True)
        cmds.select(clear=True)

        if check_bones_threshold(inverted_faces, skin_cluster) and check_bones_threshold(faces, skin_cluster):
            print random_face, 'worked'
            return faces, inverted_faces
    sys.exit('100 iteration is not enough to divide the mesh on two materials')


def set_facefx_scale(root_only=False, biped_only=False, defined=[]):
    import skin_import_export
    start, end = get_timeline()

    jnts = get_joints()
    root_jnt = 'Bip01'
    meshes = get_meshes()
    reset(meshes)

    # Brute force approach to be confident for all meshes will be scaled
    # Apply one bone skin
    for mesh in meshes:
        cmds.skinCluster('Bip01_Head', mesh, tsb=True)

    # Make joints scalable
    for jnt in jnts:
        for a in ['scaleX', 'scaleY', 'scaleZ']:
            conn = cmds.listConnections(jnt + "." + a, s=True, p=True)
            if conn:
                cmds.disconnectAttr(conn[0], jnt + "." + a)

    # Works with old skeleton
    if root_only:
        cmds.xform(root_jnt, scale=(0.01, 0.01, 0.01))
    # For unknown reasons works sometimes when all skeleton scale spoils face joints
    elif biped_only and not defined:
        if cmds.objExists('driv_Bip01_Head'):
            face_jnts = cmds.listRelatives('driv_Bip01_Head', type='joint', ad=True)
        elif cmds.objExists('Bip01_Head'):
            face_jnts = cmds.listRelatives('Bip01_Head', type='joint', ad=True)
        else:
            sys.exit('No head joint presents in scene. Biped scale only not possible.')
        filtered_jnts = [j for j in jnts if j not in face_jnts]
        cmds.xform(filtered_jnts, scale=(0.01, 0.01, 0.01))
    elif defined:
        cmds.xform(defined, scale=(0.01, 0.01, 0.01))
    # Default scale
    else:
        cmds.xform(jnts, scale=(0.01, 0.01, 0.01))
    # Transfer and bake animation to locators
    locs = []
    constrs = []

    for jnt in jnts:
        cmds.select(clear=True)
        loc_name = cmds.spaceLocator(name=jnt + '_LOC')
        locs.append(loc_name[0])

        pc = cmds.pointConstraint(jnt, loc_name)
        constrs.append(pc[0])
        oc = cmds.orientConstraint(jnt, loc_name)
        constrs.append(oc[0])

    cmds.bakeResults(locs, time=(start, end + 1), sm=True)
    cmds.delete(constrs)

    # Freeze transformation
    reset(meshes)
    reset(jnts)

    # Birng the animation back to joints from locators
    for jnt in jnts:
        cmds.select(clear=True)
        loc_name = jnt + '_LOC'

        cmds.pointConstraint(loc_name, jnt)
        cmds.orientConstraint(loc_name, jnt)

    cmds.select(meshes)
    skin_import_export.import_weights_sp()
    cmds.bakeResults(jnts, time=(start, end + 1), sm=True)
    cmds.delete(locs)


def get_texture(mesh):
    shapesInSel = cmds.ls(mesh, dag=1, o=1, s=1)
    shadingGrps = cmds.listConnections(shapesInSel, type='shadingEngine')
    shaders = cmds.ls(cmds.listConnections(shadingGrps), materials=1)
    fileNode = cmds.listConnections('%s.color' % (shaders[0]), type='file')
    if fileNode:
        currentFile = cmds.getAttr("%s.fileTextureName" % fileNode[0])
        return currentFile
    else:
        return None


def create_shader(name, texture):
    shader = cmds.shadingNode("blinn", asShader=True, name=name)
    # a file texture node
    file_node = cmds.shadingNode("file", asTexture=True, name=name)
    # a shading group
    cmds.setAttr(file_node + '.fileTextureName', texture, type="string")

    shading_group = cmds.sets(
        renderable=True, noSurfaceShader=True, empty=True)
    # connect shader to sg surface shader
    cmds.connectAttr('%s.outColor' %
                     shader, '%s.surfaceShader' % shading_group)
    # connect file texture node to shader's color
    cmds.connectAttr('%s.outColor' % file_node, '%s.color' % shader)
    return shading_group


def assign_shader(object, s_group):
    try:
        cmds.sets(object, e=True, forceElement=s_group)
    except:
        print 'Cannot assign material to', object


def find_texture(texture):
    path = 't:/'
    name = os.path.basename(texture)
    for path, dirs, file_names in os.walk(path):
        for file_name in file_names:
            if file_name == name:
                new_texture = os.path.join(path, file_name)
                return new_texture
    print 'Texture %s not found on T drive. Leaving as is.' % texture
    return texture


def organize_scene_shaders():
    # Obtain texture files from shaders
    mesh_texture = {}
    for mesh in get_meshes():
        texture = get_texture(mesh)
        mesh_texture[mesh] = texture

    # Get all shaders in scene and delete them
    shaders = cmds.ls('*', mat=True)
    cmds.delete(shaders)

    for mesh, texture in mesh_texture.iteritems():
        new_texture = find_texture(texture)
        s_name = '%s_m' % mesh
        sg = create_shader(s_name, new_texture)
        assign_shader(mesh, sg)


def get_locators_in_scene():
    existing_locs_shapes = cmds.ls('*', type='locator', flatten=True)
    return [cmds.listRelatives(l, p=True)[0] for l in existing_locs_shapes]


def set_color_lps_rig(dict):
    object = cmds.ls(sl=True)[0]
    for loc, vtxs in dict.iteritems():
        cmds.select([object + '.' + v for v in vtxs])
        mel.eval("polyColorPerVertex -cdo -rgb 0.0 1.0 1.0;")


def create_lps_rig(dict, ctrls=[]):
    object = cmds.ls(sl=True)[0]
    cmds.select(object)
    # Fetching commands from mel LPC script.
    # Since now don't want to rewrite on python
    mel.eval("setDeformGeom();")
    loc_renaming_table = {}

    if not ctrls:
        ctrls = dict.keys()

    for ctrl in ctrls:
        existing_locs = get_locators_in_scene()
        vtxs = dict[ctrl]
        # time.sleep(1)
        tmp_ls = cmds.select([object + '.' + v for v in vtxs])
        # cmds.refresh()
        # time.sleep(1)
        if ctrl != 'excluded':
            mel.eval("addHandle();")
        else:
            mel.eval("addAnchor();")
        created_locs = get_locators_in_scene()
        created_loc = [l for l in created_locs if l not in existing_locs][0]
        loc_renaming_table[created_loc] = ctrl

    for loc in loc_renaming_table.keys():
        cmds.rename(loc, loc_renaming_table[loc])


def get_shader_info(mesh):

    shapes = cmds.ls(mesh, dag=1, o=1, s=1)
    shading_groups = cmds.listConnections(shapes, type='shadingEngine')
    shading_groups = list(set(shading_groups))
    shader_info = {}

    for shading_group in shading_groups:
        shader = cmds.ls(cmds.listConnections(shading_group), materials=1)
        print shader
        cmds.select(shading_group)
        shader_mesh = cmds.ls(selection=True, flatten=True)
        cmds.select(clear=True)
    
    # print shading_groups
    return len(shading_groups)
 
 
def print_shader_info():
    for m in get_meshes():
        print m, get_shader_info(m)


def get_timeline():
    start = cmds.playbackOptions(min=True, query=True)
    end = cmds.playbackOptions(max=True, query=True)
    return int(start), int(end)


def bake_animation_joints_to_locators(jnts=[]):
    '''First part of the operation, that consists of two steps.
    The second one is a function called "bake_animation_locators_to_joints"
    Transfer with a help of constraints animation from a given
    joins to locators. Keeps an animation when reparenting or scaling joints

    Args:
            jnts (list, optional): joints. If not specified, takes all joints
                    starting from "Bip01"

    Returns:
            dict: joint:locator mapping. Used later when returning an animation back
    '''
    start, end = get_timeline()

    if not jnts:
        jnts = get_joints()
    mapping = {}
    constrs = []
    # group_name = 'tmp_locs'

    for jnt in jnts:
        cmds.select(clear=True)
        loc_name = cmds.spaceLocator(name=jnt + '_LOC')[0]
        pc = cmds.pointConstraint(jnt, loc_name)
        oc = cmds.orientConstraint(jnt, loc_name)
        # sc = cmds.scaleConstraint(jnt, loc_name)
        constrs.append(pc[0])
        constrs.append(oc[0])
        # constrs.append(sc[0])
        mapping[jnt] = loc_name
    cmds.bakeResults([l for j, l in mapping.iteritems()],
                     time=(start, end + 1), sm=True)
    cmds.delete(constrs)
    cmds.group([l for j, l in mapping.iteritems()], n='tmp_locs')
    # cmds.group([l for l in mapping.values()], name=group_name)
    return mapping


def bake_animation_locators_to_joints(data):
    '''Second part of the operation, that consists of two steps.
    The first one is a function called "bake_animation_joints_to_locators"

    Args:
            data (dict, list): joint:locator data.

    Returns:
            none:
    '''
    # Convert list of objects to mapping.
    # When locators are imported in the other file
    if isinstance(data, list):
        data = {l[:-4]: l for l in data}

    start, end = get_timeline()

    for jnt, loc in data.iteritems():
        cmds.pointConstraint(loc, jnt)
        cmds.orientConstraint(loc, jnt)
        # cmds.scaleConstraint(loc, jnt)
    cmds.bakeResults([j for j, l in data.iteritems()],
                     time=(start, end + 1), sm=True)
    cmds.delete([loc for jnt, loc in data.iteritems()])


def get_sc_multi(a):
    '''Get a multiplier from a skinned object based on the bone per vertex influences.
            A skin serves as a masked regions for further splitting blendshapes.
            Bones names are taken as a prefixes for masked areas.
            Used later when template mesh is being duplicated.

    Args:
            a (str): object name

    Returns:
            dict: with a following structure {bone:{vertex_id:bone_influence}}
    '''
    sc = get_skin_cluster(a)
    if not sc:
        exit_message = 'No skin cluster on the %s' % a
        sys.exit(exit_message)
    bones = cmds.skinCluster(sc, wi=True, q=True)
    vtxs_range = cmds.polyEvaluate(a, v=True)
    sc_multi = {}

    for bone in bones:
        per_bone_multi = {}

        for id in range(0, vtxs_range + 1):
            infl = cmds.skinPercent(sc,
                                    '%s.vtx[%s]' % (a, id),
                                    transform=bone,
                                    ib=0.0001,
                                    query=True)
            if not infl or infl == 0:
                continue
            per_bone_multi[str(id)] = round(infl, 5)
        if not per_bone_multi:
            continue
        sc_multi[bone] = per_bone_multi
    if not sc_multi:
        sys.exit('Bones under the skin cluster do not have influences on any vertex')
    else:
        return sc_multi


def get_diff_coords(a, b):
    diff = {}
    ids = [id for id in a.keys()]

    for id in ids:
        if a[id] == b[id]:
            continue
        diff_coords = calc_coords(a[id], b[id], sub=True)
        diff[id] = diff_coords
    return diff


def set_local_coords(mesh, coords):
    for vtx_id, coords in coords.iteritems():
        cmds.xform(mesh + '.vtx[%s]' % vtx_id, t=coords, r=True)


def split_blendshape(a, b):
    '''Skin of an a object in used to divide the b blendshape on a zones.
            Each joint influence becomes the separate blendshape element.

    Args:
            a (str): object with a skin cluster
            b (str): blendshape name that will be divided

    Returns:
            b_group (str): created group
    '''
    a_coords = get_vtxs_coords(a, relative=True)
    b_coords = get_vtxs_coords(b, relative=True)
    diff_coords = get_diff_coords(a_coords, b_coords)

    sc_multi = get_sc_multi(a)

    b_group = b + '_divided'
    b_group = cmds.group(n=b_group, empty=True)
    
    for bone in sc_multi.keys():
        per_bone_multi = sc_multi[bone]

        diff_coords_multi = {}

        for id, multi in per_bone_multi.iteritems():
            # If position of a identical to b
            if not id in diff_coords.keys():
                continue
            elif multi == 1:
                diff_coords_multi[id] = diff_coords[id]
            else:
                diff_coords_multi[id] = [
                    coord * multi for coord in diff_coords[id]]

        duplicated = cmds.duplicate(a, name=b + '_' + bone)[0]
        set_local_coords(duplicated, diff_coords_multi)
        cmds.parent(duplicated, b_group)

    return b_group


def batch_split_blendshapes():
    '''Splits blendshapes on a zones provided by skin influence.
            Blendshapes selected first, 
            the template with a skin cluster - the last.

    Args:
            None:

    Returns:
            None:
    '''

    objects = cmds.ls(sl=True, fl=True, tr=True)
    a = objects[-1]
    objects.remove(a)

    for o in objects:
        split_blendshape(a, o)
        print o, 'done'


def split_blendshapes_xy_axis(a, b, zx=0, zy=0, cut=0):
    '''Split blendshape on two. Movement is divided by axis.
    The first gets x, z/2 movement from original mesh,
    the second gets y, z/2. 
            Positive or negative translation are cut if cut is set to 1 or -1

    Args:
            a (str): neutral mesh name
            b (str): blendshape name that will be divided
            zx (float, optional): Z axis translation multiplier added to "X" mesh
            zy (float, optional): Z axis translation multiplier added to 'Y' mesh
            cut (int, optional): positive or negative value, 
                    that will be cut from Y axis if met conditions.
                    No cut if 0.

    Returns:
            None:
    '''
    a_coords = get_vtxs_coords(a, relative=True)
    b_coords = get_vtxs_coords(b, relative=True)
    diff_coords = get_diff_coords(a_coords, b_coords)
    x_mesh = cmds.duplicate(a, name=b + '_x')[0]
    y_mesh = cmds.duplicate(a, name=b + '_y')[0]

    for vtx_id, coords in diff_coords.iteritems():
        x_m_coords = [coords[0], 0, coords[-1] * zx]
        # Cuts positive or negative value from transform
        if cut > 0 < coords[1] or cut < 0 > coords[1]:
            y_cut = 0
        else:
            y_cut = coords[1]
        y_m_coords = [0, y_cut, coords[-1] * zy]
        cmds.xform(x_mesh + '.vtx[%s]' % vtx_id, t=x_m_coords, r=True)
        cmds.xform(y_mesh + '.vtx[%s]' % vtx_id, t=y_m_coords, r=True)


def select_bad_joints(mesh, limit=3):
    '''
    Seperates bad ones from auto generated joints that have no useful influence on a skin
    '''
    sc = get_skin_cluster(mesh)
    jnts = cmds.skinCluster(sc, query=True, inf=True)
    bad_attr_jnts = list(jnts)
    start, end = get_timeline()
    attrs = ['translateX', 'translateY',
             'translateZ', 'rotateX', 'rotateY', 'rotateZ']

    for jnt in jnts:

        for attr in attrs:
            if jnt in bad_attr_jnts:

                for frame in range(start, end + 1):
                    if frame == start:
                        init_value = cmds.getAttr(
                            '%s.%s' % (jnt, attr), time=frame)
                    else:
                        value = cmds.getAttr('%s.%s' % (jnt, attr), time=frame)
                        if not (init_value - limit) < value < (init_value + limit):
                            bad_attr_jnts.remove(jnt)
                            break
            else:
                break

    # Another method to detect bad bones.
    # This will find bones with zero weight to vertices.
    bad_sc_jnts = []

    for jnt in jnts:
        infl = cmds.skinPercent(sc,
                                '%s.vtx[*]' % mesh,
                                transform=jnt,
                                query=True)
        if infl < 0.001:
            bad_sc_jnts.append(jnt)

    # Gets joints that influence the lips zones.
    # These joints will be substracted from bad joints.
    # Due to small weights on lips (f.e. Sticky), that are selected as "bad".
    # Vertices ids are saved for male topology.
    vtxs_nums = dict_io(r'u:\face\scripts\config_data\vtx_num_mask.txt', get=True)
    affected_vtxs = ['%s.vtx[%s]' % (mesh, vtx) for vtx in vtxs_nums]
    lips_jnts = cmds.skinPercent(sc,
                                 affected_vtxs,
                                 query=True,
                                 transform=None,
                                 ib=0.1)
    bad_jnts = list(set(bad_attr_jnts + bad_sc_jnts))
    # Removes joints that influence the "lip" zone.
    bad_jnts = [j for j in bad_jnts if j not in lips_jnts]
    if bad_jnts:
        cmds.select(bad_jnts)
    else:
        print 'No bad joints found.'


def get_fxgraph(obj='', print_fxgraph=False):
    if not obj:
        obj = cmds.ls(sl=True)[0]
    bls = get_blendshape_nodes(obj)
    if not bls:
        sys.exit()
    start, end = get_timeline()
    fxgraph = ''

    for frame in xrange(start, (end + 1)):

        for bl in bls:
            bl_names = cmds.listAttr(bl + '.w', multi=True)

            for bl_name in bl_names:

                if cmds.getAttr('%s.%s' % (bl, bl_name), time=frame) == 1:
                    if print_fxgraph:
                        print bl_name, frame
                    fxgraph += '%s_%s\n' % (bl_name, str(frame))

    return fxgraph


def get_blendshape_nodes(mesh):
    bls = []
    bls_set = cmds.ls('blendShape*', type='objectSet')

    for bl_set in bls_set:
        conns = cmds.listConnections(bl_set)
        if mesh in conns:
            bls.append(cmds.ls(conns, type='blendShape')[0])

    if bls:
        return bls
    else:
        print 'No blendshape connected to', mesh


def orient_driv():
    a_jnts = ['driv_Bip01_Neck', 'driv_Bip01_Head']
    b_jnts = ['Bip01_Neck', 'Bip01_Head']
    i_jnt = 'driv_Bip01_Neck1'

    cs = []
    if exists(a_jnts + b_jnts + [i_jnt]):

        for a, b in zip(a_jnts, b_jnts):
            cs.append(cmds.orientConstraint(b, a, mo=True))

        cs.append(cmds.orientConstraint(a_jnts, i_jnt, mo=True, w=0.5))
        return cs
    else:
        print 'Not done. Some of the joints are not in scene.'

# Bones that cannot be deleted or replaced by autobones in
# set_auto_to_biped(mesh) function
low_case_skeleton = ['bn_eye_l', 'bn_eye_r',
                     'bn_tng_01', 'bn_tng_02', 'bn_tng_03', 'bn_jaw_c']
upper_case_skeleton = ['BN_Eyeball_L', 'BN_Eyeball_R',
                       'BN_Tongue_Back', 'BN_Tongue', 'BN_Tongue_Front', 'BN_Jaw_Pivot']


def parent_to_hi(jnts, mapping):

    if len(jnts) == 0:
        return

    for j, parent in mapping.iteritems():
        if j in jnts:
            if cmds.objExists(parent):
                cmds.parent(j, parent)
                jnts.remove(j)
            else:
                continue

    return parent_to_hi(jnts, mapping)


def set_auto_to_biped(mesh, skeleton='new'):
    '''Set autobones generated by DLS plugin into biped hierarchy.
            Autobones are renamed and reparented to biped. 
            The same quantity of biped bones are deleted.
            There is no closest auto to biped bones mapping.

    Args:
            mesh (str): object skinned with autobones

    Returns:
            None:
    '''
    # Gets biped bones hi from head
    if skeleton == 'new':
        biped_bones = cmds.listRelatives('driv_Bip01_Head', type='joint', ad=True)
        excl_bones = low_case_skeleton
    elif skeleton == 'old':
        biped_bones = cmds.listRelatives('Bip01_Head', type='joint', ad=True)
        excl_bones = upper_case_skeleton
    else:
        sys.exit('skeleton parameter should be "new" or "old"')
    [biped_bones.remove(j) for j in excl_bones if j in biped_bones]
    # Gets autobones
    sc = get_skin_cluster(mesh)
    if not sc:
        exit_message = 'No skin cluster found on %s' % mesh
        sys.exit(exit_message)
    auto_bones = cmds.skinCluster(sc, query=True, inf=True)
    # Checks if autobones fits biped bones quantity
    if len(biped_bones) < len(auto_bones):
        exit_message = 'Autobones quantity is greater than biped bones. %s vs %s' % (
            len(auto_bones), len(biped_bones))
        sys.exit(exit_message)
    # Sets auto/biped bones mapping
    auto_biped_match = {}

    for a, b in zip(auto_bones, biped_bones):
        auto_biped_match[a] = b

    bake_to_biped(auto_biped_match)
    return [j for j in auto_biped_match.values()]


def bake_to_locs(objs):
    prefix = '_LOC'
    start, end = get_timeline()
    locs = []
    constrs = []

    for obj in objs:
        cmds.select(clear=True)
        loc_name = cmds.spaceLocator(name=obj + prefix)
        locs.append(loc_name[0])

        pc = cmds.pointConstraint(obj, loc_name)
        constrs.append(pc[0])
        oc = cmds.orientConstraint(obj, loc_name)
        constrs.append(oc[0])

    cmds.bakeResults(locs, time=(start, end + 1), sm=True)
    cmds.delete(constrs)
    return locs


def bake_from_locs(data):
    prefix = '_LOC'
    start, end = get_timeline()
    # If there is mapping for loc:bone
    if isinstance(data, dict):
        jnts = [j for l, j in data.iteritems()]
        constrs = []

        for a, b in data.iteritems():
            loc = a + prefix
            if not cmds.objExists(loc):
                exit = '%s locator not found in scene.' % loc
                sys.exit(exit)
            constrs.append(cmds.pointConstraint(loc, b)[0])
            constrs.append(cmds.orientConstraint(loc, b)[0])

        cmds.bakeResults(jnts, time=(start, end + 1), sm=True)
        cmds.delete(constrs)
    elif isinstance(data, list):
        exit = 'Got list. Now not working with lists.'
        sys.exit(exit)
    else:
        exit = 'Got neither list nor dict.'
        sys.exit(exit)


def bake_to_biped(data):
    start, end = get_timeline()
    # If there is mapping for auto:biped
    if isinstance(data, dict):
        jnts = [biped for auto, biped in data.iteritems()]
        auto = [a for a in data.keys()]
        keyed_frames = cmds.keyframe(auto, query=True, timeChange=True)
        start, end = min(keyed_frames), max(keyed_frames)
        cmds.playbackOptions(min=min(keyed_frames), max=max(keyed_frames))
        constrs = []

        for a, b in data.iteritems():
            constrs.append(cmds.pointConstraint(a, b)[0])
            constrs.append(cmds.orientConstraint(a, b)[0])

        cmds.bakeResults(jnts, time=(start, end + 1), sm=True)
        cmds.delete(constrs)
    elif isinstance(data, list):
        exit = 'Got list. Now not working with lists.'
        sys.exit(exit)
    else:
        exit = 'Got neither list nor dict.'
        sys.exit(exit)


def walked(p, ends=''):
    files = []

    for path, dirs, file_names in os.walk(p):

        for file_name in file_names:
            if file_name.endswith(ends):
                files.append(os.path.join(path, file_name))

    return files


def add_prefix_suffix(name, suf=False, pref=True):

    for o in cmds.ls(sl=True, flatten=True):
        if suf:
            cmds.rename(o, o + '_' + name)
        elif pref:
            cmds.rename(o, name + '_' + o)
        else:
            print 'Set suffix or prefix to rename'



def dir_import():
    folder_path_list = cmds.fileDialog2(fm=3)
    folder_path = folder_path_list[0] + '/'
    files = cmds.getFileList(folder=folder_path)
    if len(files) == 0:
        cmds.warning("No files found")
    else:
        for f in files:
            cmds.file(folder_path + f, i=True)


def key_blendshapes(mesh, start=0):
    bl = get_blendshape_node(mesh)
    if not bl:
        sys.exit('No blendshape node found on oject.')
    targets = cmds.blendShape(bl, t=True, q=True)
    # If blendshape meshes were deleted from scene
    if not targets:
        targets = cmds.listAttr(bl + '.w', multi=True)
    # Generate dict for set each blendshapes in range to 1 infl per call
    weights_bls = {}

    for t in range(len(targets)):
        weight = [(i, 0) for i in range(len(targets))]
        weight[t] = (t, 1)
        weights_bls[start + t + 1] = weight

    # Keys start and end of teeth graph
    end = start + len(targets)
    cmds.setKeyframe(bl, time=start)
    cmds.setKeyframe(bl, time=end + 1)

    for frame, bl_weight in weights_bls.iteritems():
        cmds.blendShape(bl, w=bl_weight, edit=True)
        cmds.setKeyframe(bl, time=frame)

    cmds.playbackOptions(min=start, max=end+1)
    return end

def dls(mesh, target_mesh=None, num_jnts=220, infls=4, iters=4):
    import DLS
    DLS.launch()
    cmds.select(mesh)
    pruneBelow = 0.001
    isKeepOriginal = True
    isDeleteDeltaMush = False
    numBones = num_jnts
    maxInfs = infls
    start, end = get_timeline()
    maxIters = iters
    epilon = 1.0
    targetMesh = target_mesh
    isAlternativeUpdate = False
    DLS.core.learningFunc.solve(numBones, maxInfs, targetMesh, isAlternativeUpdate,
                                start, end, maxIters, isKeepOriginal, pruneBelow,
                                epilon, isDeleteDeltaMush)

def get_m_time(f_path):
    import time
    import os

    e_time = os.path.getmtime(f_path)
    return time.strftime('%Y.%m.%d %H:%M:%S', time.localtime(e_time))


def find_identical_meshes(regex, vtxs_check=True, vtxs=[]):
    '''Searches for all polygon meshes in scene that matches regex expression
        and optional - vertex count. 
        Preset vertex count fits two main types of head meshes, male, female,
        and male neck cut.


    Args:
        regex (str): regular expression
        vtxs_check (boolean, optional): condition, if to check the vertex count on
            top of the regular expression
        vtxs (list, optional): vertices count (int)

    Returns:
        list: polygon meshes that match search parameters
    
    Examples:
        >>> find_identical_meshes('(_head|head_)')
    '''    
    # 2770 - is for cut Krest cut neck head
    if not vtxs:
        vtxs = [2782, 3335, 2770]
    meshes = get_meshes()
    found = []
    [found.append(m) for m in meshes if re.search(regex, m)]

    if not found:
        return

    # Meshes I'm searching for can by messy named,
    # so the only way to find them is to compare by vertices quantity.
    if not vtxs:
        return found

    meshes_filtered = [m for m in found for vtx in vtxs if cmds.polyEvaluate(m, v=True) == vtx]
    if meshes_filtered:
        return meshes_filtered


def find_static_blendshapes(mesh='', rounded=1):

    def get_vtxs_coords_rounded(mesh, relative=False):
        vtxs_coords = {}
        vtxs = cmds.ls(mesh + '.vtx[*]', fl=True)

        for vtx in vtxs:
            if relative:
                coord = cmds.xform(vtx, q=True, t=True, r=True)
            else:
                coord = cmds.xform(vtx, q=True, t=True, ws=True)
            vtx_id = ''.join(i for i in vtx.split('.')[1] if i.isdigit())
            vtxs_coords[vtx_id] = [round(c, rounded) for c in coord]
        return vtxs_coords

    if not mesh:
        mesh = cmds.ls(sl=True)
        if mesh:
            mesh = mesh[0]
        else:
            print '# Select something.'
            return

    init_data = get_vtxs_coords_rounded(mesh, relative=True)
    not_changed_meshes = []

    for m in get_meshes():
        m_data = get_vtxs_coords_rounded(m, relative=True)
        if init_data == m_data:
            not_changed_meshes.append(m)

    if not_changed_meshes:
        cmds.select(not_changed_meshes)
    else:
        print '# No static blendshapes found for %s.' % mesh

def batch_dir_import(ext='mb'):
    folder_path_list = cmds.fileDialog2(fm=3)
    folder_path = folder_path_list[0] + '/'

    files = cmds.getFileList(folder=folder_path, filespec='*.%s' % ext)
    if len(files) == 0:
        cmds.warning("No files found")
    else:
        for f in files:
            cmds.file(folder_path + f, i=True)

def rename_ps(add='', data=[], prefix=True, suffix=False):
    if not data:
        data = cmds.ls(sl=True, fl=True)

    for d in data:
        name = d.split('|')[-1]
        name = name.split(':')[-1]
        if prefix:
            d_renamed = add + '_' + name
        elif suffix:
            d_renamed = name + '_' + add
        else:
            continue
        
        try:
            cmds.rename(d, d_renamed)
        except Exception:
            print '# Cannot rename', d

def get_blendshape_targets(bl):
    return cmds.listAttr(bl + '.w', multi=True)