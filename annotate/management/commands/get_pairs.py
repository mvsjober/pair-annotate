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

from django.core.management.base import BaseCommand
from annotate.models import LogAnnotation, LogRanking, Video

import os
import sys

class Command(BaseCommand):
    args = ''
    help = 'Get pairs'

    def _get_pairs(self):
        logs = LogAnnotation.objects.filter(video__number__gte=0, video__number__lte=77)
        for l in logs:
            print(l.video.filename, l.shot_1.number, l.shot_1.filename, l.shot_2.number, l.shot_2.filename, l.vote, l.annotation_round, l.cheat)

    def _store_rankings(self, output_dir):
        rankings = LogRanking.objects.filter(video__number__gte=0, video__number__lte=77)
        for l in rankings:
            fname = os.path.join(output_dir, "p_old-" + l.video.filename + ".txt")
            fp = open(fname, 'w')
            print(' '.join(l.p_values.split(',')), file=fp)
            fp.close()
            print("Wrote", fname, file=sys.stderr)

    def _store_pvalues(self, output_dir):
        videos = Video.objects.filter(number__gte=0, number__lte=77)
        for v in videos:
            fname = os.path.join(output_dir, "p_old-" + v.filename + ".txt")
            fp = open(fname, 'w')
            print(' '.join(v.p_values.split(',')), file=fp)
            fp.close()
            print("Wrote", fname, file=sys.stderr)

    def add_arguments(self, parser):
        parser.add_argument('--store_rankings', help="Output dir for storing rankings as p_old files. Default=don't store rankings.")
        parser.add_argument('--store_pvalues', help="Output dir for storing rankings as p_old files. Default=don't store rankings.")
            
    def handle(self, *args, **options):
        if options['store_rankings']:
            self._store_rankings(options['store_rankings'])
        elif options['store_pvalues']:
            self._store_pvalues(options['store_pvalues'])
        else:
            self._get_pairs()
