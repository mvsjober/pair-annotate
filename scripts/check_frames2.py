#!/usr/bin/env python3

import glob
import numpy as np
import os
import sys

def check(cdir):
    shot_path = os.path.join(cdir, 'movies')
    shots = {}
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
        return

    for i, start_frame in enumerate(sorted(shots.keys())):
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

        glob_fname = '*' + os.path.splitext(shot_filename)[0] + '.jpg'
        glob_fname = os.path.join(cdir + 'images', glob_fname)
        glob_fname.replace("\[", "\\\\[")
        glob_fname.replace("\]", "\\\\]")
        image_path = glob.glob(glob_fname)

        link_fullpath = os.path.join(cdir, 'movies', shot_filename)

        if len(image_path) != 1:
            print('WARNING!!! Image not found for video', link_fullpath, file=sys.stderr)
            #return
        else:
            image_filename = os.path.basename(image_path[0])
            os.utime(image_path[0], None)
            #print(image_filename)


        if i < t:
            print("Keeping", shot_filename, image_filename)
        else:
            print("Deleting", shot_fullpath, image_path[0])
            #os.remove(shot_fullpath)
            #os.remove(image_path[0])

if __name__ == '__main__':
    check(sys.argv[1])
