import maya.cmds as cmds
import sys
import set_fxgraph
import split_blendshapes
import select_bad_joints_distance_based
import functions as f
import skin_import_export as sie
reload(set_fxgraph)
reload(split_blendshapes)
reload(select_bad_joints_distance_based)
reload(f)
reload(sie)

# Gui fields
head_mesh_field = ''
teeth_mesh_field = ''
gender_coll = ''
skeleton_coll = ''


def create_div_mesh(source='', target=''):
    if not cmds.objExists(target):
        cmds.duplicate(source, name=target)
    if not f.get_skin_cluster(target):
        cmds.select(target)
        sie.create_bones = True
        sie.import_weights_sp()


def setup_head(head_mesh, teeth_mesh, gender='male', skeleton='new'):
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
    bls_suffix = '_bls'
    combined_bls_grp = head_mesh + bls_suffix
    complex_template = '%s_head_complex' % gender
    simple_template = '%s_head_simple' % gender
    tmp_bones = 'tmp_bones'
    facefx_combined_meshes = [u'anger', u'disgust', u'fear', u'happiness', u'jaw_open', u'low_lip_down',
                              u'phoneme_CH', u'phoneme_CH_delta', u'phoneme_F', u'phoneme_F_delta', u'phoneme_P',
                              u'phoneme_P_delta', u'phoneme_U', u'phoneme_U_delta', u'phoneme_W', u'phoneme_W_delta',
                              u'phoneme_Y', u'phoneme_Y_delta', u'smile', u'sadness', u'surprise', u'up_lip_up', u'wide_pose']
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
    solved_suffix = '_solved'
    divided_suffix = '*_divided'
    root_meshes = '*_root'
    not_all = False
    divided_bls = 'divided_bls'
    cm_rig = 'cm_rig'
    jnts_grp = '_jnt_grp'

    # Checks all meshes in scene

    for f_mesh in facefx_combined_meshes + [combined_bls_grp] + teeth_bls:
        if not cmds.objExists(f_mesh):
            print f_mesh
            not_all = True

    if not_all:
        sys.exit('Not all objects for facefx division present in scene.')

    # Creates complex and simple meshes from head
    # Adds skin for complex and simple
    create_div_mesh(source=head_mesh, target=complex_template)
    create_div_mesh(source=head_mesh, target=simple_template)

    spl = split_blendshapes.SplitBlendshapes(gender=gender)
    spl.blendshapes_in_scene()
    spl.prepare_blendshapes()
    spl.elements_in_scene(select=False)

    # For now dir stores not used meshes.
    cmds.delete(simple_template)
    cmds.select(facefx_combined_meshes + [complex_template])

    for f_mesh in facefx_combined_meshes:
        f.split_blendshape(complex_template, f_mesh)

    cmds.group(divided_suffix, name=divided_bls)
    cmds.delete(root_meshes)
    cmds.delete(complex_template)
    cmds.delete(combined_bls_grp)
    cmds.delete(tmp_bones)
    # Checks for neutral head duplicates in scene
    cmds.select(head_mesh)
    f.find_static_blendshapes(rounded=0)
    static_meshes = cmds.ls(sl=True)
    static_meshes.remove(head_mesh)
    cmds.delete(static_meshes)
    # Collects all suitable head topology meshes
    blendshape_meshes = f.find_identical_meshes('.*', vtxs_check=True)
    blendshape_meshes.remove(head_mesh)
    cmds.blendShape(sorted(blendshape_meshes), head_mesh)
    # Keys blendshapes
    f.key_blendshapes(head_mesh, start=0)
    # Skin computation
    f.dls(head_mesh, num_jnts=220, infls=4, iters=10)
    # Checks if solved mesh created
    bad_meshes = select_bad_joints_distance_based.get_bad_joints_distance_based(
        head_mesh + solved_suffix, fit_len=11, infl_limit=0.2)
    cmds.delete(bad_meshes)
    # Second pass on deleing useless joints
    # cmds.skinCluster(f.get_skin_cluster(head_mesh), unbind=True, edit=True)
    left_jnts = cmds.skinCluster(f.get_skin_cluster(
        head_mesh + solved_suffix), inf=True, q=True)
    root_jnt = cmds.duplicate(left_jnts[0])[0]
    left_jnts.append(root_jnt)
    sc = cmds.skinCluster(left_jnts, head_mesh, tsb=True)[0]
    cmds.setAttr("%s.envelope" % sc, 0)
    f.dls(head_mesh, num_jnts=220, infls=4, iters=10)
    bad_meshes = select_bad_joints_distance_based.get_bad_joints_distance_based(
        head_mesh, fit_len=11, infl_limit=0.2)
    cmds.delete(bad_meshes)
    set_fxgraph.set_fxgraph(head_mesh=head_mesh,
                            teeth_mesh=teeth_mesh,
                            sex=gender,
                            skeleton=skeleton)
    # Cleanup
    # Add export combined meshes and teeth to "bls" directory
    cmds.delete(head_mesh + solved_suffix)
    cmds.delete(divided_bls)
    cmds.delete(cm_rig)
    cmds.delete(head_mesh + solved_suffix + jnts_grp)
    # Scene cleanup
    try:
        execfile(r'u:\face\scripts\scene_check.py')
    except:
        print 'Scene check failed. Skipped'


def set(*args):
    gaps = False
    head = get_text(head_mesh_field)
    teeth = get_text(teeth_mesh_field)
    gender = get_checked_button(gender_coll)
    skeleton = get_checked_button(skeleton_coll)
    if not head:
        print '# Define head mesh name'
        gaps = True
    if not teeth:
        print '# Define teeth mesh name'
        gaps = True
    if not gender:
        print '# Set gender type'
        gaps = True
    if not skeleton:
        print '# Set skeleton type'

    if not gaps:
        setup_head(head, teeth, gender=gender.lower(),
                   skeleton=skeleton.lower())


def get_checked_button(coll):
    try:
        rb = cmds.radioCollection(coll, query=True, sl=True)
        return cmds.radioButton(rb, query=True, label=True)
    except Exception:
        return None


def get_text(field):
    try:
        return cmds.textField(field, query=True, text=True)
    except Exception:
        return None


def gui():
    global head_mesh_field
    global teeth_mesh_field
    global gender_coll
    global skeleton_coll
    window_name = 'Set_FX_graph'
    if cmds.window(window_name, exists=True):
        cmds.deleteUI(window_name)
    cmds.window(window_name.replace('_', ' '), width=250)
    cmds.columnLayout(adjustableColumn=False)
    head_mesh_field = cmds.textField(h=30, pht='Head', width=250)
    teeth_mesh_field = cmds.textField(h=30, pht='Teeth', width=250)
    cmds.separator(vis=True)
    cmds.text(label='Gender', h=30, align='right')
    gender_coll = cmds.radioCollection()
    cmds.radioButton(label='Male', align='right')
    cmds.radioButton(label='Female')
    cmds.separator(vis=True)
    cmds.text(label='Skeleton', h=30)
    skeleton_coll = cmds.radioCollection()
    cmds.radioButton(label='Old')
    cmds.radioButton(label='New')
    cmds.separator(vis=True)
    cmds.button(label='Set', h=30, width=250, c='set()')
    cmds.showWindow()


gui()
