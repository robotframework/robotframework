#!/bin/bash

INDIR=testdata
OUTDIR=testoutput

echo "0) Cleanup"
rm -rf $OUTDIR
mkdir $OUTDIR
cp $INDIR/*.* $OUTDIR

echo "1) Tidying"
python robotidy.py $OUTDIR/orig.html $OUTDIR/cleaned.html
python robotidy.py $OUTDIR/orig.html $OUTDIR/cleaned.tsv
python robotidy.py --fixcomments --title My_Cool_Title \
    $OUTDIR/orig.html $OUTDIR/fixed.html
python robotidy.py --format tsv -X $OUTDIR/orig.html $OUTDIR/fixed.whatever
mv $OUTDIR/fixed.whatever $OUTDIR/fixed.tsv

echo
echo "2) Tidying in place"
cp $OUTDIR/cleaned.html $OUTDIR/inplace.html
cp $OUTDIR/cleaned.tsv $OUTDIR/inplace.tsv
python robotidy.py --fixcomment --inplace --style NONE $OUTDIR/inplace.*

echo
echo "3) Running tests"
for data in $OUTDIR/*.*; do
    echo
    echo $data
    pybot --name test --output $data.xml --log none --report none $data \
        2> /dev/null
done

echo
echo "4) Checking statuses"
for output in $OUTDIR/*.xml; do
  python ../statuschecker/statuschecker.py $output
done

echo
echo "5) Diffing results"
python ../robotdiff/robotdiff.py --report $OUTDIR/tidyresult.html $OUTDIR/*.xml
