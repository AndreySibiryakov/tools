# -*- coding: utf-8 -*-

from moviepy.editor import *


def cut(vid, t_start, t_end):
    vid_ext = vid.split('.')[-1]
    vid_path = vid.split('.' + vid_ext)[0]
    out_file = vid_path + '_cut.' + vid_ext
    video = VideoFileClip(vid).subclip(t_start, t_end)
    video.write_videofile(out_file,
                          preset='slow',
                          bitrate="50000k",
                          progress_bar=False)


vid = r'd:\downloads\VID_20191030_141908.mp4'
cut(vid, '00:00:25,000', '00:00:45,000')
