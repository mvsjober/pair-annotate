#!/usr/bin/env python3

import os
import hashlib
import sys

# From http://joelverhagen.com/blog/2011/02/md5-hash-of-file-in-python/
def md5sum(fname):
    with open(fname, 'rb') as fh:
        m = hashlib.md5()
        while True:
            data = fh.read(8192)
            if not data:
                break
            m.update(data)
        return m.hexdigest()

#------------------------------------------------------------------------------
    
files = [
    ('me17in-devset-1.zip', 'annotations and scripts'),
    ('me17in-devset-2.zip', 'video files: video_0 .. video_25'),
    ('me17in-devset-3.zip', 'video files: video_26 .. video_51'),
    ('me17in-devset-4.zip', 'video files: video_52 .. video_77'),
    ('me17in-devset-5.zip', 'all features except CNN'),
    ('me17in-devset-6.zip', 'CNN features for video_0 .. video_25'),
    ('me17in-devset-7.zip', 'CNN features for video_26 .. video_51'),
    ('me17in-devset-8.zip', 'CNN features for video_52 .. video_77')
]


files_html = ""

for f in files:
    fname = f[0]
    fsize = os.path.getsize(fname)
    funit = "B"
    if fsize > 1024:
        funit = "KiB"
        fsize = fsize/1024
    if fsize > 1024:
        funit = "MiB"
        fsize = fsize/1024

    fmd5 = md5sum(fname)
    print(fname, fmd5, file=sys.stderr)
    
    files_html += """
            <tr>
              <td><tt>{0}</tt></td>
	      <td>{1}</d>
              <td>{2:.2f} {3}</td>
              <td><tt>{4}</tt></td>
              <td><a href="{0}"><button type="button" class="btn btn-default btn-sm">
                    <span class="glyphicon glyphicon-download-alt"></span> Download
		</button></a>
              </td>
            </tr>
    """.format(fname, f[1], fsize, funit, fmd5)

fp=open('index.html', 'w')
print("""
<!DOCTYPE html>
<html lang="en"><head>
    <meta http-equiv="content-type" content="text/html; charset=UTF-8">
    <meta charset="utf-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>MediaEval 2017 Predicting Media Interestingness Task - Download</title>

    <!-- Bootstrap -->
    <link href="css/bootstrap.min.css" rel="stylesheet">

    <!-- HTML5 Shim and Respond.js IE8 support of HTML5 elements and media queries -->
    <!-- WARNING: Respond.js doesn't work if you view the page via file:// -->
    <!--[if lt IE 9]>
      <script src="https://oss.maxcdn.com/libs/html5shiv/3.7.0/html5shiv.js"></script>
      <script src="https://oss.maxcdn.com/libs/respond.js/1.4.2/respond.min.js"></script>
    <![endif]-->
  </head>
  <body>
    <div class="container">
      <h1>MediaEval 2017 Predicting Media Interestingness Task</h1>

      <div class="alert alert-success" role="alert">The development data set is split into several ZIP files which can be downloaded from the links below.</div>
      <!-- <div class="alert alert-success" role="alert">The development and testing data sets are each split into several ZIP files which can be downloaded from the links below.</div> -->

      <p>File size is indicated below
        in <a href="https://en.wikipedia.org/wiki/Mebibyte">MiB</a>
        or <a href="https://en.wikipedia.org/wiki/Kibibyte">KiB</a>.
        Please also confirm
        the <a href="https://en.wikipedia.org/wiki/Md5sum">MD5
        checksum</a> after download to ensure that the file has been
        correctly retrieved.</p>
      
      <hr />

      <h2>Development set</h2>
      <div class="panel panel-default">
	<div class="panel-heading">
          <h2 class="panel-title">Download</h2>
	</div>
	<div class="panel-body">
	  <table class="table table-hover">
            <thead>
              <th>Filename</th>
              <th>Contents</th>
              <th>Size</th>
              <th>MD5 checksum</th>
              <th>&nbsp;</th>
	    </thead>

            {}

	  </table>
	</div>
      </div>

      <!-- <hr /> -->

      <!-- <h2>Testing set</h2> -->
      <!-- <div class="panel panel-default"> -->
      <!--   <div class="panel-heading"> -->
      <!--     <h2 class="panel-title">Download</h2> -->
      <!--   </div> -->
      <!--   <div class="panel-body"> -->
      <!--     <table class="table table-hover"> -->
      <!--       <thead> -->
      <!--         <th>Filename</th> -->
      <!--         <th>Contents</th> -->
      <!--         <th>Size</th> -->
      <!--         <th>MD5 checksum</th> -->
      <!--         <th>&nbsp;</th> -->
      <!--       </thead> -->

      <!--       <\!--#include file="devset-files.html" -\->  -->
      <!--     </table> -->
      <!--   </div> -->
      <!-- </div> -->
    </div>
</div>

<!-- jQuery (necessary for Bootstrap's JavaScript plugins) -->
<script src="js/jquery.min.js"></script>
<!-- Include all compiled plugins (below), or include individual files as needed -->
<script src="js/bootstrap.min.js"></script>

</body>
</html>
""".format(files_html),
      file=fp)
fp.close()
