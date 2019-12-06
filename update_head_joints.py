import os
import sys
import re
sys.path.append('u:/face/scripts/')
import functions as f
import maya.cmds as cmds
import skin_import_export as sie
reload(sie)
import batch_skin_eyes

scene_check_joints = ['Bip01', 'driv_Bip01_Head', 'Bip01_Spine2', 'Bip01_Spine3']
root_joint = scene_check_joints[0]
head_joint = scene_check_joints[1]
length_joints = scene_check_joints[2:]
# Head joints naming.
# To not to export weights from.
search_pattern = '''ao
head
eye
teeth
mouth
wetness
brow
hair
lashes
beard'''


def filter_nubs(data):
    return [d for d in data if 'Nub' not in d or 'nub' not in d]


def update(bake=False):

    def namespaced(n):
        return '%s:%s' % (name_space, n)

    cmds.currentUnit(time='pal')
    if not f.exists(scene_check_joints):
        exit_message = 'Not all joints from %s present in scene' % scene_check_joints
        sys.exit(exit_message)
    # Imports file in scene with a given name space
    import_file = cmds.fileDialog2(dialogStyle=2, fm=1)[0]
    name_space = os.path.basename(import_file).split('.')[0] + '_namespace'
    cmds.file(import_file, i=True, namespace=name_space)
    # Delete animation from joints in Biped hierarchy
    cmds.currentTime(0)
    cmds.select(f.get_joints())
    cmds.cutKey()
    # Exports skin cluster weights for body meshes in scene
    all_meshes = f.get_meshes()
    head_meshes = []
    search_pattern_r = '|'.join([sp for sp in search_pattern.split('\n')])
    regex = r"\b.*(%s).*\b" % search_pattern_r

    for m in all_meshes:
        if re.search(regex, m):
            head_meshes.append(m)

    body_meshes = [m for m in all_meshes if m not in head_meshes]
    if body_meshes:
        cmds.select(body_meshes)
        sie.export_weights_sp()

    for sc in cmds.ls(type='skinCluster'):
        cmds.skinCluster(sc, ub=True, edit=True)

    # Deletes bind poses in scene
    cmds.delete(cmds.ls(type='dagPose'))
    # Checks if scene joints are scaled
    length = f.get_length(f.get_pos(length_joints[0]),
                          f.get_pos(length_joints[1]))
    imported_length = f.get_length(f.get_pos(namespaced(length_joints[0])),
                                   f.get_pos(namespaced(length_joints[1])))
    scale_factor = length / imported_length
    if round(scale_factor, 0) != 1:
        scaled_joints_group = cmds.group(namespaced(root_joint))
        cmds.xform(scaled_joints_group,
                   scale=(scale_factor, scale_factor, scale_factor))
    # Aligns imported skeleton to the one in scene
    # All created constraints will be deleted alongside with imported mesh later
    cmds.pointConstraint(head_joint, namespaced(head_joint))
    head_children_joints = cmds.listRelatives(head_joint, ad=True, type='joint')
    head_children_joints = filter_nubs(head_children_joints)

    for j in head_children_joints:
        if f.exists(namespaced(j)):
            f.unlock_attributes(j)
            cmds.pointConstraint(namespaced(j), j)
            cmds.orientConstraint(namespaced(j), j)

    # Keys all biped joints to prevent joints shift
    if bake:
        # Gets information about keyed range of imported bones
        ns_biped = [namespaced(j) for j in f.get_joints() if f.exists(namespaced(j))]
        imported_biped_keys = cmds.keyframe(ns_biped, query=True, timeChange=True)
        ns_min, ns_max = min(imported_biped_keys), max(imported_biped_keys)
        cmds.bakeResults(f.get_joints(),
                         time=(ns_min, ns_max + 1),
                         sm=True)
        cmds.playbackOptions(min=ns_min, max=ns_max + 1)
    else:
        cmds.setKeyframe(f.get_joints(), time=0)
    cmds.namespace(removeNamespace=name_space, deleteNamespaceContent=True)
    # Imports all skin cluster weights for meshes in scene
    cmds.select(f.get_meshes())
    sie.import_weights_sp()
    # Fix eyes joints pivot.
    # When bones are imported from another character
    sy = batch_skin_eyes.SkinEyes()
    sy.set_skin()
