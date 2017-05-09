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
from annotate.models import Shot

import numpy as np
import sys

class Command(BaseCommand):
    args = ''
    help = 'Generate rankings html'

    def handle(self, *args, **options):
        modality = settings.MEDIAEVAL_MODALITY
        for vid in range(77):
            fname = "scripts/output-{}-fixed/p_new-video_{}.txt".format(modality, vid)
            p = np.loadtxt(fname)

            outname = "rankings-html/{}/video_{}_fixed.html".format(modality, vid)
            fp = open(outname, 'w')
            
            print("<table>", file=fp)
            print("<tr>", file=fp)
            i=1
            for sid in np.argsort(-p):
                shots = Shot.objects.filter(video__number=vid, number=sid)
                assert(len(shots)==1)
                shot = shots[0]
                fname = "https://annotate.hiit.fi/static/annotate/videos/links/{}/images/midframe/{}".format(shot.video.filename, shot.image_filename)
                #print(sid, p[sid], fname)

                print('<td><img width=300 src="{}" />'.format(fname), file=fp)
                print('<br />{}</td>'.format(p[sid]), file=fp)

                if i % 5 == 0:
                    print('</tr><tr>', file=fp)
                i += 1

            print("</tr>", file=fp)
            print("</table>", file=fp)
            fp.close()
            print("Wrote", outname, file=sys.stderr)
                
