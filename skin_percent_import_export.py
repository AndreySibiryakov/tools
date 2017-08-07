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
        find or create skincluster of the mesh
        apply skin

'''



import pickle
'''
def num_from_vtx(v):
    try:
        prefix = v.split('.')[-1]
        return int(''.join(chr for chr in prefix if chr.isdigit()))
    except:
        message = "Can't extract number from %s" % v
        sys.exit(message)
'''
def get_skin_cluster(mesh):
    skin_cluster = cmds.ls(cmds.listHistory(mesh),type='skinCluster')
    if skin_cluster: 
        skin_cluster = skin_cluster[0]
    else: skin_cluster = None
    return skin_cluster

path = 'd:/.work/.chrs/anna/.seith_skin_last_dump/anna_head.txt'

def export_weights_sp():
    selected_objects = cmds.ls(selected=True, flatten=True, transforms=True)
    if not selected_objects:
        sys.exit('Please, select objects to save skin from')

    objects_and_skin_cluster = {o:get_skin_cluster(o) for o in selected_objects}

    for o, sc in objects_and_skin_cluster.iteritems():
        if not sc:
            print 'Np skin cluster found for %s. Skipping.' % o
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
        
        save_path = s.path.join(path, o+'.txt')
        with open(save_path, 'wb') as bone_map:
            pickle.dump(weights, bone_map)
        print 'saved skin to %s' % save_path




    
with open(path, 'rb') as bone_map:
    loaded_dict = pickle.loads(bone_map.read())

progress = vtxs+1
progress_window = cmds.window(t="importing...")
cmds.columnLayout()
progressControl = cmds.progressBar(maxValue=progress, width=300)
cmds.showWindow(progress_window)

pr = 0
for vtx, value in loaded_dict.iteritems():
    pr += 1
    progressInc = cmds.progressBar(progressControl, edit=True, pr=pr)
    cmds.skinPercent(skluster, vtx, transformValue=value)
cmds.progressBar(progressControl, edit=True, endProgress=True) 
cmds.deleteUI(progress_window, window=True)    

    
loaded_dict.keys()



