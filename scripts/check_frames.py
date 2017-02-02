#!/usr/bin/env python3

import glob
import numpy as np
import os
import sys

video_path = "/data/interest_annotate/static/annotate/videos/"

def main():
    video_num = 0

    links_path = os.path.join(video_path, 'links') 
    if not os.path.isdir(links_path):
        os.mkdir(links_path)

    # Find all videos by listing the directories in video_path
    for filename in os.listdir(video_path):
        fullpath = os.path.join(video_path, filename)

        # Skip non-directories and 'cache'
        if not os.path.isdir(fullpath) or filename in ('cache', 'links'):
            continue

        print('Processing movie', filename, '...')

        linkname = "video_{}".format(video_num)
        link_path = os.path.join(links_path, linkname)

        if os.path.islink(link_path):
            os.remove(link_path)
        os.symlink(fullpath, link_path)

        video_num += 1

        shots = {}
        shot_path = os.path.join(fullpath, 'movies')
        for shot_filename in os.listdir(shot_path):
            start_frame = int(shot_filename.split('-')[0])
            assert(start_frame not in shots)
            shots[start_frame] = shot_filename

        ns = len(shots)
        s = int(np.sqrt(ns))

        t = s*s
        diff = ns-t
        if diff != 0:
            print('Truncating number of shots: {} - {} = {} = {}².'.format(ns, diff, t, s))
        else:
            print('No truncation needed, since {} = {}².'.format(ns, s))

        for start_frame in sorted(shots.keys())[:t]:
            shot_filename = shots[start_frame]
            shot_fullpath = os.path.join(shot_path, shot_filename)

            # skip non-files
            if not os.path.isfile(shot_fullpath):
                continue

            # skips files that don't look like mp4 videos
            if os.path.splitext(shot_filename)[1] != '.mp4':
                print('Skipping {}, since it does not end with .mp4.'.
                      format(shot_filename))
                continue

            glob_fname = link_path + '/images/midframe/* (' + \
                         os.path.splitext(shot_filename)[0] + ').jpg'
            glob_fname.replace("\[", "\\\\[")
            glob_fname.replace("\]", "\\\\]")
            image_path = glob.glob(glob_fname)

            link_fullpath = os.path.join(link_path, 'movies', shot_filename)

            if len(image_path) != 1:
                print('WARNING!!! Image not found for video', link_fullpath, file=sys.stderr)
                #return
            else:
                image_filename = os.path.basename(image_path[0])
                os.utime(image_path[0], None)
                print(image_filename)

if __name__ == '__main__':
    main()
