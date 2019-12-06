load actor
check input params
check animsets to batch
get data for sounds
main batch
save(export or unmount)
exit


def __init__(self):
    self.animsets = []
    self.sounds = []
    self.mocap_anims = {}
    self.facefx_anims = {}


def proc_lipsync(self):
    self.get_config_data()


def get_config_data(self):
    set_proc_animsets()
    set_proc_anims()
    pass

# Lang dependent
# self.cur_lang should be set


def set_animsets(self):
    # Collects existing .animset
    # Results self.animsets_data {name:path}
    self.get_animsets_data()
    # Results:
    # self.mocap_data {mocap anim path:anim name}
    # self.mocap_animations [anim name]
    # self.mocap_animsets [animset name]
    self.get_mocap_data()
    # Results self.sound_dirs_data {animset name:animset sound dir path}
    # e.g.: 'm3_12_valley': 'c:/SVN/content/sounds.us/voices/m3_12_valley'
    self.get_sound_dirs_data()
    # Create empty animsets for those who not exists still
    both_animsets = self.sound_dirs_data.keys() + self.mocap_animsets
    for animset in both_animsets:
        if animset in self.animsets_data.keys():
            continue
        else:
            self.create_empty_animset(animset)
    # Won't do multilang at a time. No need in it, maybe
    self.get_animsets_data()
    # Overwrites default animsets list
    if self.levels:
        self.animsets = self.levels
        return
    # Assings appropriate animsets names for batch
    if cfg.batch_lipsync and cfg.batch_mocap:
        self.animsets = both_animsets
    elif cfg.batch_lipsync:
        self.animsets = self.sound_dirs_data.keys()
    elif cfg.batch_mocap:
        self.animsets = self.mocap_animsets
    else:
        sys.exit('Nor lipsync, neither mocap options are selected for batch')


def set_langs(self):
    if not cfg.batch_mocap and not cfg.langs:
        sys.exit('Languages not defined.')
    self.langs = cfg.langs
    # elif cfg.batch_mocap


def get_anim_data():
    # Generates names lookup dict
    # {short_name:[facefx_name, path]}


def get_anims_for_batch(animset):

    # Gets existing anims in animset []
    animset_anims = self.get_anim_names(animset)
    # Gets stated only
    if cfg.facefx_phrases_only:
        sounds = cfg.facefx_phrases_only
    else:
        sounds = self.get_sounds(self.sound_dirs_data[animset])
    split_sounds = {anim: sound for anim, sound in split_sound(sounds)}
    # Gets excluded
    # self.sounds = self.exclude_sounds(sounds)
    # Gets excluded phrases for current localization
    local_excluded = cfg.excluded_from_batch.get(lang, [])

    for excl_path in local_excluded:
        excl_name = excl_path.split('\\')[-1]
        if excl_name in split_sounds.keys():
            del split_sounds[excl_name]

    # Removes unused

    # Removes mocap
    self.sounds = self.substract_mocap_animations(sounds)


def split_sound(self, sound):
    # File structure example
    # r'c:\SVN\content\sounds.us\voices\m3_12_valley\val_003_80_alchemist_01_09_01.flac'
    split_path = sound.split(os.sep)
    a = split_path[-1].split('.')[0]
    anim = '\\'.join(split_path[4:-1] + [a])
    return anim, sound


def anims(self):
    self.load_actor()
    self.set_console_vars()
    self.set_langs()
    self.set_animsets()
    for animset in self.animsets:
        self.cur_animset = animset
        self.mount_animset()
        self.get_anims_for_batch()
        # Both facefx and mocap
        self.batch_anims()
        self.save_actor()
        self.unmount_animset()


def set_lang_unique_data():
    self.set_console_vars()
    self.set_analyze_lang()


def get_mocap_data(self):
    if self.cur_lang != 'us':
        self.mocap_data = {}
        self.mocap_animations = []
        return

    # Results self.mocap_files [path]
    self.get_mocap_files()

    for file in self.mocap_files:
        anim_data = self.get_data(file)
        animset = anim_data.keys()[0]
        self.mocap_animsets.append(animset)
        self.mocap_data[file] = animset
        anim_name = anim_data[animset].keys()[0]
        self.mocap_animations.append(anim_name)

    self.mocap_animsets = list(set(self.mocap_animsets))


def get_mocap_files(self):

    for name in os.listdir(cfg.mocap_to_facefx_dir):
        if not name.endswith('.txt') or 'sounds_database' in name:
            continue

        self.mocap_files.append(os.path.join(
            cfg.mocap_to_facefx_dir, name))


def create_empty_animset(self, animset):
    self.load_actor()
    self.add_animset(animset):
    self.export_animset(
        animset, cfg.animsets_dir.format(lang=self.cur_lang))
    self.save_actor()
