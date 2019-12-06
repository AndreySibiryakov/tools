from subprocess import Popen, PIPE
import os
import sys
import facefx_config as fc

if os.path.isdir("d:/u-source"):
    proc = Popen(["subst", "U:", "d:\u-source"], stdout=PIPE)
    output = proc.communicate()[0]
else:
    sys.exit(
        'Found no u-source by default path. \nPlease, change the path in the config.py file.')


class Config(object):

    def __init__(self):
        self.u_scripts_dir = 'u:/face/scripts/'
        self.raw_mocap_anims_dir = 'u:/face/mocap/anims_raw/'
        self.mocap_anims_dir = 'u:/face/mocap/anims/'
        self.mocap_to_facefx_dir = 'u:/face/mocap/facefx/'
        self.mocap_template_chr = 'u:/face/mocap/chrs/miller.mb'
        self.sounds_database_path = 'u:/face/mocap/anims_to_facefx/sounds_database.txt'
        self.animsets_dir = 'u:/face/facefx/animsets_{lang}/'
        # Path to commit from
        self.destination_animsets_dir = 'c:/SVN/content/facefx/'
        self.sounds_dir = 'c:/SVN/content/sounds.{lang}/voices/'

        # Miller copied from d:/.work/.chrs/miller/.facefx/miller_facefx_scaled.facefx
        # self.actor = 'd:/.work/.facefx_general/batch_template.facefx'

        # Anna from d:\.work\.tech\anna_cm_idle\.facefx\anna_cm_idle_bones_up_down_fxgraph.facefx
        # With up down seperate lips setup. Compatible with Miller's cm
        self.actor = 'd:/.work/.chrs/miller/.facefx/miller_fs.facefx'
        self.a_ext = '.animset'
        self.ai_ext = '.animset_ingame'
        self.facefx_ingame_ext = '.facefx_ingame'
        self.txt_ext = '.txt'
        self.mb_ext = '.mb'
        self.py_ext = '.py'
        # Analysis Actor
        self.aa = 'Custom'
        # Search key to match folder names
        # m3 is for Metro3 project
        self.key = 'm3'
        # Conditions to filter sounds upon
        self.true_conditions = ['.flac']
        # Verified with a sound engineer.
        # Sounds with a listed keys in names are not spoken directly by humans
        self.false_conditions = ['_narration_',
                                 '_audiolog_',
                                 '_radiomessage_',
                                 '_radiostation_',
                                 '_radiocomm_',
                                 '_tmp_']

        self.attr_mapping = {"rotateX": "pitch",
                             "rotateY": "yaw", "rotateZ": "roll"}
        self.attr_max_degree = 30
        self.file_directory = 'u:/face/mocap/facefx/'
        self.ext = '.txt'
        self.sp = 'driv_'
        # Config for sounds database and name verification
        self.search_dir = 'c:/SVN/content/sounds.us/voices/'
        self.regex = ur"(.*sounds\.us.)|(\.flac)"
        self.sounds_database = 'sounds_database'
        self.sounds_database_path = self.file_directory + self.sounds_database + self.ext
        self.mocap_payload = 'null_face'
        self.lipsync_payload = 'facefx_background'
        self.payload_animset = 'payload'
        self.payload_anim = 'payload'
        self.base_animset = 'anim'
        self.anim_animset_path = 'u:/face/facefx/animsets_us/anim_motions_emotions.animset'
        self.face_idle_animset_name = 'face_idles'
        self.face_idle_animset_path = 'u:/face/facefx/animsets_us/face_idles.animset'
        self.curve_anim_name_prefix = '_curves'
        # Created seperate file for general facefx batch commands
        # u:\face\scripts\facefx_config.py
        # If not any, nothing would be batched
        self.tag_emotions = ['anger', 'contempt', 'death', 'disgust', 'eat', 'fear', 'fear_death', 'low_emotion',
                             'regret', 'sadness', 'sleep', 'smile', 'smile_low', 'surprise_low', 'teeth_open', 'wide_smile', 'wonder']
        self.a_langs = {'us': 'USEnglish',
                        'ru': 'German',
                        'uk': 'German',
                        'fr': 'French',
                        'it': 'Italian',
                        'es': 'Spanish',
                        'de': 'German',
                        'jp': 'German'}
        # Naming for anim batch data db keys
        self.animset = 'animset'
        self.anim = 'anim'
        # dict key used to search for a given animations in data base
        self.anim_short = 'anim_short'
        self.file_path = 'path'
        self.anim_type = 'anim_type'
        self.facefx_type = 'facefx'
        self.mocap_type = 'mocap'
        self.sound_path = 'sound_path'
        self.facefx_data_path = 'u:/face/data/facefx.json'
        self.mocap_data_path = 'u:/face/data/mocap.json'
        self.custom_process = fc.custom_process
        self.batch_mocap = fc.batch_mocap
        self.animsets = fc.animsets
        self.anims = fc.anims
        self.langs = fc.langs
        # Specifies levels (animsets) to batch only
        self.mocap_to_events = fc.mocap_to_events
        self.publish = fc.publish
        self.batch = fc.batch
        self.commit = fc.commit
        self.commit_label = fc.commit_label
        self.excluded = fc.excluded
        self.update_db = fc.update_db
        # Currently the only curves that, I feel, need to be smoothed.
        self.smooth_curves = ['up_lip_up', 'Y', 'CH', 'Y', 'U', 'W', 'F']
