#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  Copyright (c) 2016 University of Helsinki
#
#  Permission is hereby granted, free of charge, to any person
#  obtaining a copy of this software and associated documentation files
#  (the "Software"), to deal in the Software without restriction,
#  including without limitation the rights to use, copy, modify, merge,
#  publish, distribute, sublicense, and/or sell copies of the Software,
#  and to permit persons to whom the Software is furnished to do so,
#  subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be
#  included in all copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
#  EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
#  MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
#  NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS
#  BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN
#  ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
#  CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#  SOFTWARE.
#
#------------------------------------------------------------------------------

from __future__ import print_function

import argparse
import re
import sys

#------------------------------------------------------------------------------

def error(msg):
    print('Error: ' + msg)
    sys.exit(1)

#------------------------------------------------------------------------------

def process_file(fname, qrels):
    warn_count = 0

    outfname = fname + '.trec'
    if qrels:
        outfname = fname + '.qrels'
    
    outfp = open(outfname, 'w')
    with open(fname, 'r') as fp:
        for line in fp:
            parts = line.rstrip().split(',')

            if len(parts) != 4 and len(parts) != 5:
                error('Line should have four or five columns: ' + line)

            videoname = parts[0]
            targetname = parts[1]
            decision = int(parts[2])
            value = float(parts[3])

            # check that videoname is in correct format
            if not re.match(r'^video_\d+$', videoname):
                error('Video name not in correct format (e.g. video_42): ' + 
                      videoname)

            # check that targetname matches either format "0-108.mp4"
            # or "57_0-108.jpg"
            if not re.match(r'^\d+-\d+\.mp4$', targetname) and \
               not re.match(r'^\d+_\d+-\d+\.jpg$', targetname):
                error('Frame or shot name doesn\'t match either of the ' +
                      'allowed formats: ' +
                      'shotstartingframe-shotendingframe.mp4 or ' +
                      'frameNb_shotstartingframe-shotendingframe.jpg.')

            # decision value should be either 0 or 1
            if decision != 0 and decision != 1:
                error('Decision value should be 1 or 0: ' + parts[2])

            # Copied from treceval README:
            #
            # Lines of results_file are of the form 
            #      030  Q0  ZF08-175-870  0   4238   prise1 
            #      qid iter   docno      rank  sim   run_id 
            # giving TREC document numbers (a string) retrieved by query qid  
            # (a string) with similarity sim (a float).  The other fields are ignored, 
            # with the exception that the run_id field of the last line is kept and 
            # output.  In particular, note that the rank field is ignored here; 
            # internally ranks are assigned by sorting by the sim field with ties  
            # broken deterministicly (using docno). 
            # Sim is assumed to be higher for the docs to be retrieved first. 
            # File may contain no NULL characters. 
            # Lines may contain fields after the run_id; they are ignored. 
            #
            # Relevance for each docno to qid is determined from text_qrels_file, which 
            # consists of text tuples of the form 
            #    qid  iter  docno  rel 
            # giving TREC document numbers (docno, a string) and their relevance (rel,  
            # a non-negative integer less than 128, or -1 (unjudged)) 
            # to query qid (a string).  iter string field is ignored.   
            # Fields are separated by whitespace, string fields can contain no whitespace. 
            # File may contain no NULL characters. 

            if qrels:
                print('{} 0 {} {}'.format(videoname, targetname, decision), 
                      file=outfp)
            else:
                print('{} 0 {} {} {} {}'.format(videoname, targetname, decision,
                                                value, fname), file=outfp)

    outfp.close()
    print("Wrote " + outfname + ".")

#------------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="""Convert the output format of the MediaEval 2016 
        Predicting Media Interestingness Task into trec_eval format.""")

    parser.add_argument('files', type=str, nargs='+', 
                        help='one or more files to convert')
    parser.add_argument('--qrels', action='store_true',
                        help='create a trec_eval ground truth (qrels) file instead')
    args = parser.parse_args()

    for fname in args.files:
        process_file(fname, args.qrels)

#------------------------------------------------------------------------------

if __name__ == '__main__':
    main()
