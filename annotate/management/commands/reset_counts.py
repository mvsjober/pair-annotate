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
from annotate.models import Annotator

class Command(BaseCommand):
    args = ''
    help = 'Reset annotation counts for all users'

    def _reset_counts(self):
        for annotator in Annotator.objects.all():
            annotator.annotation_count = 0
            print('Setting count for {} = {}'.format(annotator.user.username,
                                                     annotator.annotation_count))
            annotator.save()

    def handle(self, *args, **options):
        self._reset_counts()
