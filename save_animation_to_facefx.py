'''
import save_animation_to_facefx
reload(save_animation_to_facefx)

sfx = save_animation_to_facefx.GetAnimation()
sfx.verify_name()
sfx.get_data()
sfx.save_data()
'''

import os
import re
import sys
import cPickle as pickle
# import pickle
import maya.cmds as cmds
sys.path.append('u:/face/scripts/')
import functions as f
reload(f)


class Vividict(dict):

    def __missing__(self, key):
        value = self[key] = type(self)()  # retain local pointer to value
        return value                     # faster to return than dict lookup


class GetAnimation(object):

    def __init__(self, eyes=False):
        '''
        Temporary disabled. For bones only.
        if not objects:
                objects = cmds.ls(sl=True, fl=True)
        if objects:
                self.objects = objects
        else:
                sys.exit('No objects selected to get animation from.')
        '''
        self.anim_group = ''
        self.anim_name = ''
        self.file_name = self.get_scene_name()
        # self.attrs = ['rotateX', 'rotateY', 'rotateZ']
        self.rotates = ["rotateX", "rotateY", "rotateZ"]
        # self.bones_cm_path = 'u:/face/mocap/cm_bone_mapping.txt'
        self.bones_cm_path = 'u:/face/mocap/cm_bone_mapping.txt'
        self.attr_max_degree = 30
        self.data = Vividict()
        self.file_directory = 'u:/face/mocap/facefx/'
        self.ext = '.txt'
        self.sp = 'driv_'
        # Config for sounds database and name verification
        self.search_dir = 'c:/SVN/content/sounds.us/voices/'
        self.true_conditions = ['.flac', 'm3']
        self.false_conditions = ['_narration_', '_audiolog_',
                                 '_radiomessage_', '_tape_',
                                 '_radiostation_', '_radiocomm_']
        self.regex = ur"(.*sounds\.us.)|(\.flac)"
        self.sounds_database = 'sounds_database'
        self.sounds_database_path = self.file_directory + self.sounds_database + self.ext
        self.sounds = {}
        try:
            self.sounds = f.dict_io(self.sounds_database_path, get=True)
        except Exception:
            print  # Cannot import sounds database. Building a new one.
            self.get_sounds()
        # Hardcoded for now. Won't changed till the end of the project
        self.eye_elements = ['Eye_Down_L', 'Eye_Down_R', 'Eye_In_L', 'Eye_In_R', 'Eye_Out_L', 'Eye_Out_R', 'Eye_Up_L', 'Eye_Up_R',
                             'Eyeball_L_Down', 'Eyeball_L_Up', 'Eyeball_L_In', 'Eyeball_L_Out', 'Eyeball_R_Down', 'Eyeball_R_Up', 'Eyeball_R_Out', 'Eyeball_R_In']
        if not eyes:
            self.calc_eyes = False
        else:
            self.calc_eyes = True

    def sound_valid(self, i):

        for c in self.true_conditions:
            if not (c in i):
                return False

        for c in self.false_conditions:
            if c in i:
                return False

        return True

    def get_sounds(self):

        for path, dirs, file_names in os.walk(self.search_dir):

            for file_name in file_names:
                sound = os.path.join(path, file_name)

                if self.sound_valid(sound):
                    name = re.sub(self.regex, '', sound, 0)
                    name = name.replace('/', '\\')
                    self.sounds[name] = name.split('\\')[1]

        f.dict_io(self.sounds_database_path, self.sounds, set=True)

    def get_sound_name(self):

        for name, group in self.sounds.iteritems():
            if self.file_name == name.split('\\')[-1]:
                self.anim_group = group
                self.anim_name = name
                return True

        if not self.anim_group:
            return False

    def verify_name(self):
        if self.get_sound_name():
            return
        else:
            self.get_sounds()
            if not self.get_sound_name():
                exit_message = 'No sound file with a name %s found.' % self.get_scene_name()
                sys.exit(exit_message)

    def get_timeline(self):
        min = cmds.playbackOptions(minTime=True, query=True)
        max = cmds.playbackOptions(maxTime=True, query=True)
        return int(min), int(max) + 1

    def get_frame_and_value(self, obj, attr):
        time_min, time_max = f.get_timeline()
        o_a = '%s.%s' % (obj, attr)
        if not self.keyed(o_a):
            return None
        values = cmds.keyframe(
            o_a, query=True, valueChange=True, time=(time_min, time_max + 1))
        if sum(values) <= 0:
            return None
        frames = cmds.keyframe(o_a, query=True, time=(time_min, time_max + 1))
        value_frame = dict(zip(frames, values))
        return value_frame

    def get_scene_name(self):
        scene_path = cmds.file(sn=True, query=True)
        return os.path.basename(scene_path).split('.')[0]

    def convert_attr_to_map(self, data):
        pos_data = {frame: 0 for frame, value in data.iteritems()}
        neg_data = {frame: 0 for frame, value in data.iteritems()}

        for frame, value in data.iteritems():
            if 0 < value < self.attr_max_degree:
                pos_data[frame] = value / self.attr_max_degree
            elif 0 > value > -self.attr_max_degree:
                neg_data[frame] = value / self.attr_max_degree
            elif value > self.attr_max_degree or value < -self.attr_max_degree:
                exit_message = 'Value out of working range of' + \
                    str(self.attr_max_degree) + \
                    ' degrees at a frame ' + str(frame)
                sys.exit(exit_message)

        return pos_data, neg_data

    def get_blendshape_node(self, mesh):
        bls_set = cmds.ls('blendShape*', type='objectSet')

        for bl_set in bls_set:
            conns = cmds.listConnections(bl_set)
            if mesh in conns:
                bl = cmds.ls(conns, type='blendShape')
                return bl[0]

        exit_message = 'No blendshape connected to ', mesh
        sys.exit(exit_message)

    def sub_driv(self, obj):
        if self.sp in obj:
            return obj.split(self.sp)[-1]
        else:
            return obj

    def read_cmds(self, path):
        data = []

        with open(path) as g:
            for l in g:
                line = l.strip().split("\t")
                if len(line) > 1:
                    data.append(line)

        return data

    def keyed(self, obj):
        if cmds.keyframe(obj, query=True):
            return True
        else:
            return False

    def get_mapped_frame_and_value(self, obj, map_values):
        start, end = self.get_timeline()
        value_frame = {}

        for frame in range(start, end):
            attr_values = [cmds.getAttr('%s.%s' % (
                obj, rot), time=frame) for rot in self.rotates]
            value_frame[frame] = self.mapp(map_values, attr_values)

        return value_frame

    def mapp(self, a, b):

        for m, v in zip(a, b):
            # Zero attributes are not used.
            if m == 0:
                continue
            # Integers should be both positive or both negative
            elif m > 0 > v or m < 0 < v:
                return 0
            # Mapping integer should be greater that animated one.
            # If not - animation curve will be broken. Max mapping value is 1.
            elif m >= v or m <= v:
                return float(v) / m
            else:
                sys.exit('Unknown error occured while mapping values.')

    def get_data(self):
        bls = cmds.ls('blendShape*', type='blendShape')

        for bl in bls:
            attrs = cmds.listAttr(bl + '.w', multi=True)

            for attr in attrs:
                frame_value = self.get_frame_and_value(bl, attr)
                if not frame_value:
                    continue
                self.data[self.anim_group][self.anim_name][attr] = frame_value

        # Gets data from joints.
        map_data = self.read_cmds(self.bones_cm_path)

        # Map data element sample
        # ['head_yaw_right','-45,0,0', 'driv_Bip01_Head']
        for attr, map_values, joint in map_data:
            if not cmds.objExists(joint):
                # print '# %s does not exist. Skipping.' % joint
                continue
            if not self.keyed(joint):
                # print '# %s not keyed. Skipping.' % joint
                continue
            m_attrs = self.get_mapped_frame_and_value(
                joint, list(eval(map_values)))
            self.data[self.anim_group][self.anim_name][attr] = m_attrs

        # Removes eye movement from animation
        if self.calc_eyes:
            return

        for eye_element in self.eye_elements:
            if eye_element in self.data[self.anim_group][self.anim_name].keys():
                del self.data[self.anim_group][self.anim_name][eye_element]

    def save_data(self):
        if self.data:
            anim_path = self.file_directory + self.file_name + self.ext
            # Converts vividict class object to dict
            d_data = eval(repr(self.data))
            with open(anim_path, 'wb') as data_path:
                pickle.dump(d_data, data_path)
            print '# Animation saved to', anim_path
        else:
            sys.exit('Data is empty. Run get_data() method.')
