'''
Animation data structure
group
    anim
        curve
            frame:value
'''
import os
import sys
sys.path.extend(['u:/face/scripts/'])
import base_config
import shutil
import pysvn
import pyperclip


'''Gets or set bone mapping for a character, bone per vertex correspondance.
    Since bones are constrained to vertices.
    And vertices are driven with a blendshapes.

Args:
    folder (str): path to bone mapping files that contain dictionary,
        dumped with a pickle
    set_mapping (bool, optional): used with cubes and mapping params.
        Defaults to False
        Sets custom mapping for a character
    cubes (list, optional): used with set and mapping params.
        Cubes that visualize joint placement
    mapping (dict, optional): used with set and cubes params.
        Bone per vertex correspondance

Returns:
    dict: default or custom bone per vertex correspondance for a '*_head' mesh

Examples:
    >>> print([i for i in example_generator(4)])
    [0, 1, 2, 3]

'''

cfg = base_config.Config()


class CommitAnimation(object):

    def __init__(self):
        self.animsets = []
        # {animset_name:animset_path}
        self.animsets_data = {}
        self.cur_lang = ''

    def get_animsets_data(self):
        # To avoid duplicates when several langs can be processed at a time
        self.animsets_data = {}
        a_dir_path = cfg.animsets_dir.format(lang=self.cur_lang)

        for name in os.listdir(a_dir_path):
            a_file_path = os.path.join(a_dir_path, name)
            if os.path.isfile(a_file_path) and a_file_path.endswith(cfg.a_ext):
                self.animsets_data[name.split(cfg.a_ext)[0]] = a_file_path

        if not self.animsets_data:
            exit_message = 'No animsets found in %s.' % a_dir_path
            sys.exit(exit_message)

    def commit_published(self):
        # Copies files to commit dirs
        animsets_to_copy = {}

        for lang in cfg.langs:
            self.cur_lang = lang
            self.get_animsets_data()
            if cfg.levels:
                self.animsets = list(cfg.levels)
            else:
                self.animsets = [a for a in self.animsets_data.keys()]

            a_dir_path = cfg.animsets_dir.format(lang=lang)
            lang_animsets_ingame = []

            for name in os.listdir(a_dir_path):
                a_file_path = os.path.join(a_dir_path, name)
                if os.path.isfile(a_file_path) and a_file_path.endswith(cfg.ai_ext):
                    lang_animsets_ingame.append(a_file_path)

            animsets_to_copy[lang] = lang_animsets_ingame

        for lang, ai_files in animsets_to_copy.iteritems():

            for ai_path in ai_files:
                shutil.copy2(
                    ai_path, cfg.destination_animsets_dir + lang + '/')

        # Commits files
        m_l_message = ''
        if cfg.batch_lipsync and cfg.batch_mocap:
            m_l_message = ' mocap and lipsync on '
        elif cfg.batch_lipsync:
            m_l_message = ' lipsync on '
        elif cfg.batch_mocap:
            m_l_message = ' mocap on '

        if len(cfg.commit_label) > 1:
            cfg.commit_label += ' '

        commit_message = cfg.commit_label + 'Batched' + m_l_message + ', '.join(str(a) for a in self.animsets) + \
            ' for ' + ', '.join(str(l) for l in cfg.langs)
        client = pysvn.Client()
        commit_info = client.checkin(
            cfg.destination_animsets_dir, commit_message)
        revision = str(commit_info).split(' ')[-1][:-1]
        pyperclip.copy(revision)
        print '# Commited at revision', revision
        print '# Revision number copied to clipboard.'


#
sa = CommitAnimation()
if cfg.commit:
    sa.commit_published()
