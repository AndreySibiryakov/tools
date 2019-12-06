"""
import split_blendshapes
reload(split_blendshapes)

spl = split_blendshapes.SplitBlendshapes()
spl.blendshapes_in_scene()
spl.elements_in_scene()
spl.prepare_blendshapes()
"""


import sys
import maya.cmds as cmds
sys.path.append('u:/face/scripts/')
import functions as f
reload(f)


class SplitBlendshapes():

    def __init__(self, map_path='', gender='male'):
        if not map_path:
            self.map_path = 'u:/face/mocap/cm_mapping.txt'
        else:
            self.map_path = map_path

        if gender == 'male':
            # Difference between simple and complex in lip zones.
            # Simple one is divided on left, right.
            # Complex is divided on upper left, upper right, lower left, lower right.
            self.div_mesh_simple = 'male_head_simple'
            self.div_mesh_complex = 'male_head_complex'
        elif gender == 'female':
            self.div_mesh_simple = 'female_head_simple'
            self.div_mesh_complex = 'female_head_complex'
        else:
            sys.exit('Gender must be "male" or "female".')
        self.cm_group = 'cm_rig'
        # Operation names to get elements from combined blendshape
        self.rename = 'rename'
        self.split = 'split'
        self.symm = 'symm'
        self.move = 'move'
        # Conditions for "split" operation
        self.simple = 'simple'
        self.complex = 'complex'
        self.data = []

        if not cmds.objExists(self.div_mesh_simple) or not cmds.objExists(self.div_mesh_complex):
            print '# Need', self.div_mesh_simple, self.div_mesh_complex
            sys.exit('# No or not enough template meshes to split elements from.')
        self.read_cmds()
        # Meshes in scene, also called combined. Happiness.
        self.blendshapes = list(set([cmd[2] for cmd in self.data if cmd[2]]))
        # Meshes obtained from combined ones. Low left lid of happiness.
        self.elements = list(set([cmd[0] for cmd in self.data if cmd[0]]))

    def read_cmds(self):
        with open(self.map_path) as g:
            for l in g:
                self.data.append(l.strip().split("\t"))

    def in_scene(self, data, select=False):
        existing_data = [d for d in data if cmds.objExists(d)]
        missing_data = [d for d in data if d not in existing_data]
        cmds.select(clear=True)
        if select:
            cmds.select(existing_data)

        if missing_data:

            for bl in sorted(missing_data):
                print '#', bl, 'not found'
        else:
            print '# All meshes are in scene.'

    def blendshapes_in_scene(self, select=False):
        self.in_scene(self.blendshapes, select=select)

    def elements_in_scene(self, select=False):
        self.in_scene(self.elements, select=select)

    def mesh_for_proc(self, a):
        if a == self.simple:
            return self.div_mesh_simple
        elif a == self.complex:
            return self.div_mesh_complex

    def prepare_blendshapes(self):
        '''
        Collects all meshes to split and argument, simple or complex
        Split every mesh in collected list
        Moves or/and renames splitted meshes
        Does the same with the others
        Deletes tmp meshes and groups
        '''
        if not cmds.objExists(self.cm_group):
            cmds.group(n=self.cm_group, empty=True)

        # Collects split meshes
        split_meshes = [(bl, opt) for res, suf, bl, proc,
                        opt in self.data if proc == self.split]
        split_meshes = list(set(split_meshes))
        split_grps = []
        for bl, opt in split_meshes:
            if not cmds.objExists(bl):
                continue
            split_grps.append(f.split_blendshape(self.mesh_for_proc(opt), bl))

        # Collects meshes for renaming including split
        split_meshes_for_rename = [[bl + '_' + suf, res] for res, suf, bl, proc,
                                   opt in self.data if proc == self.split]
        meshes_for_rename = [[bl, res] for res, suf, bl, proc,
                             opt in self.data if proc == self.rename]

        for a, b in split_meshes_for_rename + meshes_for_rename:
            if cmds.objExists(b):
                print b, 'exists, cannot rename', a, 'to', b
                continue
            if not cmds.objExists(a):
                continue
            a_dup = cmds.duplicate(a)[0]
            cmds.rename(a_dup, b)
        # Moves meshes to a single group
        meshes_for_move = [res for res, suf, bl, proc,
                           opt in self.data if proc == self.move]
        renamed_meshes = [
            b for a, b in split_meshes_for_rename + meshes_for_rename]

        meshes_to_parent = [m for m in meshes_for_move + renamed_meshes if cmds.objExists(m)]
        cmds.parent(meshes_to_parent, self.cm_group)
        # Deletes tmp meshes and groups
        cmds.delete(split_grps)
