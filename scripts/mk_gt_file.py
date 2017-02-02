#!/usr/bin/env python3

#------------------------------------------------------------------------------

import sys
import numpy as np

threshold = 0.01

#------------------------------------------------------------------------------

# Read input file with format like:
#     video_0,1025 (997-1054).jpg,0.004869209
# and put into data dictionary, e.g.:
#     data[0] => [list of data dict-objects for video_0]

data = {}
with open(sys.argv[1], 'r') as fp:
    for line in fp:
        (video, target_fname, score) = line.split(',')

        # use number for easier sorting later :-)
        video_num = int(video.split('_')[1])

        # for image names we have to edit it a bit ...
        if ' ' in target_fname:
            target_fname = target_fname.replace(' ', '_').replace('(', '').replace(')', '')

        if video_num not in data:
            data[video_num] = []

        data[video_num].append({'name': target_fname, 
                                'score': float(score)})

# Loop over data dictionary and process for each video

for video_num in sorted(data.keys()):
    vdata = data[video_num]

    d = np.array([t['score'] for t in vdata])

    # normalise so that maximum = 1.0
    #vsum = np.sum(values)
    #d = d/vsum
    max_d = np.max(d)
    values_norm = np.sort(d)/max_d

    dd = np.array([1, 1, 1, -1,  -1, -1])/6.0
    values_diff = np.convolve(values_norm, dd, mode='same')
    lenn = len(values_norm)
    values_diff[0:3] = 0.0
    values_diff[lenn-1] = values_diff[lenn-2] = values_diff[lenn-3]

    values_diff2 = np.convolve(values_diff, dd, mode='same')
    #values_diff2 = np.diff(values_diff)

    #am=np.argmax(values_norm>0.5)
    half=lenn//2
    am=np.argmax(values_diff2[half:]>threshold)+half
    if am == 0:
        am = np.argmax(values_diff2)

    values_threshold = values_norm[am]

    r = 1
    for item in sorted(vdata, key=lambda x: x['score'], reverse=True):
        s = item['score']/max_d
        item['score'] = s
        item['rank'] = r
        r += 1
        item['class'] = 0
        if s >= values_threshold:
            item['class'] = 1

        # videoname,shotname,[binary classification decision: 1(interesting) or 0(not interesting)],[interestingness level],[shot rank in video]
    for item in sorted(vdata, key=lambda x: int(x['name'].split('_')[0])):
        print('video_{}'.format(video_num), 
              item['name'], 
              item['class'],
              item['score'], 
              item['rank'], sep=',')
