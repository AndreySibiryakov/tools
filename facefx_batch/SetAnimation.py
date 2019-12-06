from FxStudio import *
from FxAnimation import *
import os
import sys
sys.path.extend(['u:/face/scripts/'])
import json
import pickle
import base_config
cfg = base_config.Config()
import AnalysisTextPreprocessor
reload(AnalysisTextPreprocessor)


class SetAnimation(object):

    def __init__(self):
        self.animsets_data = {}
        self.cur_lang = ''
        self.cur_a_lang = ''
        self.current_curve = ''
        self.mocap_db = None
        self.facefx_db = None
        self.current_batch_data = []
        self.missing_batch_data = []
        self.current_anim_data = {}
        self.template_anim_data = {cfg.animset: None, cfg.anim: None,
                                   cfg.file_path: None, cfg.anim_type: None, cfg.anim_short: None}

    def det_pickle_data(self, path):
        '''Loads mocap animation data from "pickle"

        Args:
            path (str):

        Returns:
            dict:
        '''
        with open(path, 'rb') as dict_path:
            dict = pickle.loads(dict_path.read())
            # print '# Loaded dictionary from', path
        return dict

    def get_data(self, path):
        '''Loads animation data from "json"

        Args:
            path (str):

        Returns:
            list: list of dicts
        '''
        with open(path) as dict_path:
            data = json.load(dict_path)
            return data

    def set_data(self, path, data):
        '''Dumps animation data to "json".
        Truncates file content.

        Args:
            path (str):
            data (list): list of dicts

        Returns:
            None
        '''
        with open(path, "w") as write_file:
            json.dump(data, write_file)

    def set_console_vars(self):
        '''Sets global facefx vars.
        Sets up conditions for publishing packages to engine.

        Args:
            None

        Returns:
            None
        '''
        issueCommand('set -n "po_bake_events_to_curves" -v "0";')
        issueCommand('set -n "po_collapse_face_graph" -v "0";')
        issueCommand('set -n "po_remove_anim_editor_only_data " -v "1";')
        issueCommand('set -n "po_remove_phon_word_lists " -v "1";')
        issueCommand('set -n "po_remove_mapping" -v "1";')
        issueCommand('set -n "po_destination_dir" -v "%s";' %
                     cfg.animsets_dir.format(lang=self.cur_lang))
        # For silent, no popups mode
        issueCommand('set -n "g_unattended" -v "1";')

    def set_analyze_lang(self):
        '''Sets language for facefx analyze command,
        that used in "analyze_sound(self, path, group, name)".
        Identifies lang by dict mapping in "cfg.a_langs".
        Substitues any unrecognized langs by US English.
        Assignes value to a string variable "self.cur_a_lang".

        Args:
            None

        Returns:
            None
        '''
        self.cur_a_lang = cfg.a_langs.get(self.cur_lang, 'USEnglish')

    def load_actor(self):
        '''Facefx python wrapped command.
        Operates "cfg.actor" variable.

        Args:
            None

        Returns:
            None
        '''
        issueCommand('loadActor -file "%s"' % cfg.actor)

    def close_actor(self):
        '''Facefx python wrapped command.

        Args:
            None

        Returns:
            None
        '''
        issueCommand('closeActor')

    def save_actor(self):
        '''Facefx python wrapped command.
        Operates "cfg.actor" variable.

        Args:
            None

        Returns:
            None
        '''
        issueCommand('saveActor -file "%s"' % cfg.actor)

    def analyze_sound(self, path, group, name):
        '''Facefx python wrapped command.
        Main command that processes sound to animation.
        Analysis actor in taken from "cfg.aa".
        Language is taken from "self.cur_a_lang".

        Args:
            path (str): sound path
            group (str): animset name
            name (str): animation name

        Returns:
            None
        '''
        issueCommand('analyze -audio "%s" -g "%s" -anim "%s" -overwrite -aa "%s" -language "%s"' %
                     (path, group, name, cfg.aa, self.cur_a_lang))

    def get_animsets_data(self):
        '''Collects animset files from the root of "cfg.animsets_dir"
        of the current processing lang. Assignes data to "self.animsets_data"
        as {animset_name: animset path}.

        Args:
            None

        Returns:
            None
        '''
        a_dir_path = cfg.animsets_dir.format(lang=self.cur_lang)

        for name in os.listdir(a_dir_path):
            a_file_path = os.path.join(a_dir_path, name)
            if os.path.isfile(a_file_path) and a_file_path.endswith(cfg.a_ext):
                self.animsets_data[name.split(cfg.a_ext)[0]] = a_file_path

        if not self.animsets_data:
            self.animsets_data = {None: None}

    def export_animset(self, animset, dir):
        '''Facefx python wrapped command.

        Args:
            None

        Returns:
            None
        '''
        if not os.path.exists(dir):
            os.makedirs(dir)
        path = os.path.join(dir, animset + cfg.a_ext)
        issueCommand('animSet -export "%s" -to "%s"' % (animset, path))

    def mount_animset(self, path):
        '''Facefx python wrapped command.

        Args:
            path (str): animset path

        Returns:
            None
        '''
        issueCommand('animSet -mount "%s"' % path)

    def unmount_animset(self, animset):
        '''Facefx python wrapped command.

        Args:
            animset (str): animset name

        Returns:
            None
        '''
        issueCommand('animSet -unmount "%s"' % animset)

    def publish_actor_go(self):
        '''Facefx python wrapped command.
        Simple command for publishing content to engine.
        All settings is taken from "self.set_console_vars()" method

        Args:
            None

        Returns:
            None
        '''
        issueCommand('publish -go;')

    def frames_to_time(self, frame, fps=30):
        '''Converts frame number to time in milliseconds.

        Args:
            frame (int)
            fps (int, float)

        Returns:
            float
        '''
        return 1.0 / float(fps) * float(frame)

    def add_animset(self, animset):
        '''Facefx python wrapped command.

        Args:
            animset (str) animset name

        Returns:
            None
        '''
        issueCommand('animGroup -create -group "%s";' % animset)

    def add_animation(self, animset, anim):
        '''Facefx python wrapped command.

        Args:
            animset (str): animset name
            anim (str): animation name

        Returns:
            None
        '''
        issueCommand('anim -add -group "%s" -name "%s";' % (animset, anim))

    def add_curve(self, animset, anim, curve):
        '''Facefx python wrapped command.

        Args:
            animset (str): animset name
            anim (str): animation name
            curve (str): curve name

        Returns:
            None
        '''
        issueCommand('curve -group "%s" -anim "%s" -add -name "%s";' %
                     (animset, anim, curve))

    def select_curve(self, curve):
        '''Facefx python wrapped command.

        Args:
            curve (str): curve name

        Returns:
            None
        '''
        issueCommand('select -type "curve" -names "%s";' % curve)

    def select_animation(self, animation):
        '''Facefx python wrapped command.

        Args:
            animation (str): animation name

        Returns:
            None
        '''
        issueCommand('select -type "anim" -names "%s";' % animation)

    def insert_key(self, time, value, slope_in, slope_out):
        '''Facefx python wrapped command.

        Args:
            time (float): key time in milliseconds
            value (float): key value
            slope_in (float): in tangent value
            slope_out (float): out tangent value

        Returns:
            None
        '''
        issueCommand('key -insert -cn "%s" -time %f -value %f -si %f -so %f;' %
                     (self.current_curve, time, value, slope_in, slope_out))

    def remove_animation(self, animset, animation):
        '''Facefx python wrapped command.

        Args:
            animset (str): animset name
            anim (str): animation name

        Returns:
            None
        '''
        issueCommand('anim -remove -group "%s" -name "%s";' %
                     (animset, animation))

    def remove_curve(self, animset, anim, curve):
        '''Facefx python wrapped command.

        Args:
            animset (str): animset name
            anim (str): animation name
            curve (str): curve name

        Returns:
            None
        '''
        issueCommand('curve -group "%s" -anim "%s" -remove -name "%s";' %
                     (animset, anim, curve))

    def set_framerate(self, animset, anim):
        '''Facefx python wrapped command.

        Args:
            animset (str): animset name
            anim (str): animation name

        Returns:
            None
        '''
        issueCommand(
            'anim -group "%s" -name "%s" -setframerate 30.000000' % (animset, anim))

    def animset_exists(self, animset):
        '''Facefx python wrapped command.

        Args:
            animset (str): animset name

        Returns:
            None
        '''
        result = getAnimationNames()

        for i in range(0, len(result)):
            if animset == result[i][0]:
                return i

        return None

    def get_anim_names(self, animset):
        '''Facefx python wrapped command.

        Args:
            animset (str): animset name

        Returns:
            list: animation names present in animset
        '''
        group_anim_data = getAnimationNames()

        for element in group_anim_data:
            if element[0] == animset:
                return list(element[-1])

        return None

    def rename_animation(self, animset, a_name, b_name):
        '''Facefx python wrapped command.

        Args:
            animset (str): animset name
            a_name (str): current anim name
            b_name (str): new anim name

        Returns:
            None
        '''
        issueCommand('anim -rename -group "%s" -name "%s" -newname "%s";' %
                     (animset, a_name, b_name))

    def move_animation(self, a_set, b_set, anim):
        '''Facefx python wrapped command.

        Args:
            a_set (str): source animset name
            b_set (str): target animset name
            anim (str): animation name

        Returns:
            None
        '''
        issueCommand('anim -move -from "%s" -to "%s" -name "%s";' %
                     (a_set, b_set, anim))

    def set_curve_to_manual(self, animset, anim, curve):
        '''Facefx python wrapped command.
        Sets curve to manual mode.
        Curve can be edited in manual mode only.

        Args:
            animset (str): animset name
            anim (str): animation name
            curve (str): curve name

        Returns:
            None
        '''
        issueCommand('curve -edit -group "%s" -anim "%s" -name "%s" -owner "user";' %
                     (animset, anim, curve))

    def animation_exists(self, animset, anim):
        '''Facefx python wrapped command.

        Args:
            animset (str): animset name
            anim (str): animation name

        Returns:
            anim (str):
        '''
        # Returns a nested tuple
        # ('Default', ('spr_004_level3_05', 'spr_004_level3_09', 'spr_004_level3_12'))
        result = getAnimationNames()
        if anim in result[animset][1]:
            return anim
        else:
            return None

    def add_payload(self, animset, anim, min_s, pl_text):
        '''Facefx python wrapped command.

        Args:
            animset (str): animset name
            anim (str): animation name
            min_s (float): start time of the payload
            pl_text (str): payload text

        Returns:
            None
        '''
        issueCommand('event -group "%s" -anim "%s" -add -eventgroup "%s" -eventanim "%s" -minstart %f -maxstart %f; -payload "%s";' %
                     (animset, anim, cfg.payload_animset, cfg.payload_anim, min_s, min_s, pl_text))

    def smooth_animation(self, animset, anim, curves):
        '''Facefx python wrapped command.

        Args:
            animset (str): animset name
            anim (str): animation name
            curves (list): curve names

        Returns:
            None
        '''
        curves = '|'.join(curves)
        issueCommand('smooth -group "%s" -anim "%s" -curves "%s" -p0val 0.000000 -p0slope 0.000000 -p1val 1.000000 -p1slope 0.000000 -p2val 0.000000 -p2slope 0.000000 -length 0.250000' %
                     (animset, anim, curves))

    def add_event(self, animset, anim, event, min_time):
        '''Facefx python wrapped command.

        Args:
            animset (str): animset name
            anim (str): animation name
            event (str): event name
            min_time (float): event start time

        Returns:
            None
        '''
        issueCommand(
            'event -group "%s" -anim "%s" -add -eventgroup "anim" -eventanim "%s" -minmagnitude 0.000000 -maxmagnitude 0.000000 -minstart %s -maxstart %s;' % (animset, anim, event, min_time, min_time))

    def add_custom_persist_event(self, animset, anim, event):
        '''Facefx python wrapped command.

        Args:
            animset (str): animset name
            anim (str): animation name
            event (str): event name

        Returns:
            None
        '''
        issueCommand('event -group "%s" -anim "%s" -add -eventgroup "anim" -eventanim "%s" -minstart 0.000000 -maxstart 0.000000 -persist "true";' % (animset, anim, event))

    def set_event_persist(self, animset, anim):
        '''Facefx python wrapped command.
        Works only with  "self.move_face_idles_to_events()" method
        Event id is hardcoded.
        So, will work with every single event once created only.

        Args:
            animset (str): animset name
            anim (str): animation name

        Returns:
            None
        '''
        issueCommand(
            'event -group "%s" -anim "%s" -edit -id 0 -persist "true";' % (animset, anim))

    def check_sound(self, i):
        '''Verifies True and False conditions for sound path to match.
        Conditions are set in "cfg.true_conditions" and "cfg.false_conditions".

        Args:
            i (str): sound path

        Returns:
            boolean:
        '''
        for c in cfg.true_conditions:
            if not (c in i):
                return False

        for c in cfg.false_conditions:
            if c in i:
                return False

        return True

    def get_sounds(self, dir):
        '''Collects sound paths with "os.walk" from a given directory.
        "self.check_sound" is applied to results.

        Args:
            dir (str): directory to search in

        Returns:
            list:
        '''
        dir_sounds = []

        for path, dirs, file_names in os.walk(dir):

            for file_name in file_names:
                sound = os.path.normpath(os.path.join(path, file_name))
                if self.check_sound(sound):
                    dir_sounds.append(sound)

        return dir_sounds

    def split_sound(self, sound_path):
        '''Splits sound_path to chunks:
        sound path, animset, anim

        Args:
            sound_path (str):

        Returns:
            tuple: sound path, animset name, anim name

        Examples:
            >>> split_sound(r'c:\SVN\content\sounds.us\voices\m3_12_valley\val_003_80_alchemist_01_09_01.flac')
            (r'c:\SVN\content\sounds.us\voices\m3_12_valley\val_003_80_alchemist_01_09_01.flac',
            'm3_12_valley',
            'voices\\m3_12_valley\\val_003_80_alchemist_01_09_01')
        '''
        split_path = sound_path.split(os.sep)
        animset = split_path[5]
        a = split_path[-1].split('.')[0]
        anim = '\\'.join(split_path[4:-1] + [a])
        return sound_path, animset, anim

    def get_root_subdirs(self):
        '''Gets sound VO dirs.
        Every dir represents separate level of the game.
        Directory name is taken from "cfg.sounds_dir.format(lang=self.cur_lang)".
        Directory is taken if "cfg.key" in name.
        For Metro Exodus it is "m3" suffix.

        Args:
            None

        Returns:
            list: sounds VO dirs path
        '''
        return [os.path.join(cfg.sounds_dir.format(lang=self.cur_lang), name)
                for name in os.listdir(cfg.sounds_dir.format(lang=self.cur_lang)) if cfg.key in name]

    def get_mocap_data(self):
        '''Collects mocap animation information into list of dicts:
        {animset: None,
        anim: None,
        file_path: None,
        anim_type: 'mocap',
        sound_path: None}
        Mocap data stored in .json format and collected from "cfg.mocap_to_facefx_dir".
        File path is .txt path.
        Sound path is .flac path if found with "self.get_sound_path_for_mocap_anim(anim_name)"

        Args:
            None

        Returns:
            list: list of dicts
        '''
        mocap_files = []
        mocap_data = []
        # {animset: None, anim: None, file_path: None, anim_type: None, sound_path: None}

        for name in os.listdir(cfg.mocap_to_facefx_dir):
            if name.endswith('.txt') and 'sounds_database' not in name:
                mocap_files.append(os.path.join(
                    cfg.mocap_to_facefx_dir, name))

        if not mocap_files:
            print '# No mocap animations were found in the specified folder.\n#', cfg.mocap_to_facefx_dir
            return

        for file_path_v in mocap_files:
            m_data = dict(self.template_anim_data)
            anim_data = self.det_pickle_data(file_path_v)
            animset_v = anim_data.keys()[0]
            anim_v = anim_data[animset_v].keys()[0]

            m_data[cfg.animset] = animset_v
            if anim_v:
                m_data[cfg.anim] = anim_v
            else:
                # If animation has no sound match
                m_data[cfg.anim] = os.path.basename(
                    file_path_v).split('.')[0].lower()
                m_data[cfg.anim_short] = m_data[cfg.anim]
            m_data[cfg.file_path] = file_path_v
            m_data[cfg.anim_type] = cfg.mocap_type
            m_data[cfg.sound_path] = self.get_sound_path_for_mocap_anim(
                m_data[cfg.anim])
            if m_data[cfg.sound_path]:
                m_data[cfg.anim_short] = os.path.basename(
                    m_data[cfg.sound_path]).split('.')[0].lower()
            mocap_data.append(m_data)

        return mocap_data

    def get_sound_path_for_mocap_anim(self, anim):
        '''Searches for sound file in "self.facefx_db" that matches mocap animation.
        Loads facefx database if not loaded, but doesn't update facefx database.

        Args:
            anim (str): animation name

        Returns:
            str: sound file path or empty string
        '''
        if not self.facefx_db:
            self.load_db()
        elif not self.facefx_db:
            sys.exit(
                'Collect facefx database first to search for mocap - sound match')
        found = self.get_data_from_db(self.facefx_db, cfg.anim, anim)
        if found:
            return found[0][cfg.file_path]
        else:
            return ''

    def get_data_from_db(self, db, key, value):
        '''Searches for sound file in "self.facefx_db" that matches mocap animation.

        Args:
            db (list): list of dicts
            key (str): one of data keys from base_config
            value (str):

        Returns:
            str: sound file path or empty string
        '''
        return [data for data in db if data.get(key) == value]

    def get_facefx_data(self):
        '''Collects facefx animation information into list of dicts:
        {animset: None,
        anim: None,
        file_path: None,
        anim_type: 'facefx'}
        File path is .flac path.

        Args:
            None

        Returns:
            list: list of dicts
        '''
        facefx_data = []
        sounds_path = []
        s_dirs = self.get_root_subdirs()

        for s_dir in s_dirs:
            sounds_path += self.get_sounds(s_dir)
        for sound_path in sounds_path:
            file_path_v, animset_v, anim_v = self.split_sound(sound_path)
            s_data = dict(self.template_anim_data)
            s_data[cfg.animset] = animset_v
            s_data[cfg.anim] = anim_v
            s_data[cfg.anim_short] = os.path.basename(
                file_path_v).split('.')[0].lower()
            s_data[cfg.file_path] = file_path_v
            s_data[cfg.anim_type] = cfg.facefx_type
            facefx_data.append(s_data)

        return facefx_data

    def get_facefx_db(self):
        '''Creates facefx database and assigns to "self.facefx_db".
        Saves database to cfg.facefx_data_path.

        Args:
            None

        Returns:
            None
        '''
        # 6.3 seconds for us voices
        self.facefx_db = self.get_facefx_data()
        self.set_data(cfg.facefx_data_path, self.facefx_db)

    def get_mocap_db(self):
        '''Creates mocap database and assigns to "self.mocap_db".
        Saves database to cfg.mocap_data_path.

        Args:
            None

        Returns:
            None
        '''
        # 37 seconds
        self.mocap_db = self.get_mocap_data()
        self.set_data(cfg.mocap_data_path, self.mocap_db)

    def update_db(self):
        '''Updates mocap and facefx database

        Args:
            None

        Returns:
            None
        '''
        self.get_facefx_db()
        self.get_mocap_db()

    def load_db(self):
        '''Loads mocap and facefx database

        Args:
            None

        Returns:
            None
        '''
        self.mocap_db = self.get_data(cfg.mocap_data_path)
        self.facefx_db = self.get_data(cfg.facefx_data_path)

    def query_anim_data_item(self, db, alt_db, anim):
        '''Searches for animation data in the main database first.
        If not found, searches in alternative database.
        Uses short name "cfg.anim_short" without facefx slashes

        Args:
            db (list): main database
            alt_db (list): alternative database
            anim_name (str): animation name

        Returns:
            dict: animation data
        '''
        found = self.get_data_from_db(db, cfg.anim_short, anim)
        if found:
            return found[0]
        else:
            found = self.get_data_from_db(alt_db, cfg.anim_short, anim)
            if found:
                return found[0]
            else:
                return None

    def get_anims_data_to_batch(self):
        '''Collects animation data for a given cfg.anims.
        If cfg.anims set in facefx config.
        If cfg.batch_mocap is set, first looks up in self.mocap_db.
        If not found, uses self.facefx_db.

        Args:
            None

        Returns:
            list: list of dicts
        '''
        data = []
        missing = []

        if cfg.batch_mocap:
            for anim in cfg.anims:
                found = self.query_anim_data_item(
                    self.mocap_db, self.facefx_db, anim)
                if found:
                    data.append(found)
                else:
                    missing.append(anim)
        else:
            for anim in cfg.anims:
                found = self.query_anim_data_item(
                    self.facefx_db, self.mocap_db, anim)
                if found:
                    data.append(found)
                else:
                    missing.append(anim)

        self.current_batch_data = data
        self.missing_batch_data = missing

    def get_animsets_data_to_batch(self):
        '''Collects anim data for a given cfg.animsets.
        If cfg.animsets set in facefx config.
        If cfg.batch_mocap is set, first looks up in self.mocap_db.
        If not found, uses self.facefx_db.

        Args:
            None

        Returns:
            list: list of dicts
        '''
        data = []
        missing = []

        if not cfg.batch_mocap:
            for animset in cfg.animsets:
                data += self.get_data_from_db(self.facefx_db,
                                              cfg.animset, animset)
                if not data:
                    missing.append(animset)
        elif cfg.batch_mocap:
            for animset in cfg.animsets:
                mocap_data = self.get_data_from_db(
                    self.mocap_db, cfg.animset, animset)
                facefx_data = self.get_data_from_db(
                    self.facefx_db, cfg.animset, animset)
                mocap_anims = [a[cfg.anim] for a in mocap_data]
                if not mocap_data and not facefx_data:
                    missing.append(animset)
                data += [fx for fx in facefx_data if fx[cfg.anim]
                         not in mocap_anims] + mocap_data

        self.current_batch_data = data
        self.missing_batch_data = missing

    def get_data_to_batch(self):
        '''Collects anim data for batch process.
        Depends if "cfg.anims" or "cfg.animsets" set in facefx config.
        Data assignes to "self.current_batch_data"

        Args:
            None

        Returns:
            None
        '''
        if cfg.anims:
            self.get_anims_data_to_batch()
        elif cfg.animsets:
            self.get_animsets_data_to_batch()
        else:
            sys.exit('Please, set anims or animsets in facefx config.')

    def create_missing_animsets(self):
        '''Creates empty animsets that are set in facefx config,
        but not exists in "self.animsets_data".

        Args:
            None

        Returns:
            None
        '''
        self.get_animsets_data()
        # cfg.animsets_dir.format(lang=self.cur_lang)
        existing_animsets = self.animsets_data.keys()
        self.batch_animsets = [ans.get(cfg.animset)
                               for ans in self.current_batch_data if ans.get(cfg.animset)]
        self.batch_animsets = list(set(self.batch_animsets))
        missing_animsets = [
            ans for ans in self.batch_animsets if ans not in existing_animsets]
        if not missing_animsets:
            return

        for missing in missing_animsets:
            self.create_empty_animset(missing)

    def create_empty_animset(self, animset):
        '''Creates empty animset and exports it
        to "cfg.animsets_dir.format(lang=self.cur_lang))".

        Args:
            None

        Returns:
            None
        '''
        self.add_animset(animset)
        self.export_animset(
            animset, cfg.animsets_dir.format(lang=self.cur_lang))
        self.save_actor()
        self.animsets_data[animset] = cfg.animsets_dir.format(
            lang=self.cur_lang) + animset + cfg.a_ext

    def delete_anims_from_animset(self, animset, anims):
        '''Deletes given animations from animset

        Args:
            animset (str): animset name
            anims (list): animation names

        Returns:
            None
        '''
        del_anims = []
        existing_anims = self.get_anim_names(animset)
        del_anims = [a for a in anims if a in existing_anims]
        if del_anims:

            for anim in del_anims:
                self.remove_animation(animset, anim)

    def process_facefx_anim(self):
        '''Redirects facefx process method
        to custom or default depends
        on "cfg.custom_process" state in facefx config

        Args:
            None

        Returns:
            None
        '''
        if cfg.custom_process:
            self.custom_facefx_anim_process()
        else:
            self.default_facefx_anim_process()

    def process_mocap_anim(self):
        '''Redirects mocap process method
        to custom or default depends
        on "cfg.custom_process" state in facefx config

        Args:
            None

        Returns:
            None
        '''
        if cfg.custom_process:
            self.custom_mocap_anim_process()
        else:
            self.default_mocap_anim_process()

    def exclude_anims(self):
        '''Deletes defined animations from
        "self.current_batch_data". 
        Which were manually corrected f.e.
        Excluded animations are taken from "cfg.excluded" dict
        where {'lang':[anim_names]}.

        Args:
            None

        Returns:
            None
        '''
        safe_data = []
        local_excluded = cfg.excluded.get(self.cur_lang, [])
        if not local_excluded:
            return

        for data in self.current_batch_data:
            if data[cfg.anim_short] in local_excluded:
                continue
            else:
                safe_data.append(data)

        if safe_data:
            self.current_batch_data = safe_data

    def default_facefx_anim_process(self):
        '''Creates single animation from the sound and subtitles.
        Smooths curves, rebuilds built-in facefx curves.
        Adds "cfg.lipsync_payload" payload and mocap depressor curve.
        Animation data is taken from "self.current_anim_data".

        Args:
            None

        Returns:
            None
        '''
        animset = self.current_anim_data[cfg.animset]
        anim = self.current_anim_data[cfg.anim]
        file_path = self.current_anim_data[cfg.file_path]
        self.analyze_sound(file_path, animset, anim)
        # self.smooth_curves(animset, anim_name)
        self.smooth_curves(animset, anim)
        # Partially depresses facial idles
        self.add_mocap_depressor(animset, anim)
        self.process_stress_curve(animset, anim)
        self.process_U_curve(animset, anim)
        self.add_payload(animset, anim, 0,
                         cfg.lipsync_payload)

    def process_anim(self):
        '''Redirects process to mocap or facefx
        based on "cfg.anim_type" key in "self.current_anim_data".
        Temporary mocap for us English only

        Args:
            None

        Returns:
            None
        '''
        if self.current_anim_data[cfg.anim_type] == cfg.mocap_type and self.cur_lang == 'us':
            self.process_mocap_anim()
        elif self.current_anim_data[cfg.anim_type] == cfg.facefx_type:
            self.process_facefx_anim()
        else:
            sys.exit(
                'Animation type is not suitable for processing or lang for mocap is set not to "us"')

    def custom_facefx_anim_process(self):
        '''Facefx process with special conditions.
        Initial purpose for modifying existing animations.

        Args:
            None

        Returns:
            None
        '''
        print 'Custom facefx process is not implemented yet. Passing.'
        pass

    def custom_mocap_anim_process(self):
        '''Mocap process with special conditions.
        Initial purpose for modifying existing animations.

        Args:
            None

        Returns:
            None
        '''
        print 'Custom mocap process is not implemented yet. Passing.'
        pass

    def default_mocap_anim_process(self):
        '''Creates single mocap animation.
        Takes names of animation data from "self.current_anim_data".
        Takes curves and values are from json file.
        Takes value of "cfg.file_path" in "self.current_anim_data".
        Builds linear tangents (slopes).
        Adds mocap payload "cfg.mocap_payload".
        Nutes facefx tag emotions.

        Args:
            None

        Returns:
            None
        '''
        animset = self.current_anim_data[cfg.animset]
        anim = self.current_anim_data[cfg.anim]
        file_path = self.current_anim_data[cfg.file_path]
        sound_path = self.current_anim_data[cfg.sound_path]

        anim_data = self.det_pickle_data(file_path)
        self.add_animation(animset, anim)
        self.set_framerate(animset, anim)
        curves = anim_data[animset][anim].keys()

        for curve in curves:
            self.add_curve(animset, anim, curve)
            # self.select_curve(curve)
            self.current_curve = curve
            anim_frame_values = anim_data[animset][anim][curve]
            # Emply blendshape curve
            if not anim_frame_values:
                continue
            frames = anim_frame_values.keys()
            frames = [int(fr) for fr in frames]
            frames.sort()

            for frame in frames:
                if frame == frames[0] or frame == frames[-1]:
                    slope = 0.0
                    value = anim_frame_values[frame]
                    self.insert_key(self.frames_to_time(
                        frame), value, slope, slope)
                else:
                    value = anim_frame_values.get(frame, 0)
                    prev_slope = slope
                    slope = self.calc_slope(
                        frame + 1, anim_frame_values.get(frame + 1, 0), frame, value)
                    # Get rig of negative values.
                    # They are ignored anyway in nodes with a range 0 1
                    # Slope should be zero also
                    if value < 0:
                        value = 0
                        slope = 0
                    self.insert_key(self.frames_to_time(
                        frame), value, prev_slope, slope)

        min_time = self.frames_to_time(frames[0])
        if sound_path:
            self.add_payload(animset, anim,
                             min_time, cfg.mocap_payload)
            self.mute_emotions(animset, anim, min_time)
            # Loads sound also
        # self.smooth_animation(anim_group, anim_name, curves)

    def calc_slope(self, a_frame, a_value, b_frame, b_value):
        '''Calculates linear tangent for key

        Args:
            a_frame (float): current frame
            a_value (float): current frame value
            b_frame (float): next frame
            b_value (float): next frame value

        Returns:
            None
        '''
        a_time = self.frames_to_time(a_frame)
        b_time = self.frames_to_time(b_frame)
        time = b_time - a_time
        value = b_value - a_value
        return value / time

    def smooth_curves(self, animset, anim):
        '''Reduces keys on a given curves with internal
        facefx smoothing algorithm.
        Takes list of curves from "cfg.smooth_curves"
        Sets first and the last keys to zero for smoothing curves.

        Args:
            animset (str): animset name
            anim (str): animation name

        Returns:
            None
        '''
        all_curves = getCurveNames(animset, anim)
        existing_curves = [
            s_curve for s_curve in cfg.smooth_curves if s_curve in all_curves]
        # Smooths and sets start, end keys to zero values to avoid animation breakage.
        for existing_curve in existing_curves:
            issueCommand('curve -edit -group "%s" -anim "%s" -name "%s" -owner "user";' %
                         (animset, anim, existing_curve))
            issueCommand('smooth -group "%s" -anim "%s" -curves "%s" -p0val 0.080000 -p0slope 0.000000 -p1val 1.000000 -p1slope 0.000000 -p2val 0.080000 -p2slope 0.000000 -length 0.250000 -scale 1.025000;' %
                         (animset, anim, existing_curve))
            keys = getKeys(animset, anim, existing_curve)
            start_index = 0
            end_index = len(keys) - 1
            issueCommand('key -edit -curveName "%s" -keyIndex %d -value 0.000000 -slopeIn 0.000000 -slopeOut 0.000000;' %
                         (existing_curve, start_index))
            issueCommand('key -edit -curveName "%s" -keyIndex %d -value 0.000000 -slopeIn 0.000000 -slopeOut 0.000000;' %
                         (existing_curve, end_index))

        # Lags "up_lip_up" curve to imitate muscles delay
        if cfg.smooth_curves[0] in existing_curves:
            issueCommand('smooth -group "%s" -anim "%s" -curves "%s" -p0val 1.000000 -p0slope -3.000000 -p1val 0.000000 -p1slope 0.000000 -p2val 0.000000 -p2slope 0.000000 -length 0.250000;' %
                         (animset, anim, cfg.smooth_curves[0]))
        else:
            pass

    def calc_blend_times(self, min_t, max_t):
        '''Builds mocap depressor curve for facefx process.
        Blends hardcoded in method.
        Returns None, None if animation is too short to add curve

        Args:
            min_t (float): animation start time
            max_t (float): animation end time

        Returns:
            tuple: depressor curve data list recognized by facefx and keys value list or None, None
        '''
        # Guess multiplier based on visuals
        blend_out_time = 0.5
        blend_in_time = 0.3
        if (max_t - min_t) >= (blend_out_time + blend_in_time):
            return [min_t, (min_t + blend_in_time), (max_t - blend_out_time), max_t], [0, 1, 1, 0]
        else:
            return None, None

    def get_min_max_times(self, data):
        '''Gets start and end time of animation.
        Data comes from facefx method "getKeys()"

        Args:
            data (tuple): list of times and list of values of animation

        Returns:
            tuple: start and end time
        '''
        times = [list(d)[0] for d in data]
        return min(times), max(times)

    def add_mocap_depressor(self, animset, anim):
        '''Creates curve, called 'facefx_to_mocap_depressor'
        in facefx animation.
        Curve depresses mocap animation while facefx animation playing,
        if any mocap animation is playing alongside the facefx.
        Curve name is hardcoded.
        Curve start and end time is taken from the lenght of the
        'Rate of Speech Scale' curve.
        Curve that always present among lipsync curves.
        If not, phrase is already too short for depression.     

        Args:
            animset (str): animset name
            anim (str): animation name

        Returns:
            None
        '''
        rate_of_speech = 'Rate of Speech Scale'

        try:
            curve_data = getKeys(animset, anim, rate_of_speech)
        except:
            return
        min_t, max_t = self.get_min_max_times(curve_data)
        blend_times, blend_values = self.calc_blend_times(min_t, max_t)
        # Phrase too short to add blends
        if not blend_times and not blend_values:
            return
        self.current_curve = 'facefx_to_mocap_depressor'
        self.add_curve(animset, anim, self.current_curve)

        for t, v in zip(blend_times, blend_values):
            self.insert_key(t, v, 0.0, 0.0)

        # Not good, but will keep seperate from each other
        # even whith the same keys in both of them
        min_t, max_t = self.get_min_max_times(curve_data)
        # Additive values are measured manually
        ros_blend_times, ros_blend_values = self.calc_blend_times(
            min_t - 0.125, max_t + 0.300)
        self.remove_curve(animset, anim, rate_of_speech)
        self.current_curve = rate_of_speech
        self.add_curve(animset, anim, self.current_curve)
        self.set_curve_to_manual(animset, anim, self.current_curve)
        for t, v in zip(ros_blend_times, ros_blend_values):
            self.insert_key(t, v, 0.0, 0.0)

    def mute_emotions(self, animset, anim, min_time):
        '''Depresses to zero facefx tag emotions in mocap animation.
        Takes list of tags from "cfg.tag_emotions"

        Args:
            animset (str): animset name
            anim (str): animation name
            min_time (float): event start

        Returns:
            None
        '''
        for tag in cfg.tag_emotions:
            self.add_event(animset, anim, tag, min_time)

    def normalize_value(self, v, min_v, max_v):
        '''Normalizes single curve value.
        Used for processing "Stress" internal facefx curve.

        Args:
            v (float): curve value
            min_v (float): minimum value
            max_v (float): maximum value

        Returns:
            float: 
        '''
        return (v - min_v) / (max_v - min_v)

    def process_stress_curve(self, animset, anim):
        '''Makes internal facefx curve useful for facefx animation.
        "low lip down" node is connected to "Stress" curve.
        Normalizes it and double smooths keys on curve.
        Stress curve name is hardcoded.

        Args:
            animset (str): animset name
            anim (str): anim name

        Returns:
            None
        '''
        stress_curve = 'Stress'

        try:
            self.set_curve_to_manual(animset, anim, stress_curve)
            issueCommand('smooth -group "%s" -anim "%s" -curves "%s" -p0val 0.080000 -p0slope 0.000000 -p1val 1.000000 -p1slope 0.000000 -p2val 0.080000 -p2slope 0.000000 -length 0.070000;' %
                         (animset, anim, stress_curve))
            curve_data = getKeys(animset, anim, stress_curve)
        except:
            return

        # time, value, slope in, slope out
        data = [list(d) for d in curve_data]
        # Gets min max for upper bound data
        upper_bound_range = [d[1] for d in data if d > 1]
        min_v, max_v = min(upper_bound_range), max(upper_bound_range)
        # Curve has not useful keys
        if min_v == max_v:
            return
        proc_data = []

        for d in data:
            if d[1] <= 1:
                # Sets lower bound keys to zero
                proc_data.append([d[0], 0, 0, 0])
            else:
                norm_v = self.normalize_value(d[1], min_v, max_v)
                proc_data.append([d[0], norm_v, d[2], d[3]])

        self.remove_curve(animset, anim, stress_curve)
        self.add_curve(animset, anim, stress_curve)
        self.current_curve = stress_curve
        for t, v, sl_in, sl_out in proc_data:
            self.insert_key(t, v, sl_in, sl_out)
        # Double smoothin to reduce the amount fo keys and fix tangents
        issueCommand('smooth -group "%s" -anim "%s" -curves "%s" -p0val 0.080000 -p0slope 0.000000 -p1val 1.000000 -p1slope 0.000000 -p2val 0.080000 -p2slope 0.000000 -length 0.070000;' %
                     (animset, anim, stress_curve))

    def process_U_curve(self, animset, anim):
        '''Custom process for U curve.
        Combines frequent short curve calls to constant animation.
        And normalizes curve values.
        Imitates muscle tention.
        Curve name is hardcoded.
        "W" curve is deleted if exists.

        Args:
            animset (str): animset name
            anim (str): anim name

        Returns:
            None
        '''
        curve = 'U'
        # No need in W curve as it doubles values and corrupts animation
        # Since U curve is normalized
        del_curve = 'W'
        try:
            self.remove_curve(animset, anim, del_curve)
        except:
            pass

        try:
            curve_data = getKeys(animset, anim, curve)
        except:
            return

        # time, value, slope in, slope out
        data = [list(d) for d in curve_data]
        # Double reducing
        proc_data = self.reduce_U_gaps(data)
        proc_data = self.reduce_U_gaps(proc_data)
        # If no keys were reduced
        # But commenting since all curves need to be normalized
        # if len(data) == len(proc_data):
        #     continue

        self.remove_curve(animset, anim, curve)
        self.add_curve(animset, anim, curve)
        self.current_curve = curve
        # Normalize values, to not to change mapping.
        # Maybe, changing mapping is easier.
        vals_data = [d[1] for d in proc_data]
        min_v, max_v = min(vals_data), max(vals_data)

        for t, v, sl_in, sl_out in proc_data:
            self.insert_key(t, self.normalize_value(
                v, min_v, max_v), sl_in, sl_out)
        # Double smoothing to reduce the amount of jittered keys and fix tangents
        issueCommand('smooth -group "%s" -anim "%s" -curves "%s" -p0val 0.080000 -p0slope 0.000000 -p1val 1.000000 -p1slope 0.000000 -p2val 0.080000 -p2slope 0.000000 -length 0.290000 -scale 1.118750;' %
                     (animset, anim, curve))

    def reduce_U_gaps(self, data, diff_delta=0.1):
        '''Deletes every key between two ones,
        which value difference is greater than "diff_delta"

        Args:
            data (list): animation data obtained from "getKeys()"
            diff_delta (float, optional): min max value threshold 
                for gap to be detected

        Returns:
            list: processed animation data 
        '''
        # Data is [[time, value, slope in, slope out],]
        cleanup_data = []

        for index, d in enumerate(data):
            d_prev = data[index - 1][1] if 0 <= (index - 1) else 0
            d_next = data[index + 1][1] if len(data) > (index + 1) else 0
            if d_prev > (d[1] + diff_delta) and (d[1] + diff_delta) < d_next:
                continue
            else:
                cleanup_data.append(d)

        return cleanup_data

    def move_face_idles_to_events(self):
        '''Moves mocap idle animations to "cfg.face_idle_animset_name"
        animset.
        Substituting animations with events.

        Args:
            None

        Returns:
            None
        '''
        self.load_actor()
        # Mocap is for 'us' localization only now
        self.cur_lang = 'us'
        self.get_animsets_data()
        # self.get_mocap_animsets()
        if self.levels:
            self.animsets = list(self.levels)
        else:
            sys.exit('Levels should be filled.')
        # Mounts base animset to copy mocap curve animation into
        self.mount_animset(cfg.face_idle_animset_path)
        for animset in self.animsets:
            if animset in [a for a in self.animsets_data.keys()]:
                self.mount_animset(self.animsets_data[animset])
            else:
                print 'Animset not present in data. Skipping.', animset
                continue
            mocap_names = self.get_anim_names(animset)
            for name in mocap_names:

                curve_name = name + cfg.curve_anim_name_prefix
                self.rename_animation(animset, name, curve_name)
                # Removes curve animation from base animset if exists
                face_idles_names = self.get_anim_names(
                    cfg.face_idle_animset_name)
                if curve_name in face_idles_names:
                    self.remove_animation(cfg.face_idle_animset_name, name)
                self.move_animation(
                    animset, cfg.face_idle_animset_name, curve_name)
                # Replaces moved and renamed animation by and empty one
                self.add_animation(animset, name)
                # By default event is taken from animset named cfg.base_animset
                self.add_custom_persist_event(
                    animset, name, curve_name)

            self.save_actor()
            self.set_console_vars()
            self.unmount_animset(animset)

        self.unmount_animset(cfg.face_idle_animset_name)
        self.save_actor()

    def check_cfg(self):
        '''Checks if config path variables exists.
        Takes variables from "cfg = base_config.Config()".
        Analyses only str type variables.
        Uses 'us' lang for {lang} variable formatting.

        Args:
            None

        Returns:
            None
        '''
        vars = [v for k, v in cfg.__dict__.iteritems() if isinstance(v, str)]
        got_missing = False

        for v in vars:
            if ':' in v and '.' in v:
                if os.path.isfile(v.format(lang='us')):
                    continue
                elif os.path.isdir(v.format(lang='us')):
                    continue
                else:
                    print v
                    got_missing = True

        if got_missing:
            err_msg = '''\nFix above base config file paths to continue batch.\nu:/face/scripts/base_config.py'''
            sys.exit(err_msg)

    def publish_lang(self, lang):
        '''Publishes animations for current language.
        Animations is taken from "self.current_batch_data".
        Lang is set to "self.cur_lang".
        Publish is set per animset to avoid memory crashes.

        Args:
            lang (str): current processing language

        Returns:
            None
        '''
        self.cur_lang = lang
        if cfg.update_db:
            self.update_db()
        else:
            self.load_db()
        self.get_data_to_batch()
        self.exclude_anims()  # deletes stated animations from self.current_batch_data
        self.set_analyze_lang()
        self.set_console_vars()
        self.load_actor()
        self.create_missing_animsets()
        animsets = list(set([ans[cfg.animset]
                             for ans in self.current_batch_data]))

        for animset in animsets:
            self.mount_animset(self.animsets_data[animset])
            self.publish_actor_go()
            self.set_console_vars()
            self.unmount_animset(animset)

        if self.missing_batch_data:
            print 'Defined in facefx config but not processed.'
            print 'Missing:'

            for d in self.missing_batch_data:
                print d

        self.close_actor()

    def batch_lang(self, lang):
        '''Processes animations for current language.
        Animations is taken from "self.current_batch_data".
        Lang is set to "self.cur_lang".


        Args:
            lang (str): current processing language

        Returns:
            None
        '''
        self.cur_lang = lang
        if cfg.update_db:
            self.update_db()
        else:
            self.load_db()
        self.get_data_to_batch()
        self.exclude_anims()  # deletes stated animations from self.current_batch_data
        self.set_analyze_lang()
        self.set_console_vars()
        self.load_actor()
        self.create_missing_animsets()
        animsets = list(set([ans[cfg.animset]
                             for ans in self.current_batch_data]))

        for animset in animsets:
            anims_data = [
                anim for anim in self.current_batch_data if anim[cfg.animset] == animset]
            self.mount_animset(self.animsets_data[animset])
            anims = [data[cfg.anim] for data in anims_data]
            self.delete_anims_from_animset(animset, anims)

            for data in anims_data:
                self.current_anim_data = data
                self.process_anim()

            self.save_actor()
            self.set_console_vars()
            self.unmount_animset(animset)

        if self.missing_batch_data:
            print 'Defined in facefx config but not processed.'
            print 'Missing:'

            for d in self.missing_batch_data:
                print d

        self.close_actor()

    def batch_langs(self):
        '''Launches animation process for every language
        in "cfg.langs" facefx config

        Args:
            None

        Returns:
            None
        '''
        for lang in cfg.langs:
            self.batch_lang(lang)

    def publish_langs(self):
        '''Launches animation publish process for every language
        in "cfg.langs" facefx config

        Args:
            None

        Returns:
            None
        '''
        for lang in cfg.langs:
            self.publish_lang(lang)

    def run(self):
        '''Initiates batch process.

        Args:
            None

        Returns:
            None
        '''
        self.check_cfg()
        if cfg.batch and cfg.publish:
            self.batch_langs()
            self.publish_langs()
        elif cfg.batch:
            self.batch_langs()
        elif cfg.publish:
            self.publish_langs()
        else:
            print 'Select process in facefx config.'
            return


sa = SetAnimation()
sa.run()
