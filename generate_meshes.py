# Launch with 'execfile(r'u:\face\scripts\generate_meshes.py')''

import maya.cmds as cmds
import random

command = "cmds.xform('%s', t=%s, ro=%s, s=%s, ws=True)"
condition = '''if cmds.objExists("{o}"):
    {c}
else:
    print "{o} not exists"'''
mb_ext = '.mb'
py_ext = '.py'
objects = ['bandit_01_head_tgt',
           'bandit_02_head_tgt',
           'bandit_03_head_tgt',
           'bandit_04_head_tgt',
           'baron_head_tgt',
           'cannibal_02_head_tgt',
           'cannibal_03_head_tgt',
           'cannibal_04_head_tgt',
           'damir_head_tgt',
           'doctor_01_head_tgt',
           'duke_head_tgt',
           'fisherman_mil_02_head_tgt',
           'homeless_v1_head_tgt',
           'idiot_head_tgt',
           'krest_head_tgt',
           'lyosha_head_tgt',
           'miller_head_init_tgt',
           'miller_head_tgt',
           'professor_head_tgt',
           'sam_head_tgt',
           'savage_01_head_tgt',
           'savage_civil_head_tgt',
           'silantius_head_tgt',
           'stepan_head_tgt',
           'tokarev_head_tgt',
           'yermak_head_tgt',
           'miller_brows',
           'miller_brows_inner',
           'miller_lip_lower',
           'miller_lip_upper',
           'miller_mouth',
           'miller_neck',
           'miller_nose']

chr_grp = 'chr_grp'
bls_grp = 'bls_grp'

t_head = 'miller_head'
t_teeth = 'miller_teeth'
t_eyes = ['miller_l_eye', 'miller_r_eye']
t_head_meshes = ['bandit_01_beard',
                 'bandit_02_beard',
                 'bandit_02_eyelashes',
                 'duke_hair',
                 'idiot_hair',
                 'lyosha_beard',
                 'lyosha_eyebrows',
                 'miller_beard',
                 'miller_hair',
                 'miller_wetness',
                 'professor_hair',
                 'stepan_beard',
                 'stepan_brows']

bls = ['anger',
       'anger_x',
       'anger_y',
       'blink_l',
       'blink_r',
       'cheek_blow_l',
       'cheek_blow_r',
       'chew',
       'Chin_Upwards',
       'delta_happiness_smile',
       'delta_jaw_open_chew',
       'disgust',
       'eyes_down_l',
       'eyes_down_r',
       'eyes_left_l',
       'eyes_left_r',
       'eyes_right_l',
       'eyes_right_r',
       'eyes_up_l',
       'eyes_up_r',
       'fear',
       'happiness',
       'Jaw_Backwards',
       'Jaw_Forwards',
       'jaw_left',
       'jaw_open',
       'jaw_right',
       'lips_frown',
       'lips_left',
       'Lips_Open',
       'Lips_Pinch',
       'lips_right',
       'Lips_Sticky_1',
       'Lips_Sticky_2',
       'low_lip_down',
       'phoneme_CH',
       'phoneme_CH_delta',
       'phoneme_F',
       'phoneme_F_delta',
       'phoneme_P',
       'phoneme_P_delta',
       'phoneme_U',
       'phoneme_U_delta',
       'phoneme_W',
       'phoneme_W_delta',
       'phoneme_Y',
       'phoneme_Y_delta',
       'sadness',
       'smile',
       'surprise',
       'up_lip_up',
       'wide_pose',
       'Teeth_Backwards',
       'Teeth_Forwards',
       'Teeth_Left',
       'Teeth_Open',
       'Teeth_Right',
       'Tongue_Up',
       'Tongue_Down',
       'Tongue_In',
       'Tongue_Out',
       'Tongue_Wide',
       'Tongue_Narrow',
       'Tongue_Pressed_Upwards',
       'Tongue_Rolled_Up',
       'Tongue_Rolled_Down']

random_objects = ['bandit_01_head_tgt',
                  'bandit_02_head_tgt',
                  'bandit_03_head_tgt',
                  'bandit_04_head_tgt',
                  'baron_head_tgt',
                  'cannibal_02_head_tgt',
                  'cannibal_03_head_tgt',
                  'cannibal_04_head_tgt',
                  'damir_head_tgt',
                  'doctor_01_head_tgt',
                  'duke_head_tgt',
                  'fisherman_mil_02_head_tgt',
                  'homeless_v1_head_tgt',
                  'idiot_head_tgt',
                  'krest_head_tgt',
                  'lyosha_head_tgt',
                  'miller_head_init_tgt',
                  'miller_head_tgt',
                  'professor_head_tgt',
                  'sam_head_tgt',
                  'savage_01_head_tgt',
                  'savage_civil_head_tgt',
                  'silantius_head_tgt',
                  'stepan_head_tgt',
                  'tokarev_head_tgt',
                  'yermak_head_tgt']


def get_random_tr():
    return [random.randint(-10, 7) * 3, random.randint(-7, 10) * 3, 0]


def set_template():
    global bls_grp
    global chr_grp
    chr_grp = cmds.group(name=chr_grp, empty=True)
    bls_grp = cmds.group(name=bls_grp, empty=True)
    cmds.hide(bls_grp)
    cmds.parent(bls_grp, chr_grp)

    cmds.currentTime(0)
    meshes = cmds.duplicate(t_head, t_teeth, t_eyes, t_head_meshes)
    cmds.parent(meshes, chr_grp)

    for frame, bl in enumerate(bls, start=1):
        cmds.currentTime(frame)
        if frame < 53:
            bl_mesh = cmds.duplicate(t_head, name=bl)[0]
        else:
            bl_mesh = cmds.duplicate(t_teeth, name=bl)[0]
        cmds.parent(bl_mesh, bls_grp)


def get_command(o):
    t = cmds.xform(o, t=True, ws=True, q=True)
    r = cmds.xform(o, ro=True, ws=True, q=True)
    s = cmds.xform(o, s=True, ws=True, q=True)

    return command % (o, str(t), str(r), str(s))


def get_commands():
    commands = ''

    for o in objects:
        commands += condition.format(o=o, c=get_command(o)) + '\n'

    return commands


def save_generated(commands):
    if not cmds.objExists(chr_grp):
        print '# Ctrl group not exists. Exiting.'
        return

    f_path = cmds.fileDialog2(fm=0, fileFilter='*.mb')
    if f_path:
        f_path = f_path[0]
    else:
        print '# Cancelled'
        return

    py_path = f_path.replace(mb_ext, py_ext)

    with open(py_path, 'w+') as py:
        py.write(commands)

    cmds.select(chr_grp)
    cmds.file(f_path, force=True,
              options="v=0;", typ="mayaBinary", pr=True, es=True)
    cmds.delete(chr_grp)
    # Add reset clusters position


def set_random(*args):

    for o in random_objects:
        cmds.xform(o, t=get_random_tr(), a=True)


def process(*args):
    set_template()
    save_generated(get_commands())


# gui
if cmds.window('Generate', exists=True):
    print 'got to existing'
    cmds.deleteUI('Generate')
# Supress warnings
cmds.scriptEditorInfo(sw=True)
cmds.window('Generate', width=250)
cmds.columnLayout(adjustableColumn=True)
cmds.button(label='Set Random',
            command=set_random,
            ann='Mix controls position')
cmds.button(label='Process',
            command=process,
            ann='Export mesh with blendshapes and construction file')
cmds.showWindow()
