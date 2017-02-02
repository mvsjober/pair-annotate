#!/usr/bin/env python3

from annotate.models import Video, Shot, ShotPair
from annotate.pmatrix import PMatrix

from django.core.management.base import BaseCommand
from django.utils import timezone

import datetime
import logging
import os
import os.path
import numpy as np
import sys

#------------------------------------------------------------------------------

OUTPUT_PATH = 'data'

# How long a pair is reserved for an annotator, in seconds
ANNOTATION_EXPIRE = 60    # = 30 minutes

LOG = logging.getLogger(__name__)

#------------------------------------------------------------------------------

class Command(BaseCommand):
    args = ''
    help = 'Process shot pairs (unreserve abandoned pairs etc)'

    def make_filename(self, video, prefix):
        return '{}/{}-{}-round{}.txt'.format(OUTPUT_PATH, prefix,
                                             video.number, 
                                             video.annotation_rounds)

    def _process_pairs(self):
        now = timezone.now()
        delta = datetime.timedelta(0, ANNOTATION_EXPIRE)

        # Set up dictionaries for counting the number of unannotated
        # pairs, and total number of pairs for each video
        unannotated_counts = {}
        total_counts = {}
        for video in Video.objects.all():
            unannotated_counts[video.id] = 0
            total_counts[video.id] = 0

        # Check all pairs ...
        for pair in ShotPair.objects.all():
            status = pair.status

            # completely ignore videos which are in calculating mode
            if pair.video.status == Video.CALCULATING:
                continue

            # Keep count of total number of pairs for video
            total_counts[pair.video.id] += 1

            # Keep count of number of unannotated pairs for each video
            if status in (ShotPair.UNANNOTATED, ShotPair.RESERVED):
                unannotated_counts[pair.video.id] += 1

            # Release reserved pairs if enough time has passed since
            # annotation started
            if status == ShotPair.RESERVED:
                if now - pair.annotation_started > delta:
                    LOG.info('UNRESERVING: %s, %s', pair, 
                             pair.annotation_started)
                    pair.status = ShotPair.UNANNOTATED
                    pair.save()
                else:
                    LOG.info('KEEPING RESERVATION: %s', pair)

        for video_id, count in sorted(unannotated_counts.items()):
            video = Video.objects.get(id=video_id)

            m_filename = self.make_filename(video, 'm')
            pold_filename = self.make_filename(video, 'p_old')

            # For each video which has all its pairs annotated and we
            # aren't already calculating
            if count == 0 and video.status != Video.CALCULATING:
                LOG.info('VIDEO %d: READY FOR BTL CALC (round %d)', 
                         video.number, video.annotation_rounds)

                # Generate the M matrix (comparison matrix) and save
                # it to file for offline BTL calculation
                m = self._generate_comparison_matrix(video)

                np.savetxt(m_filename, m, fmt='%d')
                LOG.info('* generated ' + m_filename)

                old_ps = video.get_p_values()
                if old_ps is not None:
                    np.savetxt(pold_filename, old_ps, fmt='%f')
                    LOG.info('* generated ' + pold_filename)

                # FIXME just for debugging
                video.status = Video.CALCULATING
                video.save()
            else: # Otherwise, just log current status
                if video.status == Video.ANNOTATING:
                    tot = total_counts[video_id]
                    done = 100.0*((tot-count)/tot)
                    LOG.info("VIDEO %d: annotating %.2f%% done " + 
                             "(%d pairs left, round %d)", 
                             video.number, done, count, video.annotation_rounds)
                elif video.status == Video.CALCULATING:
                    LOG.info("VIDEO %d: calculating BTL (round %d)", 
                             video.number, video.annotation_rounds)
                    assert os.path.isfile(m_filename), \
                        'Video {} calculating but no m-*.txt file found!'.format(
                            video.number)

                    pnew_filename = self.make_filename(video, 'p_new')
                    if os.path.isfile(pnew_filename):
                        LOG.info("* found BTL output file %s", pnew_filename)
                        p = np.loadtxt(pnew_filename)
                        
                        # Remove the pairs from the database
                        remove_count = ShotPair.objects.filter(video=video).delete()
                        LOG.info("* removed %d old shot pairs", remove_count[0])
                        
                        # Generate new pairs based on the p values
                        (t, s) = self.get_ts(video)

                        # Get all shots for video
                        shots = Shot.objects.filter(video=video)

                        # Generate ids
                        ids = [x.id for x in shots]

                        # Spiral matrix
                        pm = PMatrix(s)
                        pm.init_spiral(p, ids)

                        # Generate pairs from spiral matrix
                        pairs = pm.generate_pairs()
                        
                        assert(len(pairs) == t*(s-1))

                        # Save pairs to the database
                        for pair in pairs:
                            shot_1 = shots.get(id=pair[0])
                            shot_2 = shots.get(id=pair[1])
                            shot_pair = ShotPair(video=video,
                                                 shot_1=shot_1, shot_2=shot_2,
                                                 status=ShotPair.UNANNOTATED)
                            shot_pair.save()
                        LOG.info('* generated %d new shot pairs', len(pairs))

                        # Update status of video object
                        video.annotation_rounds += 1
                        video.set_p_values(p)
                        video.status = Video.ANNOTATING
                        video.save()

                        os.remove(m_filename)
                        LOG.info('* removed %s', m_filename)
                        if os.path.isfile(pold_filename):
                            os.remove(pold_filename)
                            LOG.info('* removed %s', pold_filename)
                        
                        os.remove(pnew_filename)
                        LOG.info('* removed %s', pnew_filename)
 
    def get_ts(self, video):
        t = Shot.objects.filter(video=video).count()

        # Sanity check
        s = np.sqrt(t)
        assert s.is_integer()
        s = int(s)

        return (t, s)
        
    def _generate_comparison_matrix(self, video):
        (t, s) = self.get_ts(video)

        pairs = ShotPair.objects.filter(video=video)

        m = np.zeros((t,t), dtype=np.int)

        for pair in pairs:
            status = pair.status

            i1 = pair.shot_1.number
            i2 = pair.shot_2.number

            if status == ShotPair.SHOT_1_SELECTED:
                m[i1, i2] = 1
            elif status == ShotPair.SHOT_2_SELECTED:
                m[i2, i1] = 1
            else:
                assert False

        return m

    def handle(self, *args, **options):
        self._process_pairs()
