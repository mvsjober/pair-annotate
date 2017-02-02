#!/bin/bash

#TRES=y0.5
TRES=0.01

RANKINGS_FILE="image-rankings-subset1and2-combined.txt"
OUTPUTDIR="html/image_rankings"

# RANKINGS_FILE="video-rankings-subset1and2-combined.txt"
# OUTPUTDIR="html/video_rankings"

ALLFNAME="${OUTPUTDIR}/all_curves_${TRES}.html"

mkdir -p $OUTPUTDIR

echo "<p>${TRES}</p>" > $ALLFNAME
for i in {0..51}
do 
    IMGFNAME="video_${i}_${TRES}.html"
    ./mk_rankings_webpage.py video_${i} $RANKINGS_FILE $TRES ${OUTPUTDIR} > ${OUTPUTDIR}/${IMGFNAME} 2> /tmp/foobar
    OUTPUT=$(</tmp/foobar)
    echo "<img src=\"threshold_video_${i}_${TRES}.jpg\"/> <a href=\"${IMGFNAME}\">${OUTPUT}</a><br/>" >> $ALLFNAME
    echo "Wrote ${OUTPUTDIR}/${IMGFNAME} ..."
done
echo "Wrote ${ALLFNAME} ..."
