#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
from __future__ import division

import MySQLdb
import datetime

sys.path.append("../core")
from settings_local import DATABASES

#------------------------------------------------------------------------------

db_name = 'annotate_video'
round = 5
filename_field = 'filename'

# db_name = 'annotate_image'
# round = 5
# filename_field = 'image_filename'

#------------------------------------------------------------------------------

# connect
db = MySQLdb.connect(host=db_info['HOST'], user=db_info['USER'], passwd=db_info['PASSWORD'], db=db_name)

cursor = db.cursor()

# execute SQL select statement
cursor.execute("select id,filename,p_values from annotate_video where annotation_rounds=%d" % round)

# commit your changes
db.commit()

# get the number of rows in the resultset
numrows = int(cursor.rowcount)

# get and display one row at a time.
for x in range(0,numrows):
    row = cursor.fetchone()
    video_id = row[0]
    video_name = row[1]
    p_values = [float(x) for x in row[2].split(',')]


    cursor2 = db.cursor()
    cursor2.execute("select %s from annotate_shot where video_id=%d" % (filename_field, video_id))

    db.commit()

    rowcount2 = cursor2.rowcount
    assert(rowcount2 == len(p_values))

    for i in range(0, rowcount2):
        row2 = cursor2.fetchone()
        shot_name = row2[0]
        print(video_name, shot_name, p_values[i], sep=',')
