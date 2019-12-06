# If not any language is set, nothing would be batched
# Specifies language to batch sounds on:
# List:
'''
us
ru
fr
it
es
de
'''
# Several langs should be seperated by commas.
# ['us','ru', 'fr', 'it', 'es', 'de', 'jp']
langs = ['us', 'uk', 'ru']

# Specifies animsets to batch only
# If all levels, leave blank []
# List:
'''
'm3_12_valley',
'm3_08_desert',
'm3_ending',
'm3_13_dead_city',
'm3_12_autumn',
'm3_10_yamantau',
'm3_09_summer',
'm3_06_spring',
'm3_06_bridge',
'm3_05_winter',
'm3_02_dead_moscow',
'm3_05_chase',
'universal_m3',
'm3_dlc1_epilogue',
'm3_dlc1'

# Mocap animsets
'alyosha_idle',
'damir_idle',
'duke_idle',
'face_idles',
'idiot_idle',
'krest_idle',
'miller_fs_idle',
'miller_idle',
'sam_idle',
'savage_idle',
'stepan_idle',
'tokarev_idle',
'woman_idle',
'yermak_idle'
'''

# Simple name. Sound dir name equals to animset name.
# F.e. "m3_02_dead_moscow" for sounds,
# "alyosha_idle" for mocap animsets.
# If anims set, animset ignored.
animsets = ['m3_dlc2']

# Simple name, sound file name if it is a facefx animation.
# F.e. "cha_000_newchasestart_04_11" or "Alyosha_angry".
# If anims defined, animsets ignored.
anims = []

# Some other process, than default.
# Could be additive animation curves smoothing
# or mocap animation curves reducing.
# Default value is False
custom_process = False

# Ignored list of animation names.
# If animation contains manual corrections, f.e.
excluded = {'us': ['val_40_admiral_01_02',
                   'val_40_admiral_01_06',
                   'val_40_admiral_01_08',
                   'val_40_admiral_01_13',
                   'val_40_admiral_01_14',
                   'val_40_admiral_01_19',
                   'val_40_admiral_01_20',
                   'val_40_admiral_01_25',
                   'val_40_admiral_01_26',
                   'val_40_admiral_01_28',
                   'val_40_admiral_01_29',
                   'val_40_admiral_01_30',
                   'val_40_admiral_01_34',
                   'val_40_admiral_01_34_02',
                   'val_40_admiral_01_34_04',
                   'val_40_admiral_01_35',
                   'val_40_admiral_01_36',
                   'val_40_3_admiral_guitar_01_07',
                   'val_050_finale_01_01_00',
                   'val_050_finale_01_01_01',
                   'val_050_finale_01_01_02',
                   'val_050_finale_01_01_03',
                   'val_050_finale_01_01_04',
                   'dlc1_12_1_startingout_01_06']}

# Collects information about sounds in VO directory
# and mocap files in mocap/facefx.
# Database update takes near 2 minutes.
# Once updated, database stored in "u:\face\data\"
# False only for one lang being batched several times
# for a short period of time.
# Default True
update_db = True

# Mocap includes in batch process if True.
# Mocap is substituted with facefx animations if False.
# Default True
batch_mocap = True

# Moves facial idles to anim group and replace
# then by empty animation with event inside.
# Does not work now.
mocap_to_events = False

# Creates facefx or mocap animation in facefx.
# Default True
batch = True

# Prepares facial lip-sync and mocap for engine.
# Default True
publish = True

# Commits to svn
# Default True
commit = False

# Sets tag or label. For example 'E3', 'MS20'
# This is not a commit comment. Comment is auto generated
# Default ''
commit_label = ''
