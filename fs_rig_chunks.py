import maya.cmds as cmds

blink_pairs = {'{bl}.EyeSquint_{side}': '{bl}.squint_{side}_blink_delta',
               '{bl}.EyeOpen_{side}': '{bl}.eye_open_{side}_blink_delta',
               '{bl}.EyeUp_{side}': '{bl}.eye_up_{side}_blink_delta',
               '{bl}.MouthSmile_{side}': '{bl}.smile_{side}_blink_delta',
               '{bl}.Sneer_{side}': '{bl}.sneer_{side}_blink_delta',
               '{bl}.CheekSquint_{side}': '{bl}.cheek_squint_{side}_blink_delta'}


def set_blink_for_emotions(bl_node, pairs, blink_ctrl, blink_bl):
    # Sets rules for neutral blink value
    sum_blinks = cmds.shadingNode('plusMinusAverage', asUtility=True)
    sub_from_neutral_blink = cmds.shadingNode(
        'plusMinusAverage', asUtility=True)
    remap_neutral_blink = cmds.shadingNode('remapValue', asUtility=True)
    # Set up node
    cmds.setAttr("%s.operation" % sub_from_neutral_blink, 2)
    # Connections for sum_blinks
    for index, bl in enumerate(pairs.keys()):
        cmds.connectAttr('%s' % bl,
                         '%s.input1D[%s]' % (sum_blinks, index), f=True)

    cmds.connectAttr('%s.output1D' % sum_blinks,
                     '%s.input1D[1]' % sub_from_neutral_blink, f=True)
    # Connections for sub_from_neutral_blink
    cmds.connectAttr(
        blink_ctrl, '%s.input1D[0]' % sub_from_neutral_blink, f=True)
    cmds.connectAttr('%s.output1D' % sub_from_neutral_blink,
                     '%s.inputValue' % remap_neutral_blink, f=True)
    # Connections for remap_neutral_blink
    cmds.connectAttr('%s.outValue' % remap_neutral_blink,
                     '%s' % blink_bl, f=True)

    for driver_bl, driven_bl in pairs.iteritems():
        condition = cmds.shadingNode('condition', asUtility=True)
        cmds.connectAttr(blink_ctrl, '%s.firstTerm' % condition, f=True)
        cmds.connectAttr(driver_bl, '%s.colorIfTrueR' % condition, f=True)
        cmds.connectAttr('%s.outColorR' % condition, driven_bl, f=True)
        cmds.setAttr("%s.colorIfFalseR" % condition, 0)
        # Greater than
        cmds.setAttr("%s.operation" % condition, 2)


sides = ['R', 'L']
bl = 'blendShape1'
ctrl = 'ExpressionBlendshapes.EyeBlink_{}'
blink_bl = '%s.Blink_{}' % bl

for side in sides:
    data = {dr.format(bl=bl, side=side): dn.format(bl=bl, side=side)
            for dr, dn in blink_pairs.iteritems()}
    set_blink_for_emotions(bl, data, ctrl.format(side), blink_bl.format(side))


# Sticky lips
# (position, value)
first_node = [(0, 0), (0.1, 0.3), (0.2, 0)]
second_node = [(0.1, 0), (0.2, 0.3), (0.3, 0)]


def set_remap_function_points(node, data):

    for index, d in enumerate(data):
        position, value = d[0], d[1]
        cmds.setAttr("{}.value[{}].value_Position".format(
            node, index), position)
        cmds.setAttr("{}.value[{}].value_FloatValue".format(
            node, index), value)
        # Linear interpolation
        cmds.setAttr("{}.value[{}].value_Interp".format(
            node, index), 1)


def set_sticky_lips(bl_node, jaw, st_1, st_2):

    for sticky, data in zip([st_1, st_2], [first_node, second_node]):
        sticky_remap = cmds.shadingNode('remapValue', asUtility=True)
        set_remap_function_points(sticky_remap, data)
        cmds.connectAttr('%s.%s' % (bl_node, jaw),
                         '%s.inputValue' % sticky_remap, f=True)
        cmds.connectAttr('%s.outValue' % sticky_remap,
                         '%s.%s' % (bl_node, sticky), f=True)


def set_double_blend(driver, bl, driven_1, driven_2):
    first_node = [(0, 0), (0.5, 1), (1, 0)]
    second_node = [(0.5, 0), (1, 1)]

    for driven, data in zip([driven_1, driven_2], [first_node, second_node]):
        driven_remap = cmds.shadingNode('remapValue', asUtility=True)
        set_remap_function_points(driven_remap, data)
        cmds.connectAttr(driver, '%s.inputValue' % driven_remap, f=True)
        cmds.connectAttr('%s.outValue' % driven_remap,
                         '%s.%s' % (bl, driven), f=True)


first_node = [(0, 0), (0.3, 1), (0.6, 0)]
second_node = [(0.3, 0), (0.6, 1), (1, 0)]
third_node = [(0.6, 0), (1, 1)]


first_node = [(0, 0), (0.5, 1), (1, 0)]
second_node = [(0.5, 0), (1, 1)]
