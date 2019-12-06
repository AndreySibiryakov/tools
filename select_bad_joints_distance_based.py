import functions as f
import maya.cmds as cmds
# import pprint


def get_zero_weight_jnts(mesh):
    sc = f.get_skin_cluster(mesh)
    jnts = cmds.skinCluster(sc, query=True, inf=True)
    bad_sc_jnts = []

    for jnt in jnts:
        infl = cmds.skinPercent(sc,
                                '%s.vtx[*]' % mesh,
                                transform=jnt,
                                query=True)
        if infl < 0.001:
            bad_sc_jnts.append(jnt)

    return bad_sc_jnts


def average(data):
    return float(sum(data)) / float(len(data))


def get_bad_joints_distance_based(mesh, fit_len=11, infl_limit=0.2):
    # Gets vertices under every joint in skin cluster
    sc = f.get_skin_cluster(mesh)
    jnts = cmds.skinCluster(sc, query=True, inf=True)
    jnts_vtxs_infl = f.get_sc_multi(mesh)
    jnt_vtx_data = {}
    zero_infl_jnts = get_zero_weight_jnts(mesh)
    infl_jnts = [jnt for jnt in jnts if jnt not in zero_infl_jnts]

    for jnt in infl_jnts:
        vtxs_infl = jnts_vtxs_infl[jnt]
        cmds.select(clear=True)
        cmds.skinCluster(sc, e=True, selectInfluenceVerts=jnt)
        jnt_vtxs = cmds.ls(sl=True, fl=True)
        # Filters anything else except vtxs
        jnt_vtxs = [i for i in jnt_vtxs if cmds.objectType(i) == 'mesh']
        # Gets out vertex digit id only
        jnt_vtxs = [''.join(c for c in vtx_id.split('.')[-1]
                            if c.isdigit()) for vtx_id in jnt_vtxs]
        jnt_vtxs = [int(vtx_id) for vtx_id in jnt_vtxs]
        # Removes low infl vertex from the list
        jnt_vtxs = [
            vtx_id for vtx_id in jnt_vtxs if vtxs_infl[str(vtx_id)] > infl_limit]
        if jnt_vtxs:
            jnt_vtx_data[jnt] = jnt_vtxs
        else:
            zero_infl_jnts.append(jnt)

    # pprint.pprint(jnt_vtx_data)
    jnt_vtxs_length = {}

    for jnt, vtxs in jnt_vtx_data.iteritems():
        vtxs_pos = [f.get_pos('%s.vtx[%s]' % (mesh, vtx)) for vtx in vtxs]
        jnt_pos = f.get_pos(jnt)
        jnt_vtx_len = [f.get_length(jnt_pos, vtx_pos) for vtx_pos in vtxs_pos]
        # print jnt, jnt_vtx_len
        av_len = average(jnt_vtx_len)
        jnt_vtxs_length[jnt] = av_len

    # pprint.pprint(jnt_vtxs_length)
    '''
    for jnt, av in jnt_vtxs_length.iteritems():
        if av >= fit_len:
            print jnt, av
    '''
    cmds.select(clear=True)
    return [jnt for jnt, av in jnt_vtxs_length.iteritems() if av >= fit_len] + zero_infl_jnts
    '''
    # Sort out bad joints base on length limit parameter
    bad_jnts = list(infl_jnts)

    for jnt, vtxs in jnt_vtx_data.iteritems():
        jnt_vtx_values = [max_data[vtx] for vtx in vtxs if vtx]
        print jnt, (sum(jnt_vtx_values) / len(jnt_vtx_values))
        # if max(jnt_vtx_values) > limit:
        if (sum(jnt_vtx_values) / len(jnt_vtx_values)) > limit:
            bad_jnts.remove(jnt)

    return bad_jnts + zero_infl_jnts
    '''


# cmds.select(get_bad_joints_distance_based(mesh, fit_len=11, infl_limit=0.2)
