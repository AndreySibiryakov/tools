import maya.cmds as cmds
import sys
sys.path.append('u:/face/scripts/')
import functions as f


def get_head_mesh(data, part='head'):
    head = []

    if not data:
        print 'Nothing selected.'
        return None, None

    if len(data) == 1:
        print 'One object selected', data[0]
        print 'Select two or more.'
        return None, None

    for d in data:
        if part in d:
            head.append(d)

    data.remove(head[0])

    if len(head) == 1:
        return head[0], data
    elif len(head) > 1:
        print len(head), 'meshes with name "head" found.'
        print 'Taking first one as head', head[0]
        return head[0], data
    else:
        print 'No meshes with name "head" found.'
        print 'Taking first one selected'
        return data[0], data


def divide_symmetry():
    head, meshes = get_head_mesh(cmds.ls(sl=True))
    if not head or not meshes:
        return

    for m in meshes:
        f.divide_mesh(head, m, threshold=1.5)


def set_delta_mesh():
    head, meshes = get_head_mesh(cmds.ls(sl=True))
    if not head or not meshes:
        return

    if len(meshes) != 2:
        print 'Select 3 meshes total:'
        print '"head", "modificated", "most modificated".'
        return

    f.set_delta_mesh(head, meshes[0], meshes[1])


def anger_xy_split():
    head, meshes = get_head_mesh(cmds.ls(sl=True))
    if not head or not meshes:
        return

    if len(meshes) != 1:
        print 'More than one mesh selected for split. Using', meshes[0]

    # First, select base mesh, last - modificated one
    f.split_blendshapes_xy_axis(head,
                                meshes[0],
                                zy=1, zx=0,
                                cut=0)


# gui
window_name = 'Mesh_Tools'
if cmds.window(window_name, exists=True):
    print 'got to existing'
    cmds.deleteUI(window_name)
cmds.window(window_name.replace('_', ' '), width=250)
cmds.columnLayout(adjustableColumn=True)
cmds.button(label='Divide Symmetry',
            command='divide_symmetry()',
            ann='Divides mesh on two by X axis with threshold')
cmds.button(label='Set Delta',
            command='set_delta_mesh()',
            ann='Gets difference between 3 meshes')
cmds.button(label='Anger Split',
            command='anger_xy_split()',
            ann='Splits anger on X and Y axis motion')
cmds.showWindow()
