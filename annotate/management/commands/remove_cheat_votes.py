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
#------------------------------------------------------------------------------

from django.core.management.base import BaseCommand
from annotate.models import Annotator, LogAnnotation, ShotPair, Video

import math

class Command(BaseCommand):
    args = ''
    help = 'Remove cheated votes'

    def _remove_cheats(self):
        sum_to_remove = 0
        for annotator in Annotator.objects.all():
            name = annotator.user.username
            # logs = LogAnnotation.objects.filter(annotator=annotator, annotation_round=7,
            #                                     video__number__gte=0, 
            #                                     video__number__lte=77).order_by('-when')

            logs = LogAnnotation.objects.filter(annotator=annotator, annotation_round=3,
                                                video__number__gte=78, 
                                                video__number__lte=103).order_by('-when')
            
            current_logs = []
            current_same = 1
            prev_vote = -1
            prev_time = None
            for log in logs:
                vote = log.vote
                cur_time = log.when
                if prev_time is not None: 
                    time_diff = -(cur_time-prev_time).total_seconds()
                else:
                    time_diff = 1000
                    
                if vote == prev_vote and time_diff < 600:
                    current_same += 1
                    current_logs.append(log)
                else:
                    if current_same > 20:
                        print(name, len(current_logs))
                        sum_to_remove += current_same-1

                        annotator.annotation_count -= len(current_logs)
                        annotator.save()

                        for rlog in current_logs:
                            rlog.cheat = True
                            rlog.save()
                            
                            shot_pair = ShotPair(video=rlog.video,
                                                 shot_1=rlog.shot_1, shot_2=rlog.shot_2,
                                                 status=ShotPair.UNANNOTATED)
                            shot_pair.save()

                            if rlog.video.status == Video.CALCULATING:
                                rlog.video.status = Video.ANNOTATING
                                rlog.video.save()
                                print("Reset video {} state: CALCULATING => ANNOTATING.".format(rlog.video.number))

                    current_logs.clear()
                    current_same = 1

                prev_vote = vote
                prev_time = cur_time

        print(sum_to_remove)

            
    def handle(self, *args, **options):
        self._remove_cheats()
