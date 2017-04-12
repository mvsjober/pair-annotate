#!/usr/bin/env python3

import argparse
import math 
import os
import re
import sys

def main(args):
    p = re.compile(r'^\d+_(\d+-\d+)\.jpg$')
    video_path = args.dir
    
    # Find all videos by listing the directories in video_path
    for filename in os.listdir(video_path):
        fullpath = os.path.join(video_path, filename)

        print('Processing', filename, '...')
        
        image_files = os.listdir(os.path.join(fullpath, 'images'))
        N = len(image_files)

        # sanity check that N=s^2
        s = int(math.sqrt(N))
        t = s*s
        assert(t == N)

        allowed_video = []
        for ifile in image_files:
            m = p.match(ifile)
            assert(m)
            allowed_video.append(m.group(1) + '.mp4')

        movies_path = os.path.join(fullpath, 'movies')
        video_files = os.listdir(movies_path)
        to_delete = []
        for vfile in video_files:
            if vfile not in allowed_video:
                to_delete.append(vfile)

        N_v = len(video_files)
        assert(N_v - len(to_delete) == N)

        for vfile in to_delete:
            vfile_path = os.path.join(movies_path, vfile)
            if args.dryrun:
                print('Here we would remove', vfile_path)
            else:
                print('Removing', vfile_path)
                os.remove(vfile_path)
            
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('dir', type=str)
    parser.add_argument('--dryrun', action='store_true')
    args = parser.parse_args()
    main(args)
    
