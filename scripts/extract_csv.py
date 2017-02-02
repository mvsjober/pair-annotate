#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
from __future__ import division

import MySQLdb
import datetime
import sys
import os

sys.path.append("../core")
from settings_local import DATABASES

#------------------------------------------------------------------------------

output_dir = 'csv'
separator = ','

#------------------------------------------------------------------------------

def print_description(cursor, table, columns, file):
    cursor.execute("describe " + table)
    db.commit()

    names = []
    row = cursor.fetchone()
    while row is not None:
        name = row[0]
        if columns is None or name in columns:
            names.append(name)
        row = cursor.fetchone()
        
    print(separator.join(names), file=file)

#------------------------------------------------------------------------------

def print_rows(cursor, table, columns, file):
    cols = '*'
    if columns is not None:
        cols = ','.join(columns)

    cursor.execute("select %s from %s" % (cols, table))
    db.commit()

    row = cursor.fetchone()
    while row is not None:
        sep = separator
        rl = len(row)
        for i, item in enumerate(row):
            if i == rl-1:
                sep='\n'
            if isinstance(item, str) and separator in item:
                item = '"' + item + '"'
            print(item, end=sep, file=file)

        row = cursor.fetchone()

#------------------------------------------------------------------------------

tables = ['annotate_annotator',
          'annotate_shot',
          'annotate_shotpair',
          'annotate_video',
          'auth_user',
          'social_auth_usersocialauth']

columns = { 
    'auth_user': ['id', 'last_login', 'username', 'date_joined'],
    'social_auth_usersocialauth': ['id', 'provider', 'uid', 'user_id']
}

db_info = DATABASES['default']

for dbname in ('video', 'image'):
    db = MySQLdb.connect(host=db_info['HOST'], user=db_info['USER'], passwd=db_info['PASSWORD'],
                         db='annotate_'+dbname)
    cursor = db.cursor()

    path = output_dir + '/' + dbname
    if not os.path.exists(path):
        os.mkdir(path)

    for table in tables:
        filename = path + '/' + table + '.csv'
        fp=open(filename, 'w')

        cols = columns.get(table)
        print_description(cursor, table, cols, file=fp)
        print_rows(cursor, table, cols, file=fp)

        fp.close()
        print('Wrote '+filename, file=sys.stderr)



