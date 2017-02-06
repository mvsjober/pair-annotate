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

# from django.conf import settings
from django.core.management.base import BaseCommand
from annotate.models import Video, LogRanking
# from annotate.pmatrix import PMatrix
from django.utils import timezone

# import glob
# import os
# import numpy as np

class Command(BaseCommand):
    args = ''
    help = 'Initialise ranking log'

    def handle(self, *args, **options):
        for video in Video.objects.all():
            head = "Video {}, round {}:".format(video.number, video.annotation_rounds)
            
            log = LogRanking.objects.filter(video=video,
                                            annotation_round=video.annotation_rounds)
            if len(log) > 1:
                print(head, "ERROR! There should only be one matching ranking log item!")
                return

            if len(log) == 1:
                print(head, "already has a ranking logged.")
            elif video.p_values == "":
                print(head, "has no annotation ranking yet. (p_values is empty)")
            else:
                r = LogRanking(video=video, annotation_round=video.annotation_rounds, when=timezone.now(),
                               p_values=video.p_values)
                r.save()
                print(head, "logged ranking in the database.")
                
