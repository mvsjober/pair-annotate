#!/usr/bin/env python3

#------------------------------------------------------------------------------
#  Copyright (c) 2017 University of Helsinki
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public
# License along with this program. If not, see
# <http://www.gnu.org/licenses/>.
# ------------------------------------------------------------------------------

from django.conf import settings
from django.core.management.base import BaseCommand
from annotate.models import Video, Shot, ShotPair
from annotate.pmatrix import PMatrix

import glob
import os
import numpy as np

class Command(BaseCommand):
    args = ''
    help = 'Add videos, including shots, and initial random pair comparisons'

    def _add_video(self, video_num, fullpath, image_subpath='midframe'):
        video_path = settings.VIDEO_PATH

        links_path = os.path.join(video_path, 'links') 
        if not os.path.isdir(links_path):
            os.mkdir(links_path)

        linkname = "video_{}".format(video_num)
        link_path = os.path.join(links_path, linkname)

        if os.path.islink(link_path):
          os.remove(link_path)
        os.symlink(fullpath, link_path)

        filename = os.path.basename(fullpath)

        # Create video
        video = Video(filename=linkname, number=video_num)
        video.save()
        print('Created video row for "{}" -> "{}" with id {}'.
              format(linkname, filename, video.id))

        video_num += 1

        # Compile a dictionary of shots keyed by their starting frame
        shots = {}
        shot_path = os.path.join(fullpath, 'movies')
        for shot_filename in os.listdir(shot_path):
            start_frame = int(shot_filename.split('-')[0])
            assert(start_frame not in shots)
            shots[start_frame] = shot_filename

        ns = len(shots)
        s = int(np.sqrt(ns))
        # s = 3

        t = s*s
        diff = ns-t
        if diff != 0:
            print('Truncating number of shots: {} - {} = {} = {}².'.format(ns, diff, t, s))
        else:
            print('No truncation needed, since {} = {}².'.format(ns, s))

        shot_num = 0
        print('Creating rows for shots:', end=' ')
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

            globglob = os.path.join(link_path, 'images', image_subpath, '*' + 
                                   os.path.splitext(shot_filename)[0] + '.jpg')
            image_path = glob.glob(globglob)
            if len(image_path) != 1:
                print('WARNING!!! Image not found for: ' + linkname + ' ' + 
                      shot_filename)
                print('Used glob:', globglob)
                image_filename = ''
                return
            else:
                image_filename = os.path.basename(image_path[0])

            shot = Shot(video=video, filename=shot_filename,
                        image_filename=image_filename,
                        number=shot_num)
            shot.save()
            print('.', end='', flush=True)
            shot_num += 1


    def _create_videos_and_shots(self):
        video_path = settings.VIDEO_PATH
        print('Generating videos and shots from', video_path)

        video_num = 0

        # Find all videos by listing the directories in video_path
        for filename in os.listdir(video_path):
            fullpath = os.path.join(video_path, filename)

            # Skip non-directories and 'cache'
            if not os.path.isdir(fullpath) or filename in ('cache', 'links'):
                continue

#            if video_num not in range(0,26):
#            if video_num not in range(26,52):
#            if video_num not in range(52,78):
#            if video_num not in range(78,104):
            if video_num not in range(104,108):
                print("Skipping", video_num, "...")
                video_num += 1
                continue

            self._add_video(video_num, fullpath)

            print()

    def _create_videos_and_shots_from_list(self):
        videos_to_add = [
            (104, 'Decay_extract_25fps'),
            (105, 'Fitz_extract_25fps'),
            (106, 'ToS-4K-1920_25fps'),
            (107, 'Valkaama_extract')
        ]

        video_path = settings.VIDEO_PATH
        print('Generating videos and shots from list', videos_to_add)

        for video_num, filename in videos_to_add:
            fullpath = os.path.join(video_path, filename)
            self._add_video(video_num, fullpath, '')

            print()
            
    def _create_initial_random_pairs(self):
        # For each video ...
        for video in Video.objects.all():
            if video.number not in range(104,108):
                continue

            print('Generating random comparison pairs for video "{}"'.format(video.filename), end=' ')

            # Fetch the shots for this video
            shots = Shot.objects.filter(video=video)

            # t=s^2, where s = number of stimuli = number of shots
            num_shots = shots.count()
            s = np.sqrt(num_shots)

            # FIXME some fill-out strategy to reach t'=s^2
            if not s.is_integer():
                print("error sqrt(num_shots)={} not integer".format(s))
                return

            # Collect shot ids into list
            s = int(s)
            ids = [s.id for s in shots]

            # Distribute the ids randomly into the square design matrix P
            pm = PMatrix(s)
            pm.init_randomly(ids)
            
            # Generate comparison pairs (along rows, columns)
            pairs = pm.generate_pairs()

            assert(len(pairs) == num_shots*(s-1))
            
            # Save pairs as ShotPair objects into database
            for p in pairs:
                shot_1 = shots.get(id=p[0])
                shot_2 = shots.get(id=p[1])
                shot_pair = ShotPair(video=video, shot_1=shot_1, shot_2=shot_2,
                                     status=ShotPair.UNANNOTATED)
                shot_pair.save()
                print('.', end='', flush=True)
            print()

    def handle(self, *args, **options):
        #self._create_videos_and_shots()
        self._create_videos_and_shots_from_list()
        self._create_initial_random_pairs()
