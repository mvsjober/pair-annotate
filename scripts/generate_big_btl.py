#!/usr/bin/env python3

from operator import itemgetter
import re
import numpy as np

#------------------------------------------------------------------------------

pjpg = re.compile(r'^\d+_(\d+-\d+)\.jpg$')
pmp4 = re.compile(r'^(\d+-\d+)\.mp4$')

#------------------------------------------------------------------------------

def ranking_for_video(video, lines, ranking):
    assert(video not in ranking)
    t = len(lines)
    s = int(np.sqrt(t))
    assert(s*s == t)
    
    sorted_lines = sorted(lines, key=lambda x: int(x[0].split('-')[0]))
    #print(video)
    #print(sorted_lines[:10])

    M = np.zeros((t,t), dtype=np.int)
    
    for i in range(t):
        i_rank = sorted_lines[i][1]
        for j in range(i+1, t):
            j_rank = sorted_lines[j][1]
            if i_rank < j_rank:
                M[i, j] += 1
            else:
                M[j, i] += 1

    ranking[video] = M

#------------------------------------------------------------------------------

def load_ranking(fname, ranking, is_video):
    with open(fname, 'r') as fp:
        prev_video = None
        lines = []
        for line in fp:
            # line example: video_0,107_102-113.jpg,0,0.0998011954829,36

            parts = line.strip().split(',')
            video = parts[0]

            if video != prev_video and prev_video is not None:
                # process shots for single video
                ranking_for_video(prev_video, lines, ranking)
                lines.clear()
                #return

            filename = parts[1]
            m = None
            if is_video:
                m = pmp4.match(filename)
            else:
                m = pjpg.match(filename)
            assert(m)

            # tuples with shot name ("102-113") and rank (e.g. 1, 2, ...)
            lines.append((m.group(1), int(parts[4])))
            prev_video = video

        ranking_for_video(prev_video, lines, ranking)

#------------------------------------------------------------------------------

def load_pairs(fname, ranking):
    cheats = {}
    with open(fname, 'r') as fp:
        for line in fp:
            # line example: video_0 41 1683-1708.mp4 16 947-968.mp4 2 6 False
            parts = line.strip().split(' ')
            video = parts[0]
            i1 = int(parts[1])
            i2 = int(parts[3])
            vote = int(parts[5])
            cheat = parts[7]
            if cheat != "False":
                cheats[video] = cheats.get(video, 0) + 1
                continue

            M = ranking[video]
            prev_vote = M[i1][i2]

            if vote == 1:
                M[i1, i2] += 1
            elif vote == 2:
                M[i2, i1] += 1
            else:
                assert False

    print("Skipped cheats:")
    for key, value in sorted(cheats.items()):
        print(key, value)

            
#------------------------------------------------------------------------------

for modality in ["video", "image"]:
    ranking = {}

    load_ranking("devset-2016-{}.txt".format(modality), ranking, modality == "video")
    load_ranking("testset-2016-{}.txt".format(modality), ranking, modality == "video")
    
    # zero out for skipping old ranking pairs
    for video, M in ranking.items():
        ranking[video] = np.zeros(M.shape)
    
    load_pairs("pairs-{}-2017-05-02-fixed.txt".format(modality), ranking)

    for video, M in ranking.items():
        np.savetxt("output-{}-fixed/m-{}.txt".format(modality, video), M, fmt='%2d')
