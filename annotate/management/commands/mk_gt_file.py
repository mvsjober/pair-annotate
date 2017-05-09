#!/usr/bin/env python3

#------------------------------------------------------------------------------

from django.conf import settings
from django.core.management.base import BaseCommand
from annotate.models import Shot

import glob
import numpy as np
import os
import re
import sys

threshold = 0.01

#------------------------------------------------------------------------------

class Command(BaseCommand):
    args = ''
    help = 'Make groundtruth file from p_new files'

    def _mk_gt(self):
        modality = settings.MEDIAEVAL_MODALITY

        # Read input files as e.g. output-image-fixed/p_new-video_*.txt 
        #     0.09863332 0.1353585 0.1486468 ...
        # and put into data dictionary, e.g.:
        #     data[0] => [list of data dict-objects for video_0]

        data = {}

        # here read files instead
        input_dir = 'scripts/output-{}-fixed'.format(modality)

        pvid = re.compile(r'^.*-video_(\d+).txt$')

        for fname in glob.glob(os.path.join(input_dir, "p_new-video_*.txt")):
            m = pvid.match(fname)
            video_num = int(m.group(1))
            print("Reading", fname, "...", end=' ', file=sys.stderr)

            p = np.loadtxt(fname)
            assert(p.shape[0] > 1 and len(p.shape) == 1)

            for i in range(len(p)):
                matching_shots = Shot.objects.filter(video__number=video_num, number=i)
                assert(len(matching_shots) == 1)
                shot = matching_shots[0]

                if modality == 'video':
                    target_fname = shot.filename
                else:
                    target_fname = shot.image_filename
                    # for image names we have to edit it a bit ...
                    target_fname = target_fname.replace(' ', '_').replace('(', '').replace(')', '')

                if video_num not in data:
                    data[video_num] = []

                data[video_num].append({'name': target_fname, 
                                        'score': float(p[i])})

            print("[{} shots]".format(len(p)), file=sys.stderr)

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
            split_char = '_' if modality == 'image' else '-'
            for item in sorted(vdata, key=lambda x: int(x['name'].split('_')[0])):
                print('video_{}'.format(video_num), 
                      item['name'], 
                      item['class'],
                      item['score'], 
                      item['rank'], sep=',')


    def handle(self, *args, **options):
        self._mk_gt()
        
