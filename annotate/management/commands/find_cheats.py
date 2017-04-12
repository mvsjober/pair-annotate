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
from annotate.models import Annotator, LogAnnotation

import math

class Command(BaseCommand):
    args = ''
    help = 'Find cheating annotators'

    def _find_cheats(self):
        for annotator in Annotator.objects.all():
            name = annotator.user.username
            logs = LogAnnotation.objects.filter(annotator=annotator, annotation_round=6).order_by('-when')
            vc = [0, 0]
            for log in logs:
                vote = log.vote
                assert(vote == 1 or vote == 2)
                vc[vote-1] += 1
            sum = vc[0] + vc[1]
            if sum < 20:
                continue

            pdiff = math.fabs((vc[0] / sum)-0.5)

            number_of_long_strings = 0
            longest_same = 1
            current_same = 1
            prev_vote = -1
            for log in logs:
                vote = log.vote
                #print(name, vote)
                if vote == prev_vote:
                    current_same += 1
                else:
                    if current_same > longest_same:
                        longest_same = current_same
                    if current_same >= 20:
                        number_of_long_strings += 1
                    current_same = 1
                prev_vote = vote
                
            if current_same > longest_same:
                longest_same = current_same
            if current_same >= 20:
                number_of_long_strings += 1

            if pdiff > 0.2 or longest_same >= 20:
                print(name, sum, pdiff, longest_same, number_of_long_strings)
            
    def handle(self, *args, **options):
        self._find_cheats()
