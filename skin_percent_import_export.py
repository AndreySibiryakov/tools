import pickle

def dict_manipulations(dict, path, get=True, set=False):
    if get == True:
        with open(path, 'rb') as bone_map:
            mapping = pickle.loads(dict.read())
    elif set == True:
        with open(path, 'wb') as bone_map:
            pickle.dump(dict, bone_map)
    else:
        sys.exit('Command not specified')
        
mesh = 'anna_head'
skluster = 'anna_head_sc'
path = 'd:/.work/.chrs/anna/.seith_skin_last_dump/anna_head.txt'

weights = {}
vtxs = cmds.polyEvaluate(mesh, v=True)

for id in range(0,vtxs+1):
    vtx = '%s.vtx[%s]' % (mesh, id)
    per_vtx_value = []
    infls = cmds.skinPercent(skluster, vtx, value=True, ib=0.0001, query=True)
    bones = cmds.skinPercent( skluster, vtx, transform=None, ib=0.0001, query=True)
    for infl, bone in zip(infls, bones):
        per_vtx_value.append((bone, infl))
    weights[vtx] = per_vtx_value
    
with open(path, 'wb') as bone_map:
    pickle.dump(weights, bone_map)




    
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



