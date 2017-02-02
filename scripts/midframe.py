#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
from __future__ import division

import os
import os.path
import cv2
import sys

fname = sys.argv[1]
vc = cv2.VideoCapture(fname)

n = -1
rval = True

if not vc.isOpened():
    print("Unable to open", fname, file=sys.stderr)

while rval:
    rval, frame = vc.read()
    n += 1

midframe = n//2

vc.release()

print('{} has {} frames, midframe = {}'.format(fname, n, midframe))

vc = cv2.VideoCapture(fname)

frame = None
for i in range(midframe):
     rval, frame = vc.read()

base_path = os.path.split(os.path.dirname(fname))[0]
name_base = os.path.splitext(os.path.basename(fname))[0]
f1, f2 = [int(x) for x in name_base.split('-')]

assert f2-f1+1 == n

image_fname = str(f1+i) + ' (' + name_base + ').jpg'

out_fname = os.path.join(base_path, 'images', 'midframe', image_fname)

if os.path.isfile(out_fname):
    print("WARNING: file exists:", out_fname, file=sys.stderr)
else:
    cv2.imwrite(out_fname,frame)
    print('Wrote', out_fname, '...')

vc.release()
