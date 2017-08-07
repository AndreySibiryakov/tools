from maya import cmds, OpenMaya
import pickle
import sys
import maya.cmds as cmds
import os
import pickle
from maya.api.OpenMaya import MVector
import maya.mel as mel
import random
import time



class LpcRig(object):

	def __init__(self):
		try:
			self.mesh = cmds.ls(selection=True, flatten=True)[0]
		except:
			print 'A mesh should be selected for the rigging.'
			return
		self.edges = {}
		self.save_dir = 'd:\\.work\\.chrs\\.lps'
		self.data = data
		self.curves = []
		self.hi = '_hi_curve'
		self.low = '_low_curve'
		self.rig_objects = []

	def set_region(self, name, paint=False):
		sel = cmds.ls(sl=True, fl=True)
		if not sel:
			print 'Please, select edges.'
			return
		
		region = {}
		if name == 'excluded':
			vtxs = cmds.ls(cmds.polyListComponentConversion(tv=True), fl=True)
			region[name] = [v.split('.')[-1] for v in vtxs]

		else:
			for e in sel:
				cmds.select(e)
				vtxs = cmds.ls(cmds.polyListComponentConversion(tv=True), fl=True)
				e_id = filter(str.isdigit, str(e.split('.')[-1]))
				region['el_'+str(e_id)] = [v.split('.')[-1] for v in vtxs]
		
		if paint:
			vtxs = cmds.ls(cmds.polyListComponentConversion(sel, tv=True), fl=True)
			cmds.select(vtxs)
			mel.eval("polyColorPerVertex -cdo -rgb 0.0 1.0 1.0;")

		
		self.edges[name] = region

	def set_chains(self, name):
		region = {}
		edges_init = cmds.ls(sl=True, fl=True)
		edges_split = self.split_edges_on_chains(edges_init)
		
		for i, edges in edges_split.iteritems():
			cmds.select(edges)
			vtxs = cmds.ls(cmds.polyListComponentConversion(tv=True), fl=True)
			region[str(i)] = [v.split('.')[-1] for v in vtxs]
		
		self.edges[name] = region

	def is_connected(self, a, b):
		a_vtxs = cmds.ls(cmds.polyListComponentConversion(a, tv=True), fl=True)
		b_vtxs = cmds.ls(cmds.polyListComponentConversion(b, tv=True), fl=True)
		shared_vtxs = [a for a in a_vtxs if a in b_vtxs]
		if shared_vtxs:
			return True
		else:
			return False

	def get_edge_chain(self, chain, data):
		for c in chain:
			connected = [d for d in data if self.is_connected(c, d) and d not in chain]
			if not connected:
				continue
			chain.append(connected[0])
			data.remove(connected[0])
			return self.get_edge_chain(chain, data)
		del data[0]
		return chain
		  
	def split_edges_on_chains(self, data):	
		chains = {}
		iter = 0
		while data:
			chains[iter] = self.get_edge_chain([data[0]], data)
			iter += 1
		return chains

	def save(self, name=''):
		pass

	def load(self, name):
		pass

	def delete_rig(self):
		cmds.delete(self.rig_objects)
		cmds.delete(self.mesh, ch=True)

	def get_dag_path (self, obj):
		'''MARCO GIORDANO'S CODE (http://www.marcogiordanotd.com/)
		
		Called by 'get_u_param' function.
		Call functions: None '''

		if isinstance(obj, list)==True:
			oNodeList=[]
			for o in obj:
				selectionList = OpenMaya.MSelectionList()
				selectionList.add(o)
				oNode = OpenMaya.MDagPath()
				selectionList.getDagPath(0, oNode)
				oNodeList.append(oNode)
			return oNodeList
		else:
			selectionList = OpenMaya.MSelectionList()
			selectionList.add(obj)
			oNode = OpenMaya.MDagPath()
			selectionList.getDagPath(0, oNode)
			return oNode

	def get_u_param(self, pnt = [], crv = None):
		'''MARCO GIORDANO'S CODE (http://www.marcogiordanotd.com/) - Function called by 
		
		Called by 'connectLocToCrv' function.
		Call functions: 'get_dag_path' '''
		
		point = OpenMaya.MPoint(pnt[0],pnt[1],pnt[2])
		curveFn = OpenMaya.MFnNurbsCurve(self.get_dag_path(crv))
		paramUtill=OpenMaya.MScriptUtil()
		paramPtr=paramUtill.asDoublePtr()
		isOnCurve = curveFn.isPointOnCurve(point)
		if isOnCurve == True:
			curveFn.getParamAtPoint(point , paramPtr,0.001,OpenMaya.MSpace.kObject )
		else :
			point = curveFn.closestPoint(point,paramPtr,0.001,OpenMaya.MSpace.kObject)
			curveFn.getParamAtPoint(point , paramPtr,0.001,OpenMaya.MSpace.kObject )
		
		param = paramUtill.getDouble(paramPtr)  
		return param

	def connect_locs_to_curve(self, locs, curve):
		'''Connect locators to lid curves via pointOnCurveInfo nodes.
		
		Called by 'buildRig' function.
		Call functions: None '''
		
		# Upper eyelid
		for loc in locs:
			position = cmds.xform (loc, q = 1, ws = 1, t = 1)
			u = self.get_u_param (position, curve)
			name = loc.replace ("_locator", "_pointOnCurveInfo")
			ptOnCrvInfo = cmds.createNode ("pointOnCurveInfo", n = name)
			cmds.connectAttr (curve + ".worldSpace", ptOnCrvInfo + ".inputCurve")
			cmds.setAttr (ptOnCrvInfo + ".parameter", u)
			cmds.connectAttr (ptOnCrvInfo + ".position", loc + ".t")

	def set_deformation(self):
		cmds.select(self.mesh)
		# Fetching commands from mel LPC script.
		# Since now don't want to rewrite on python
		try:
			mel.eval("setDeformGeom();")
		except:
			print 'LPC not loaded. Please, initialize.'

	def set_lpc_for_region(self, data):
		ctrls = data.keys()
		loc_renaming_table = {}

		for ctrl in ctrls:
			existing_locs = self.get_locators_in_scene()
			vtxs = data[ctrl]
			# time.sleep(1)
			cmds.select([self.mesh+'.'+v for v in vtxs])
			#cmds.refresh()
			#time.sleep(1)
			if ctrl != 'excluded':
				mel.eval("addHandle();")
			else:
				mel.eval("addAnchor();")
			created_locs = self.get_locators_in_scene()
			created_loc = [l for l in created_locs if l not in existing_locs][0]
			loc_renaming_table[created_loc] = ctrl
		'''
		for loc in loc_renaming_table.keys():
			cmds.rename(loc, loc_renaming_table[loc])
		'''
		return loc_renaming_table.keys()

	def get_locators_in_scene(self):
		existing_locs_shapes = cmds.ls('*', type='locator', flatten=True)
		return [cmds.listRelatives(l, p=True)[0] for l in existing_locs_shapes]

	def set_color_lps_rig(self, dict):
		# Won't work with excluded and maybe with chains
		object = cmds.ls(sl=True)[0]
		for loc, vtxs in dict.iteritems():
			cmds.select([object+'.'+v for v in vtxs])
			mel.eval("polyColorPerVertex -cdo -rgb 0.0 1.0 1.0;")

	def create_hi_curve(self, locs, name):
		loc_pos = []
		for loc in locs:
			pos = cmds.xform(loc, ws=True, t=True, q=True)
			loc_pos.append((pos[0], pos[1], pos[2]))
		return cmds.curve(p=loc_pos, ws=True, d=1, name=name+self.hi)

	def create_low_curve(self, name):
		cmds.duplicate(name+self.hi, name=name+self.low)
		return cmds.rebuildCurve(name+self.low, rt=0, s=3)[0]

	def get_pos(self, a):
		pos = cmds.xform(a, translation=True,
							query=True,
							worldSpace=True)    
		return pos

	def get_length(self, a_pos, b_pos):
		return (MVector(b_pos) - MVector(a_pos)).length()

	def get_average_position(self, objects):
	    pos = [cmds.xform(o, ws=True, t=True, q=True) for o in objects]
	    a_x = sum([x[0] for x in pos])/len(pos)
	    a_y = sum([x[1] for x in pos])/len(pos)
	    a_z = sum([x[2] for x in pos])/len(pos)
	    return [a_x, a_y, a_z]

	def get_furthest(self, a, objects):
		return max([self.get_length(self.get_pos(o), a) for o in objects])

	def get_closest(self, a, objects, excluded):
		filtered = [o for o in objects in o not in excluded]
		return min([self.get_length(self.get_pos(f), a) for f in filtered])

	def get_closest_in_order(self, start, objects):
	    ordered = []
	    if start not in ordered:
	        next = self.get_closest(start, objects, ordered)
	        ordered.append(start)
	    for i in range(0, len(objects)-1):
	        next = self.get_closest(next, objects, ordered)
	        ordered.append(next)
	    return ordered

	def order_locs(self, objects):  
	    average = self.get_average_position(objects)     
	    furthest = self.get_furthest(average, objects)
	    ordered = self.get_closest_in_order(furthest, objects)
	    return ordered

	# Didn't work for me. Control vertex is more handful controls than jointss
	# skinned to curve7 I miss rotation, the only one downside of thr control vertex
	def create_controls(self, crv):
	    jnts = []
	    #groups = []
	    #general_g = cmds.group(name=c+'_grp')
	    max = cmds.getAttr('%s.maxValue' % crv )
	    for id in range(0,int(max)):
	        pos = cmds.xform('%s.cv[%s]' % (crv, id), t=True, ws=True, q=True)
	        cmds.select(clear=True)
	        jnt = cmds.joint(p=pos)
	        jnts.append(jnt)
	        cmds.select(clear=True)
	        c = cmds.sphere(ch=0, o=1, po=0, ax=(0, 1, 0), r=0.2, s=4, nsp=2)[0]
	        # c = cmds.circle(ch=0, o=1, nr=(0, 1, 0), r=0.2)[0]
	        g = cmds.group(c)
	        cmds.xform(g, t=pos)
	        nc = cmds.normalConstraint(
	        	self.mesh, g, w=1, aim=(0,1,0), u=(1,0,0), wut='scene')
	        cmds.delete(nc)
	        # cmds.xform(g, os=True, r=True, t=(0,1,0))
	        cmds.parentConstraint(c, jnt, mo=True)
	        cmds.hide(jnts)
	        #cmds.parent(g, general_g)
	    cmds.skinCluster(jnts, crv)

	e = lpc.Edges()
	e.set_mesh()
	e.set_region('excluded')
	e.set_chains('test')

	f.dict_io(save_dir+'f_lips', e.edges, set=True)
	e.edges = f.dict_io(save_dir+'f_chain_lips.txt', get=True)


	def build(self)
		r = lpc.LpcRig(e.mesh)
		cmds.select(e.mesh)
		mel.eval("setDeformGeom();")

		a_objects = cmds.ls( '*', flatten=True, transforms=True)
		cmds.select(clear=True)
		ctrl_grp = cmds.group(name='curve_ctrls', empty=True)
		for region in e.edges.keys():
		    locs = r.set_lpc_for_region(e.edges[region])
		    if region != 'excluded':
		        curve_name = region+r.hi
		        locs = r.order_locs(locs)
		        hi_curve = r.create_hi_curve(locs, region)
		        r.connect_locs_to_curve(locs, hi_curve)
		        low_curve = r.create_low_curve(region)
		        cmds.parent(low_curve, ctrl_grp)
		        cmds.hide(hi_curve)
		        cmds.wire(hi_curve, w=low_curve, gw=0, en=1, ce=0, li=0)
		    # Not so handful, as I expected
		    # r.create_controls(low_curve)
		b_objects = cmds.ls( '*', flatten=True, transforms=True)
		rig_objects = [o for o in b_objects if o not in a_objects]
		r.rig_objects = rig_objects