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
import functions as func

class Lpc(object):


	def __init__(self):
		'''
		if isinstance(data, dict):
			self.data = data
		else:
			sys.exit('Please, provide rig data.')
		'''
		self.mesh = ''
		self.curves = []
		self.hi = '_hi_ctrl'
		self.low = '_ctrl'
		self.rig_objects = []
		self.curve_vtx_match = {}
		self.bls = []
		self.current_bl = ''
		self.lpc_prefix = '_lpc'

		self.data = {}
		self.used_vtxs = []
		self.save_dir = 'd:\\.work\\.chrs\\.lps\\'
		self.current_rig = ''
		self.match_prefix = '_match'
		self.ext = '.txt'


	def get_vtxs(self):
		up = self.data.keys()

		for re in up:
			mid = self.data[re].keys()
	
			for rse in mid:
				
				for vtx in self.data[re][rse]:
					self.used_vtxs.append('%s.%s' % (self.mesh, vtx))


	def paint_used_vtxs(self):
		self.get_vtxs()
		cmds.select(self.used_vtxs)
		mel.eval("polyColorPerVertex -cdo -rgb 0.0 0.0 0.5;")
		cmds.select(clear=True)


	def paint_vtxs(self, objs):
		vtxs = cmds.ls(cmds.polyListComponentConversion(objs, tv=True), fl=True)
		cmds.select(vtxs)
		mel.eval("polyColorPerVertex -cdo -rgb 0.0 0.0 0.5;")
		cmds.select(clear=True)

	def vtxs_used_check(self, vtxs):
		found_used = False
		
		for vtx in vtxs:
			if vtx in self.used_vtxs:
				print vtx, 'is used.'
				found_used = True
		if found_used:
			return
		else:
			[self.used_vtxs.append(vtx) for vtx in vtxs]

	def set_region(self, name, paint=False):
		sel = cmds.ls(sl=True, fl=True)
		if not sel:
			print 'Please, select edges.'
			return
		region = {}
		if name == 'excluded':
			vtxs = cmds.ls(cmds.polyListComponentConversion(tv=True), fl=True)
			self.vtxs_used_check(vtxs)
			region['excluded'] = [v.split('.')[-1] for v in vtxs]
		else:

			for e in sel:
				cmds.select(e)
				vtxs = cmds.ls(cmds.polyListComponentConversion(tv=True), fl=True)
				self.vtxs_used_check(vtxs)
				e_id = filter(str.isdigit, str(e.split('.')[-1]))
				region['el_'+str(e_id)] = [v.split('.')[-1] for v in vtxs]

		if paint: self.paint_vtxs(sel)
		self.data[name] = region


	def set_chains(self, name, paint=False):
		region = {}
		edges_init = cmds.ls(sl=True, fl=True)
		vtxs = cmds.ls(cmds.polyListComponentConversion(tv=True), fl=True)
		self.vtxs_used_check(vtxs)
		# Copies variable, because split_edges_on_chains() removes info from it
		edges_selected = eval(repr(edges_init))
		if not edges_init:
			print 'Please, select edges.'
			return
		edges_split = self.split_edges_on_chains(edges_init)
		
		for i, edges in edges_split.iteritems():
			cmds.select(edges)
			vtxs = cmds.ls(cmds.polyListComponentConversion(tv=True), fl=True)
			region[str(i)] = [v.split('.')[-1] for v in vtxs]
		
		if paint: self.paint_vtxs(edges_selected)
		self.data[name] = region


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


	def save(self, name):
		func.dict_io(self.save_dir+name+self.ext, self.data, set=True)
		self.current_rig = name


	def load(self, name):
		self.data = func.dict_io(self.save_dir+name+self.ext, get=True)
		print 'Rig data loaded.'
		match_path = self.save_dir+name+self.match_prefix+self.ext
		if os.path.exists(match_path):
			self.curve_vtx_match = func.dict_io(match_path, get=True)
			print 'Match for rig data loaded.'
		else:
			print 'Match for rig data not loaded.'
		self.current_rig = name


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


	def get_u_param(self, pnt=[], crv=None):
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


	def set_mesh(self, mesh=''):
		if not mesh:
			self.mesh = cmds.ls(selection=True, flatten=True)[0]

	# Not working as expected due to any X possible selection
	def sort_position(self, values):
		# values = [[x,y,z],[x,y,z],[x,y,z]...]
		x_values = [x for x in values[0]]
		return [s for x, s in sorted(zip(x_values, values))]


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
		object = cmds.ls(sl=True)[0]
		
		for loc, vtxs in dict.iteritems():
			cmds.select([object+'.'+v for v in vtxs])
			mel.eval("polyColorPerVertex -cdo -rgb 0.0 0.0 0.5;")


	def create_hi_curve(self, locs, name):
		loc_pos = []
		
		for loc in locs:
			pos = cmds.xform(loc, ws=True, t=True, q=True)
			loc_pos.append((pos[0], pos[1], pos[2]))
		return cmds.curve(p=loc_pos, ws=True, d=1, name=self.mesh+'_'+name+self.hi)


	def create_low_curve(self, name):
		cmds.duplicate(self.mesh+'_'+name+self.hi, name=self.mesh+'_'+name+self.low)
		return cmds.rebuildCurve(self.mesh+'_'+name+self.low, rt=0, s=4)[0]


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


	def get_furthest(self, locs, average):
		check_value = 0.0
		match_l = ''
		
		for loc in locs:
			l = self.get_length(self.get_pos(loc), average)
			if l > check_value:
				check_value = l
				match_l = loc
		
		if match_l:
			return match_l
		else:
			print loc, locs
			return loc


	def get_closest(self, a, objects, excluded):
		check_value = float('inf')
			
		for o in objects:
			if o not in excluded:
				l = self.get_length(self.get_pos(o), self.get_pos(a))
				if l < check_value:
					check_value = l
					match = o
		return match


	def get_closest_in_order(self, start, objects):
		ordered = []
		if start not in ordered:
			next = self.get_closest(start, objects, ordered)
			ordered.append(start)
		for i in range(0, len(objects)-1):
			next = self.get_closest(next, objects, ordered)
			ordered.append(next)
		return ordered


	def order_locs(self, objects, init=''):  
		average = self.get_average_position(objects)	 
		if not init:
			init = self.get_furthest(objects, average)
		ordered = self.get_closest_in_order(init, objects)
		return ordered


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


	def get_init_loc(self, a, locs):
		check_value = float('inf')
		
		for loc in locs:
			l = self.get_length(self.get_pos(loc), self.get_pos(a))
			if l < check_value:
				check_value = l
				match_l = loc 
		
		return match_l
	

	def get_closest_vtx(self, element, obj):
		vtxs = cmds.polyEvaluate(obj, v=True)
		
		check_value = float('inf')
		current_vtx = ''
		element_pos = self.get_pos(element)
		
		for vtx in range(0, vtxs+1):
			l = self.get_length(element_pos, self.get_pos(obj+'.vtx[%s]' % vtx))
			if l < check_value:
				check_value = l
				match_l = vtx 
		
		return match_l


	def set_curves(self):
		cmds.select(self.mesh)
		# Fetching commands from mel LPC script.
		# Since now don't want to rewrite on python
		try:
			mel.eval("setDeformGeom();")
		except:
			print 'LPC not loaded. Please, initialize it.'
		
		a_objects = cmds.ls( '*', flatten=True, transforms=True)
		cmds.select(clear=True)
		ctrl_grp = cmds.group(name=self.mesh+'_curve_ctrls', empty=True)
		
		for region in self.data.keys():
			locs = self.set_lpc_for_region(self.data[region])
			if region != 'excluded':
				curve_name = region+self.hi
				if self.curve_vtx_match:
					closest_vtx = '%s.vtx[%s]' % (self.mesh, str(self.curve_vtx_match[region]))
					init_loc = self.get_init_loc(closest_vtx, locs)
					locs = self.order_locs(locs, init=init_loc)
				else:
					locs = self.order_locs(locs)
				hi_curve = self.create_hi_curve(locs, region)
				self.connect_locs_to_curve(locs, hi_curve)
				low_curve = self.create_low_curve(region)
				cmds.hide(hi_curve)
				cmds.wire(hi_curve, w=low_curve, gw=0, en=1, ce=0, li=0, dds=[(0, 100)])
				cmds.parent(low_curve, ctrl_grp)
				
			# Not so handful, as I expected
			# self.create_controls(low_curve)
		b_objects = cmds.ls('*', flatten=True, transforms=True)
		rig_objects = [o for o in b_objects if o not in a_objects]
		self.rig_objects = rig_objects

		if not self.curve_vtx_match:

			for c in self.data.keys():
				if c != 'excluded':
					self.curve_vtx_match[c] = self.get_closest_vtx('%s_%s%s.cv[0]' % (self.mesh, c, self.low), self.mesh)

		func.dict_io(self.save_dir+self.current_rig+self.match_prefix+self.ext, self.curve_vtx_match, set=True)


	def set_blendshape(self, a='', b=''):

		meshes = cmds.ls(sl=True)
		if meshes and len(meshes) == 2:
			a = meshes[-1]
			b = meshes[0]
		
		for c in self.data.keys():
			if c != 'excluded':
				a_ctrl = '%s_%s%s' % (a, c, self.low)
				b_ctrl = '%s_%s%s' % (b, c, self.low)
				bl = cmds.blendShape(b_ctrl, a_ctrl)[0]
				cmds.setAttr('%s.%s' % (bl, b_ctrl), 1)
				self.bls.append(bl)

		self.current_bl = b


	def delete_blendshape(self):
		if self.bls:
			cmds.delete(self.bls)


	def duplicate_lpc(self):
		mesh = cmds.ls(sl=True)
		if mesh:
			if self.current_bl:
				d_mesh = cmds.duplicate(mesh, name=self.current_bl+self.lpc_prefix)[0]
			else:
				d_mesh = cmds.duplicate(mesh)[0]
			cmds.delete(cmds.ls('%s|*' % d_mesh, tr=True))
			print 'Got', d_mesh
