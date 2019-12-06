import maya.cmds as cmds
import maya.mel as mel
import pprint


class Rbf(object):

    def __init__(self):
        self.x, self.y, self.z = 'translateX', 'translateY', 'translateZ'
        self.static_attr = 'static_one'
        self.init_suff = '_init'
        # Blenshapes with duplicated source mesh as [0]
        self.bls = []
        self.ctrls = []
        self.main_ctrl = ''
        self.rbf_solver = ''
        self.bl_name = ''

    def set_input_rbf(self, solver, o):

        for coord, index in zip([self.x, self.y, self.z], [0, 1, 2]):
            cmds.connectAttr('%s.%s' % (o, coord), '%s.nInput[%s]' % (
                solver, str(index)), force=True)

    def set_default_rbf_settings(self, solver):
        cmds.setAttr('%s.NDimension' % solver, 1)
        cmds.setAttr('%s.MDimension' % solver, 1)
        cmds.setAttr('%s.distanceMode' % solver, 0)
        cmds.setAttr('%s.rbfMode' % solver, 0)
        cmds.setAttr('%s.blendShapeMode' % solver, 0)
        cmds.setAttr('%s.normalize' % solver, 0)

    def add_static_one(self, o):
        cmds.select(o)
        cmds.addAttr(max=1, min=1, dv=1, ln=self.static_attr, at='long')
        cmds.select(clear=True)

    def set_rbf_target(self, target, solver, index, bl):
        '''Connects new target to rbf node.
            Uses all 3 axis of translation.

            Args:
                target (str): object representing blend to "bl" from initial position
                solver (str): rbf node name
                index (int): target id for rbf node. Ascending.
                bl: (str): blendshape attribute name

            Returns:
                None:
        '''
        index = str(index)
        # Connects target object coordinates to solver
        for coord, axis_id in zip([self.x, self.y, self.z], [0, 1, 2]):
            cmds.connectAttr('%s.%s' % (target, coord), '%s.poses[%s].nKey[%s]' % (
                solver, index, axis_id), force=True)
        # Connects static value to solver for target object
        cmds.connectAttr('%s.%s' % (self.main_ctrl, self.static_attr),
                         '%s.poses[%s].mValue[%s]' % (solver, index, index), force=True)
        # Connects output link from solver to blendshape node
        cmds.connectAttr('%s.mOutput[%s]' % (
            solver, index), '%s.%s' % (self.bl_name, bl), force=True)
        # Updates rbf dimensions
        # Always be + 1. 0 is default pose dimension.
        cmds.setAttr("%s.NDimension" % solver, int(index) + 1)
        cmds.setAttr("%s.MDimension" % solver, int(index) + 1)

    def delete_if_exists(self, o):
        if cmds.objExists(o) and o:
            cmds.delete(o)

    def set_rbf(self):
        # Creates static attribute
        self.add_static_one(self.main_ctrl)
        self.rbf_solver = mel.eval('createNode rbfSolver;')
        self.set_default_rbf_settings(self.rbf_solver)
        self.set_input_rbf(self.rbf_solver, self.main_ctrl)
        indxs = [i for i, bl in enumerate(self.bls)]

        for ctrl, bl, index in zip(self.ctrls, self.bls, indxs):
            self.set_rbf_target(ctrl, self.rbf_solver, index, bl)

    def delete_rbf(self, *args):
        cmds.delete(self.ctrls_grp)
        self.delete_if_exists(self.init_mesh)
        self.delete_if_exists(self.bl_name)
        cmds.deleteUI(self.gui_name, window=True)

    def print_inits(self):
        pprint.pprint(rbf.__dict__)
