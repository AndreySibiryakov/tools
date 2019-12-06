# -*- coding: utf-8 -*-
import os
from kanji_to_romaji import kanji_to_romaji
import codecs
import re


def transliterate_jp(sounds_dir):

    for path, dirs, file_names in os.walk(sounds_dir):

        for file_name in file_names:
            if not file_name.endswith('.txt'):
                continue
            sub = os.path.normpath(os.path.join(path, file_name))
            try:
                f = codecs.open(sub, encoding='utf-8', mode='r+')
                jp_data = f.read()
            except Exception:
                print 'Contains no japanese', sub
                f.close()
                continue
            # if len(jp_data) > 1:
            try:
                # proc_data = kanji_to_romaji(jp_data.encode('UTF-8'))
                proc_data = parse_data(jp_data, sub)
            except Exception:
                print 'Unknown data inside. Skipping.', sub
                f.close()
                continue
            f.seek(0, 0)
            f.truncate()
            f.write(proc_data)
            f.close()


def add_spaces(data):
    data = re.sub('\s*\s', ' ', data)
    data = re.sub('_', '', data)
    return data


def parse_data(data, sub):
    proc_data = []

    for d in data.split(' '):
        if '<' in d or '>' in d in d:
            proc_data.append(d)
        else:
            proc_element = kanji_to_romaji(d)
            proc_data.append(proc_element)
            # if not re.search('[a-aA-z]', proc_element):

    proc_data_str = ' '.join([d for d in proc_data])
    proc_data_str_no_tags = re.sub('( \<|\<).*?(\>|\> )', '', proc_data_str)
    if len(proc_data_str_no_tags) <= 4:
        print proc_data_str_no_tags, sub

    return proc_data_str


sounds_dir = 'c:/SVN/content/sounds.jp/voices/m3_dlc2/'
# test_dir = 'd:/.work/.tech/jp_lang/long_test/'
'''
jp_data = r'{"anim|anger" magnitude=0 blendin=0.6 blendout=0.6} {"anim|disgust" magnitude=0 blendin=0.6 blendout=0.6} {"anim|fear" magnitude=0 blendin=0.6 blendout=0.6} {"anim|sadness" magnitude=0 blendin=0.8 blendout=0.6} {"anim|smile" magnitude=0.8 blendin=0.6 blendout=0.8 persist} {"anim|wide_smile" magnitude=0 blendin=0.6 blendout=0.6} {"anim|wonder" magnitude=0 blendin=0.5 blendout=0.6} {"anim|sleep" magnitude=0 blendin=0.5 blendout=0.6} {"anim|surprise_low" magnitude=0 blendin=0.3 blendout=0.6} {"anim|smile_low" magnitude=0.65 blendin=0.3 blendout=0.6 persist} {"anim|low_emotion" magnitude=0 blendin=0.3 blendout=0.6} {"anim|teeth_open" magnitude=0 blendin=0.3 blendout=0.6}ヤシの木に！ ハハハ{"anim|anger" magnitude=0 blendin=0.6 blendout=0.6} {"anim|disgust" magnitude=0 blendin=0.6 blendout=0.6} {"anim|fear" magnitude=0 blendin=0.6 blendout=0.6} {"anim|sadness" magnitude=0 blendin=0.6 blendout=0.6} {"anim|smile" magnitude=0 blendin=0.6 blendout=0.8} {"anim|wide_smile" magnitude=0 blendin=0.6 blendout=0.6} {"anim|wonder" magnitude=0 blendin=0.6 blendout=0.6} {"anim|sleep" magnitude=0 blendin=0.6 blendout=0.6} {"anim|surprise_low" magnitude=0 blendin=0.3 blendout=0.6} {"anim|smile_low" magnitude=0 blendin=0.3 blendout=0.6} {"anim|low_emotion" magnitude=0 blendin=0.3 blendout=0.6} {"anim|teeth_open" magnitude=0 blendin=0.3 blendout=0.6}'
jp_spaced = add_spaces(jp_data)
print jp_spaced
proc_data = parse_data(jp_spaced)
print proc_data
'''
transliterate_jp(sounds_dir)
# c:\SVN\content\sounds.jp\voices\m3_12_valley\val_19_tortugaentry_01_04.flac
