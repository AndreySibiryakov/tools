import maya.OpenMaya as OpenMaya
from maya.api.OpenMaya import MVector
import maya.cmds as cmds
import sys


class SoftSelectionBlend():

    def __init__(self):
        self.a_mesh = ''
        self.b_mesh = ''
        self.a_vtx_data = {}
        self.b_vtx_data = {}
        self.src_text = 'Set Source'
        self.tgt_text = 'Set Target'
        self.window_name = 'Blend_Soft_Selection'
        self.source_btn = ''
        self.target_btn = ''
        self.blend_sl = ''
        self.source_btn_ann = '        Select source mesh to collect data from'
        self.target_btn_ann = '''        Select target mesh to appy blend to.
        
        MMB updates target position'''
        self.blend_sl_ann = '''        Slide right to blend position
        between source and target meshes.
        
        Slide left to double delta
        between source and target meshes.
        
        MMB sets slider position to zero'''

    def calc_coords(self, a_coords, b_coords, add=False, sub=False):
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

    def get_soft_selected_data(self):
        compOpacities = {}
        if not cmds.softSelect(q=True, sse=True):
            print "Soft Selection is turned off"
            return
        if not cmds.ls(sl=True):
            print 'Nothing Selected for Blend'
            return
        if cmds.objectType(cmds.ls(sl=True)[0]) != 'mesh':
            print 'Vertices Not Selected for Blend'
            return
        richSel = OpenMaya.MRichSelection()
        try:
            # get currently active soft selection
            OpenMaya.MGlobal.getRichSelection(richSel)
        except RuntimeError:
            print "Verts are not selected"
            return
        richSelList = OpenMaya.MSelectionList()
        richSel.getSelection(richSelList)
        selCount = richSelList.length()
        for x in xrange(selCount):
            shapeDag = OpenMaya.MDagPath()
            shapeComp = OpenMaya.MObject()
            try:
                richSelList.getDagPath(x, shapeDag, shapeComp)
            except RuntimeError:
                    # nodes like multiplyDivides will error
                continue

            compFn = OpenMaya.MFnSingleIndexedComponent(shapeComp)
            try:
                # get the secret hidden opacity value for each component (vert, cv, etc)
                for i in xrange(compFn.elementCount()):
                    weight = compFn.weight(i)
                    compOpacities[compFn.element(i)] = weight.influence()
            except Exception, e:
                print e.__str__()
                print 'Soft selection appears invalid, skipping for shape "%s".' % shapeDag.partialPathName()

        return compOpacities

    def get_vtxs_position(self, mesh):
        '''returns dict {vtx_id:[0,0,0]}'''
        data = cmds.xform('%s.vtx[*]' % mesh, q=True, r=True, t=True)
        vtxs = zip(data[0::3], data[1::3], data[2::3])
        return {k: v for k, v in enumerate(vtxs)}

    def get_dag_node(self, mesh):
        selectionList = OpenMaya.MSelectionList()
        try:
            selectionList.add(mesh)
        except:
            return None
        dagPath = OpenMaya.MDagPath()
        selectionList.getDagPath(0, dagPath)
        return dagPath

    def get_vtxs_delta(self, t_coords, a_coords, b_coords):
        # , multi_data
        delta = {}
        vtx_ids = [id for id in a_coords.keys()]

        for vtx_id in sorted(vtx_ids):
            if a_coords[vtx_id] == b_coords[vtx_id]:
                delta[vtx_id] = t_coords[vtx_id]
                continue
            diff_coords = self.calc_coords(
                a_coords[vtx_id], b_coords[vtx_id], sub=True)
            delta[vtx_id] = self.calc_coords(
                t_coords[vtx_id], diff_coords, add=True)

        return delta

    def multiply_coords(self, coords, multi):
        return [c * multi for c in coords]

    def set_vtx_position(self, data, mesh):
        dag_node = self.get_dag_node(mesh)
        MFnMesh = OpenMaya.MFnMesh(dag_node)
        # start_time = timeit.default_timer()
        MFnMesh.setPoints(self.data_to_MPointArray(data))
        # print "Time ", (timeit.default_timer() - start_time)

    def data_to_MPointArray(self, data):
        # Create empty point array to store new points
        newPointArray = OpenMaya.MPointArray()
        vtxs_coords = []

        for vt in sorted(data.keys()):
            vtxs_coords.append(data[vt])

        for d in vtxs_coords:
            newPointArray.append(*d)

        return newPointArray

    def get_vtxs_soft_delta(self, t_coords, a_coords, b_coords, multi_data):
        # multi_data for soft selection
        # blend float for floatslider
        try:
            blend = round(cmds.floatSlider(
                self.blend_sl, value=True, query=True), 2)
        except Exception as e:
            print e
            print 'Gui error occured. Exiting.'
            return
        delta = {}
        vtx_ids = [id for id in a_coords.keys()]

        for vtx_id in sorted(vtx_ids):
            if a_coords[vtx_id] == b_coords[vtx_id]:
                delta[vtx_id] = t_coords[vtx_id]
                continue
            diff_coords = self.calc_coords(
                b_coords[vtx_id], a_coords[vtx_id], sub=True)
            multi = multi_data.get(vtx_id, 0)
            multi_coords = self.multiply_coords(diff_coords, multi)
            blend_coords = self.multiply_coords(multi_coords, blend)
            delta[vtx_id] = self.calc_coords(
                t_coords[vtx_id], blend_coords, add=True)

        return delta

    def process_blend(self, *args):
        if not cmds.objExists(self.a_mesh) or not cmds.objExists(self.b_mesh):
            print 'Select meshes for blend'
            print 'Source mesh is', self.a_mesh
            print 'Target mesh is', self.b_mesh
            return
        soft_selection_data = self.get_soft_selected_data()
        if not soft_selection_data:
            return
        dest_data = self.get_vtxs_soft_delta(
            self.b_vtx_data, self.a_vtx_data, self.b_vtx_data, soft_selection_data)
        self.set_vtx_position(dest_data, self.b_mesh)

    def prepare_a_mesh(self, *args):
        # Assigned to "Set Target" button
        self.update_text(btn=self.source_btn, btn_type='src')
        self.a_vtx_data = self.get_vtxs_position(self.a_mesh)

    def prepare_b_mesh(self, *args):
        # Assigned to "Set Target" button
        self.update_text(btn=self.target_btn, btn_type='tgt')
        self.b_vtx_data = self.get_vtxs_position(self.b_mesh)

    def update_b_mesh(self, *args):
        self.b_vtx_data = self.get_vtxs_position(self.b_mesh)

    def update_text(self, btn='', btn_type=''):
        selection = cmds.ls(sl=True)
        if selection:
            mesh = self.get_transform(selection)
            cmds.button(btn, label='%s' % mesh, edit=True)
            if btn_type == 'src':
                self.a_mesh = mesh
            elif btn_type == 'tgt':
                self.b_mesh = mesh
        elif btn_type == 'src':
            cmds.button(btn, label='%s' % self.src_text, edit=True)
            self.a_mesh = ''
        elif btn_type == 'tgt':
            cmds.button(btn, label='%s' % self.tgt_text, edit=True)
            self.b_mesh = ''
        else:
            return

    def get_slider_val(self, sl):
        return round(cmds.floatSlider(sl, value=True, query=True), 2)

    def get_transform(self, vals):
        if cmds.objectType(vals[0]) == 'transform':
            return vals[0]
        elif cmds.objectType(vals[0]) == 'mesh':
            return cmds.listRelatives(cmds.ls(vals, o=True), p=True)[0]
        else:
            print 'Select polygon object to work with'
            print 'Now is selected', vals[0]
            return

    def reset_slider_value(self, *args):
        # Not working now because of controlConnection
        cmds.floatSlider(self.blend_sl, v=0, edit=True)
        cmds.refresh()


def gui():
    if cmds.window(sb.window_name, exists=True):
        cmds.deleteUI(sb.window_name)
    cmds.window(sb.window_name, titleBarMenu=False)
    cmds.columnLayout(adjustableColumn=True)
    sb.source_btn = cmds.button(
        label=sb.src_text, h=30, width=70, align='left')
    sb.target_btn = cmds.button(
        label=sb.tgt_text, h=30, width=70, align='left')
    cmds.button(sb.source_btn,
                c=sb.prepare_a_mesh,
                ann=sb.source_btn_ann,
                edit=True)
    cmds.button(sb.target_btn,
                c=sb.prepare_b_mesh,
                dragCallback=sb.update_b_mesh,
                ann=sb.target_btn_ann,
                edit=True)
    sb.blend_sl = cmds.floatSlider(min=-1.0,
                                   max=1.0,
                                   step=0.1,
                                   w=250,
                                   v=0,
                                   h=30)
    cmds.floatSlider(
        sb.blend_sl,
        dragCallback=sb.reset_slider_value,
        ann=sb.blend_sl_ann,
        edit=True)
    cmds.button(label='Close',
                h=30,
                width=70,
                align='left',
                command=clear_scene)
    cmds.showWindow()


def clear_scene(*args):
    cmds.deleteUI(sb.window_name, window=True)
    cmds.scriptJob(kill=job_link_slider)
    cmds.delete(ctrl_attr)


def run():
    global job_link_slider
    global ctrl_attr
    # Scriptjob command does not accept class instance.
    # Thats why have taken gui out of class
    gui()
    ctrl_attr = 'tmp_connection_object'
    cmds.sphere(name=ctrl_attr)
    cmds.hide(ctrl_attr)
    job_link_slider = cmds.scriptJob(
        attributeChange=['%s.ty' % ctrl_attr, 'sb.process_blend()'])
    cmds.connectControl(sb.blend_sl, '%s.ty' % ctrl_attr)


# Whould like to get rid of this global vars.
job_link_slider = ''
ctrl_attr = ''
sb = SoftSelectionBlend()
run()
