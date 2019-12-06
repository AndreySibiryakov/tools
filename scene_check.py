import re
import maya.cmds as cmds
import maya.mel as mel
import functions as f
import os


def get_groups():

    empty_shapes = []
    trs = cmds.ls('*', type='transform')
    constrs = cmds.ls(type='constraint')
    jnts = cmds.ls(type='joint')
    trs = [tr for tr in trs if tr not in constrs + jnts]

    for tr in trs:
        shape = cmds.listRelatives(tr, s=True)
        if not shape:
            empty_shapes.append(tr)

    return empty_shapes


def get_bad_naming(data):
    bad = {}

    for item in data:
        found_pr = []

        for pr in bad_prefixes:
            if re.search(regex.format(pr), item.lower()):
                found_pr.append(pr)

        if re.search(num_regex, item.lower()):
            found_pr.append('digit not "_" seperated')

        if found_pr:
            bad[item] = found_pr

    return bad


def check_shapes_naming():
    bad_shapes = {}
    trs = cmds.ls('*', type='transform')

    for tr in trs:
        shape = cmds.listRelatives(tr, s=True)
        if not shape:
            continue

        if 'Shape' not in shape[0]:
            bad_shapes[tr] = shape

    return bad_shapes


def keyed(obj):
    if cmds.keyframe(obj, query=True):
        return True
    else:
        return False


def check_over_scale(data):
    over_scaled = {}

    for item in data:
            # Skips keyed
        if keyed(item):
            continue
        else:
            scale = [int(cmds.getAttr('%s.%s' % (item, at)))
                     for at in scale_attrs]
            if sum(scale) > 3:
                over_scaled[item] = scale

    return over_scaled


def print_stats():
    print '.' * 70
    # Checks naming
    print '\nPlese, rename:'
    bad = get_bad_naming(meshes + grps)
    if bad:
        for item, bad_data in bad.iteritems():
            print '{:.<40} {}'.format(item, ', '.join([b for b in bad_data]))
    # Checks skin on meshes
    # Checks saved skin
    print '\nCheck skin cluster on meshes:'

    for mesh in meshes:
        if f.get_skin_cluster(mesh):
            continue
        elif os.path.exists(skin_data_path + mesh + txt_ext):
            print '{:.<40} {}'.format(mesh, 'no skin cluster, but saved skin')
        else:
            print '{:.<40} {}'.format(mesh, 'no skin cluster')

    # Checks scale in non keyed
    print '\nFix scale on objects greater than 1:'
    over_scaled = check_over_scale(meshes + jnts + grps)
    if over_scaled:
        for item, attrs in over_scaled.iteritems():
            print '{:.<40} {}'.format(item, ', '.join(str(at) for at in attrs))

    print '\n', '.' * 70, '\n'


bad_prefixes = ['new', 'version', 'v', 'old', 'tmp', 'temp', 'delete',
                'temporary', 'outdated', 'del', 'copy', 'duplicated', 'test']

skin_data_path = 'u:/data/skin/'
txt_ext = '.txt'
regex = r'(.|\b|$|_){}($|_|\b|[0-9])'
num_regex = r'[a-z][0-9]($|\b|\s|_)'
scale_attrs = ['scaleX', 'scaleY', 'scaleZ']

mel.eval("cleanUpScene 3")
# Gets objects data in scene
meshes = f.get_meshes()
jnts = cmds.ls('*', type='joint')
grps = get_groups()

# Optimizes scene
# print 'Optimizing scene:'
print_stats()
