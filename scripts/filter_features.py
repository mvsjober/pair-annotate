#!/usr/bin/env python3

import copy
import math
import os
import re
import sys

base_path = '/group/mediaeval/public_html/dl/devset'
video_path = os.path.join(base_path, 'videos')
feature_path = os.path.join(base_path, 'features', 'Features_From_FudanUniversity')
#feature_path = os.path.join(base_path, 'features', 'Features_From_MultimodalPersonDiscovery')

p = re.compile(r'^\d+_(\d+-\d+)\.jpg$')
pv = re.compile(r'/video_\d+/')
pvs = re.compile(r'^video_\d+$')
pn = re.compile(r'\d+-\d+')
allowed_list = {}
vid_counts = {}

# Find all videos by listing the directories in video_path
for filename in os.listdir(video_path):
    fullpath = os.path.join(video_path, filename)
    
    image_files = os.listdir(os.path.join(fullpath, 'images'))
    N = len(image_files)

    # sanity check that N=s^2
    s = int(math.sqrt(N))
    t = s*s
    assert(t == N)

    allowed_video = set()
    for ifile in image_files:
        m = p.match(ifile)
        assert(m)
        allowed_video.add(m.group(1))

    assert(N == len(allowed_video))
    allowed_list[filename] = allowed_video
    vid_counts[filename] = N
    
    #print("{} should have {} items.".format(filename, N))

for root, dirs, files in os.walk(feature_path):
    root_short = '/'.join(root.split('/')[7:])
    if len(dirs) > 1:
        m = pvs.match(dirs[0])
        if not m:
            print('SCANNING', ' '.join(dirs))
        else:
            ldirs = len(dirs)
            print('VIDEO', root_short, ldirs)
            assert(ldirs == 78)

    if len(files) > 1:  # probably has features
        # print(root)
        # print(root, len(dirs), len(files))
        m = pv.search(root)
        assert(m)
        vid = m.group(0)[1:-1]
        assert(vid in allowed_list)
        al = allowed_list[vid]
        missing = copy.copy(al)

        diff = len(files) - len(al)

        to_remove = []
        for fname in files:
            mn = pn.search(fname)
            assert(mn)
            video_num = mn.group(0)
            if video_num not in al:
                remove_fname = os.path.join(root, fname)
                # print("BOOM", os.path.join(root, fname))
                to_remove.append(remove_fname)
            else:
                missing.remove(video_num)

        if len(missing) > 0:
            print(root_short, "has missing", ' '.join(missing))
        if len(to_remove) > 0:
            print(root_short, "would remove", len(to_remove), "files")
            #for f in to_remove:
            #    os.remove(f)
        
        if diff + len(missing) != len(to_remove):
            print("BOOM", root)
            print(len(files), len(al))
            print(diff, len(to_remove))
            print('\n'.join(files))
            print('\n'.join(al))
            print('\n'.join(to_remove))
            sys.exit(0)
