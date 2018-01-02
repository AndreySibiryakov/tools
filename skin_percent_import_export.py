'''
export:
	for every mesh:
		normalize weights
		for every vertex export weights

import:
	for every selected mesh:
		check if skin is saved
		check if bones in saved data exists
			if not, print
		find or create skin cluster of the mesh
		apply skin

'''



import pickle
import os
import sys


sp_path = 'd:\\.work\\.chrs\\.sp'
create_bones = False


def toggle_on_off(*args):
	global create_bones
	if create_bones == True:
		create_bones = False
	else:
		create_bones = True


def get_skin_cluster(mesh):
	skin_cluster = cmds.ls(cmds.listHistory(mesh),type='skinCluster')
	if skin_cluster: 
		skin_cluster = skin_cluster[0]
	else: skin_cluster = None
	return skin_cluster


def exists(objects):
	'''
	Takes strings and lists
	Return True or False
	'''
	
	if isinstance(objects, str):
		if cmds.objExists(objects): 
			return True
	
	elif isinstance(objects, list):
		true_false = []
		for o in objects:
			if cmds.objExists(o): 
				true_false.append(True)
			else: 
				true_false.append(False)
		if False in true_false: 
			return False
		else: 
			return True
	else:
		print 'Types "str", "list" are accepted only'
		return False       


def export_weights_sp(*args):
	
	global sp_path
	
	selected_objects = cmds.ls(selection=True, flatten=True, transforms=True)
	if not selected_objects:
		sys.exit('Please, select objects to save skin from')

	objects_and_skin_cluster = {o:get_skin_cluster(o) for o in selected_objects}

	for o, sc in objects_and_skin_cluster.iteritems():
		if not sc:
			print 'No skin cluster found for %s. Skipping.' % o
			continue
		weights = {}
		vtxs = cmds.polyEvaluate(o, v=True)
		cmds.skinCluster(sc, forceNormalizeWeights=True, edit=True)

		for id in range(0,vtxs+1):
			vtx = '%s.vtx[%s]' % (o, id)
			per_vtx_value = []
			infls = cmds.skinPercent(sc, vtx, value=True, ib=0.0001, query=True)
			bones = cmds.skinPercent(sc, vtx, transform=None, ib=0.0001, query=True)
			per_vtx_value = [(b, i) for b, i in zip(bones, infls)]
			weights[id] = per_vtx_value
		
		save_path = os.path.join(sp_path, o+'.txt')
		with open(save_path, 'wb') as bone_map:
			pickle.dump(weights, bone_map)
		print 'Saved skin for %s' % o


def import_weights_sp(*args):
	
	global sp_path
	# cmds.scriptEditorInfo(sw=True)
	selected_objects = cmds.ls(selection=True, flatten=True, transforms=True)
	if not selected_objects:
		sys.exit('Please, select objects to load skin to.')
	# Check if skin is saved
	o_path = {}
	
	for o in selected_objects:
		save_path = os.path.join(sp_path, o+'.txt')
		if not os.path.exists(save_path):
			print 'No saved skin cluster found for %s' % o
		else:
			o_path[o] = save_path
	# Check if bones in saved exists in scene
	o_data = {}
	o_bones = {}
	bones = []
	
	for o, p in o_path.iteritems():
		with open(p, 'rb') as saved_file:
			data = pickle.loads(saved_file.read())
		o_data[o] = data
		data_values = data.values()
		
		for values in data_values:
			bones += [b[0] for b in values]
		o_bones[o] = bones
	
	bones = list(set(bones))
	stop_bones = []
	
	for bone in bones:
		if not cmds.objExists(bone):
			print '%s not found' % bone
			stop_bones.append(bone)
	
	if stop_bones:
		if create_bones == False:
			sys.exit('Please, rename or add bones to import weights')
		else:
			tmp_grp = cmds.group(empty=True, name='tmp_bones')
			
			for b in stop_bones:
				cmds.select(clear=True)
				cmds.joint(name=b)
				cmds.parent(b, tmp_grp)
			
			print 'Temporary bones created.'
				

	# Check if skin cluster is on onject
	for o, data in o_data.iteritems():
		sc = get_skin_cluster(o)
		if sc:
			# Maybe there is another more handy way to obtain bones under skin cluster
			# If yes - compare bones in it and saved
			# And add if not enough bones
			sc_bones = cmds.skinPercent(sc, '%s.vtx[*]' % o, transform=None, query=True)
			saved_bones = o_bones[o]
			missing_bones = [b for b in saved_bones if b not in sc_bones]
			if missing_bones:
				cmds.skinCluster(o, ai=missing_bones, name=sc, mi=4, wt=0, edit=True)
		else:
			# Now, not defining unique name for every skin cluster
			# If no - assign with bones in saved
			sc = cmds.skinCluster(o, o_bones[o], mi=4, wt=0, tsb=True)[0]

		vtxs = cmds.polyEvaluate(o, v=True)
		progress = vtxs+1
		progress_window = cmds.window(t="importing...")
		cmds.columnLayout()
		progressControl = cmds.progressBar(maxValue=progress, width=300)
		cmds.showWindow(progress_window)
		pr = 0
		
		for id, value in data.iteritems():
			pr += 1
			progressInc = cmds.progressBar(progressControl, edit=True, pr=pr)
			cmds.skinPercent(sc, '%s.vtx[%s]' % (o, id), transformValue=value)
		
		cmds.skinCluster(sc, forceNormalizeWeights=True, edit=True)
		cmds.progressBar(progressControl, edit=True, endProgress=True) 
		cmds.deleteUI(progress_window, window=True)
		print 'Loaded skin for %s' % o
	
	# cmds.scriptEditorInfo(sw=False)    


#gui    
cmds.window('Import Export', width=250)
cmds.columnLayout( adjustableColumn=True )
cmds.button(label='Import', command=import_weights_sp)
cmds.button(label='Export', command=export_weights_sp)
cmds.checkBox( label='Create missing bones', onc=toggle_on_off, ofc=toggle_on_off, value=False)
cmds.showWindow()
























