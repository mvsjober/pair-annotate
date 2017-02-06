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
    help = 'Clean database (remove videos, shots, pair comparisons)'

    def handle(self, *args, **options):
        print('Deleting videos and shots ...')
        Video.objects.all().delete()
        Shot.objects.all().delete()

        print('Deleting shot pairs ...')
        ShotPair.objects.all().delete()
