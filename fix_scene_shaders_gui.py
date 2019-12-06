import re
import os
import maya.cmds as cmds
import maya.mel as mel


def get_meshes():
    '''Gets all the transform meshes node names from a scene

    Returns:
            list: all meshes in scene

    '''
    objects = cmds.ls('*', type='mesh')
    meshes = cmds.listRelatives(objects, parent=True)
    meshes = list(set(meshes))
    return meshes


def find_texture(texture):
    '''Searches for the texture file by its name in a given drive.
        Uses to substitute old broken paths by up to date ones.

    Args:
        texture (str): full path of the texture

    Returns:
        str: Up to date full texture path
    '''
    path = 't:/'
    name = os.path.basename(texture)
    for path, dirs, file_names in os.walk(path):
        for file_name in file_names:
            if file_name == name:
                new_texture = os.path.join(path, file_name)
                return new_texture
    return texture


def fix_texture_files_path():
    '''Substitutes the right image path for all texture file nodes in scene.

    Returns:
        None:
    '''
    texutre_files = cmds.ls(type='file')

    for t_file in texutre_files:
        texture = cmds.getAttr("%s.fileTextureName" % t_file)
        found_texture_path = find_texture(texture)
        if found_texture_path:
            cmds.setAttr("%s.fileTextureName" % t_file, found_texture_path, type="string")


def get_texture_name(texture):
    '''Gets image file name of a texture node.

    Args:
        texture (str): file node

    Returns:
        str: image file name
    '''
    try:
        texture_path = cmds.getAttr("%s.fileTextureName" % texture)
        return os.path.basename(texture_path).split('.')[0]
    except Exception as e:
        print '# %s\nError while executing function get_texture_name().' % e
        return


def get_texture(f):
    '''Gets 2D texture node from a given texture node.

     Returns:
        str: 2D texture node name
    '''
    return cmds.ls(cmds.listHistory(f), type='place2dTexture')


def rename_2d_texture(texture, name):
    '''Renames 2D texture node from a given texture node.

    Args:
        texture (str): texture name
        name (str): new name for 2D texture

     Returns:
        None:
    '''
    texture_2d = cmds.ls(cmds.listHistory(str(texture)), type='place2dTexture')
    if texture_2d:
        cmds.rename(texture_2d[0], name)


def rename_sg_nodes(template, sg='', texture='', count=''):
    '''Renames nodes connected to a shading group or a texture according to template naming.
    Texture nodes types (normal, diffuse, specular) are guessed according to prefixes.
    They are standart: '_nm', '_refl' or '_bump'. Diffuse has no prefix.


    Args:
        template (str): name template to be given to nodes
        sg (str, optional): shading group node name. sg or texture should be filled.
        texture (str, optional): texture node name. sg or texture should be filled.
        count (str, optional): prefix. Should be written with underscore '_2'

    Returns:
        None:
    '''
    if not sg and not texture:
        return

    if not sg and texture:
        shaders = list(set(cmds.ls(cmds.listConnections(texture), materials=True)))
        sgs = list(set(cmds.ls(cmds.listConnections(shaders), type='shadingEngine')))
    else:
        sgs = [sg]
        shaders = list(set(cmds.ls(cmds.listConnections(sg), materials=True)))
    # Protects from bad named normals
    if shaders and sgs:
        nodes = cmds.listHistory(sgs)
        files = list(set(cmds.ls(nodes, type='file')))
        tangent = cmds.ls(nodes, type='bump2d')
    else:
        return
    # Pattern to specify type of materials in image file name.
    refl_pr = ur'_refl\b'
    nm_pr = ur'_nm\b'
    bump_pr = ur'_bump\b'
    # Prefixes, that are defined while renaming sg nodes.
    sg_pr = '_SG'
    sh_pr = '_M'
    diffuse_pr = '_D'
    specular_pr = '_S'
    normal_pr = '_N'
    tangent_pr = '_N_Tangent'
    texture_pr = '_2D'
    # Another protection from bad image files naming.
    # Assuming, that diffuse, specular and normal can be used only once in material.
    diffuse_used = False
    specular_used = False
    normal_used = False

    for f in list(set(files)):
        texture_name = get_texture_name(f)
        if not texture_name:
            continue

        if re.search(refl_pr, texture_name) or re.search(bump_pr, texture_name) and not specular_used:
            cmds.rename(f, template + specular_pr + count)
            rename_2d_texture(template + specular_pr + count, template + specular_pr + texture_pr + count)
            specular_used = True
        elif re.search(nm_pr, texture_name) and not normal_used:
            cmds.rename(f, template + normal_pr + count)
            rename_2d_texture(template + normal_pr + count, template + normal_pr + texture_pr + count)
            normal_used = True
        elif not diffuse_used:
            cmds.rename(f, template + diffuse_pr + count)
            rename_2d_texture(template + diffuse_pr + count, template + diffuse_pr + texture_pr + count)
            diffuse_used = True
        else:
            print '# Skipping file %s with texture name %s' % (f, texture_name)

    if tangent:
        try:
            cmds.rename(tangent, template + tangent_pr + count)
        except:
            print '# Did not rename tangent node %s' % tangent

    for shader in shaders:
        try:
            cmds.rename(shader, template + sh_pr + count)
        except:
            print '# Did not rename shader node %s' % shader

    for sg in sgs:
        try:
            cmds.rename(sg, template + sg_pr + count)
        except:
            print '# Did not rename shading group node %s' % sg


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


def get_mesh_diffuse_name(mesh):
    '''Returns diffuse image name, that is connected to mesh material.
        Diffuse is guessed with a help of prefixes of non-diffuse textures.
        [ur'_refl\b', ur'_nm\b', ur'_bump\b'].

    Args:
        mesh (str):

    Returns:
        list: diffuse image names
    '''
    shape = cmds.listRelatives(mesh, c=True)[0]
    sgs = list(set(cmds.ls(cmds.listConnections(shape), type='shadingEngine')))
    nodes = cmds.listHistory(sgs)
    textures = list(set(cmds.ls(nodes, type='file')))
    diffuse_names = []
    not_diffuse = [ur'_refl\b', ur'_nm\b', ur'_bump\b']

    for texture in textures:
        texture_file = cmds.getAttr("%s.fileTextureName" % texture)
        texture_file_name = os.path.basename(texture_file).split('.')[0]
        if [True for d in not_diffuse if re.search(d, texture_file_name)]:
            continue
        else:
            diffuse_names.append(texture_file_name)

    return list(set(diffuse_names))


def get_most_used_texture_and_heads():
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
    # texture:number of used times
    head_match = {}
    # texture:head using it
    head_t_m_data = {}
    # texture: sll the heads using it
    head_used_data = {}

    for head in find_identical_meshes('(_head|head_)'):
        if not get_mesh_diffuse_name(head):
            continue
        head_t = get_mesh_diffuse_name(head)[0]
        if head_t not in head_t_m_data.keys():
            head_used_data[head_t] = [head]
        else:
            heads = head_used_data[head_t]
            heads.append(head)
            head_used_data[head_t] = heads

        if head_t not in head_match.keys():
            head_match[head_t] = 1
        else:
            head_match[head_t] += 1

        head_t_m_data[head_t] = head

    max_t = max(head_match.values())
    most_texture = [h for h in head_match.keys() if head_match[h] == max_t][0]
    head_of_most_texture = head_t_m_data[most_texture]
    another_heads = head_used_data[most_texture]
    return head_of_most_texture, another_heads


def get_shading_group(mesh):
    '''Gets shading group connected to a given mesh

    Args:
        mesh (str):

    Returns:
        list:
    '''
    shape = cmds.listRelatives(mesh, c=True)[0]
    return list(set(cmds.ls(cmds.listConnections(shape), type='shadingEngine')))


def split_mesh_on_parts(mesh):
    '''Divides polygonal mesh on the shader assigned zones.

    Args:
        mesh (str):

    Returns:
        dict: shading group name as key, list of mesh faces of mesh shape as value
    '''
    sgs = get_shading_group(mesh)
    if not sgs:
        return
    # Not sure about this. better leave for n
    sgs = list(set(sgs))
    mesh_data = {}

    for sg in sgs:
        cmds.hyperShade(objects=sg)
        selection = cmds.ls(sl=True)
        # filter selection to a given mesh only
        selection = [s for s in selection if mesh in s]
        mesh_data[sg] = selection

    return mesh_data


def add_head_sg(sg, template, count=''):
    '''Creates duplicate of a given shading group
        with a template name

    Args:
        sg (str): shading group name
        template (str): new name of a duplicated shading group
        count (str, optional): vertices count (int)

    Returns:
        list: updated shader name
    '''
    # Check base on the only one shader name.
    if not count or count <= 1:
        shader = template + '_M'
    else:
        shader = template + '_M' + count

    if not cmds.objExists(shader):
        tmp_head_name = 'tmp_head_M'
        cmds.duplicate(sg, rr=True, un=True, name=tmp_head_name)
        rename_sg_nodes(template, sg=tmp_head_name, count=count)
    return shader


def fix_sg_names():
    '''Iterates through all texture file nodes in scene.
        Renames all nodes connected to texture: shaders, shading
        groups, 2d textures, files

    '''
    mel.eval('hyperShadePanelMenuCommand("hyperShadePanel1", "deleteUnusedNodes");')
    # Disables because T drive is not set up everywhere
    # fix_texture_files_path()
    not_diffuse_prs = [ur'_refl\b', ur'_bump\b', ur'_nm\b']
    texture_data = {}
    counted_used = {}

    # Gets {texture name:file texture name} to prevent from
    # using the same texture twise, because function rename_sg_nodes()
    # goes up to sg and then lists all textures connected to sg.
    for texture in sorted(cmds.ls(type='file')):
        texture_file = cmds.getAttr("%s.fileTextureName" % texture)
        texture_file_name = os.path.basename(texture_file).split('.')[0]
        texture_file_name = re.sub(r"[^a-zA-Z0-9_.:]", '_', texture_file_name)
        texture_data[texture] = texture_file_name

    for texture, texture_file_name in texture_data.iteritems():
        if not cmds.objExists(texture):
            continue

        if [True for regex in not_diffuse_prs if re.search(regex, texture_file_name)]:
            continue

        # Decided to add counter like this: material, material_2, material_3.
        if texture_file_name in counted_used.keys():
            counter = counted_used[texture_file_name] + 1
            counted_used[texture_file_name] = counter
            counter_pr = '_' + str(counter)
        else:
            counted_used[texture_file_name] = 1
            counter_pr = ''
        rename_sg_nodes(texture_file_name, texture=texture, count=counter_pr)


def fix_face_names():
    '''Renames shading group and connected nodes of head meshes that uses
        the same image texture (diffuse). Template 'face' is used as name mask.
        If there are other head meshes with different textures most common
        texture on head is used. Updated materials applied to head meshes.
        Old named shading group is deleted
    '''
    heads_identical = []
    head, heads_identical = get_most_used_texture_and_heads()
    # head_sg = get_shading_group(head)[0]
    head_template_name = 'face'

    if not heads_identical:
        return

    for head_identical in heads_identical:
        head_parts = split_mesh_on_parts(head_identical)
        counter = 1

        for sg, part in head_parts.iteritems():
            if counter == 1:
                cmds.select(part)
                cmds.hyperShade(assign=add_head_sg(sg, head_template_name, count=''))
            else:
                cmds.select(part)
                cmds.hyperShade(assign=add_head_sg(sg, head_template_name, count='_' + str(counter)))
            counter += 1

    mel.eval('hyperShadePanelMenuCommand("hyperShadePanel1", "deleteUnusedNodes");')


def fix_materials(*args):
    '''General function that organizes scene shading groups
        in two passes. This one is the second one,
        that renames shading groups - fix_sg_names().
    '''
    sg_fixed = False
    try:
        fix_sg_names()
        print '# Fixed shading nodes names.'
        sg_fixed = True
    except Exception as e:
        print '# %s. Error while fixing scene shading group names.' % e

    '''This one is the second one, that renames shading groups
        connected to head meshes - fix_face_names().
    '''
    if sg_fixed:
        try:
            fix_face_names()
            print '# Fixed face material names.'
        except Exception as e:
            print '# %s. Error while fixing face names.' % e
    else:
        print '# Skipping face names fix.'


def enable_checkboxes(*args):
    '''General function that organizes scene shading groups.
        Enables all checkboxes in the menu - Show
    '''
    for model_p in ['modelPanel1', 'modelPanel2', 'modelPanel3', 'modelPanel4']:
        try:
            cmds.modelEditor(model_p,
                             allObjects=True,
                             grid=True,
                             hud=True,
                             sel=True,
                             manipulators=True,
                             edit=True)
        except:
            pass


# gui
cmds.window('Fix Materials', width=250)
cmds.columnLayout(adjustableColumn=True)
cmds.button(label='Fix',
            command=fix_materials,
            ann='Fix all materials in scene including heads')
cmds.button(label='Enable Show Checkboxes',
            command=enable_checkboxes,
            ann='Turns on all checkboxes in show menu')
cmds.showWindow()
