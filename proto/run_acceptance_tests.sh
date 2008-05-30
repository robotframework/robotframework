#!/bin/bash

OUTPUTDIR=/opt/cruisecontrol/logs/robot-core
BACKUPDIR=$OUTPUTDIR/old/$(date +%Y%m%d-%H%M%S)
OUT=$OUTPUTDIR/output.txt

cd /opt/cruisecontrol/projects/robot-core
rm -rf atest/results

echo 'Running Robot Acceptance Tests' >$OUT
echo -n 'Date: ' >>$OUT
date -R >>$OUT
echo >>$OUT

echo '1) svn update' >>$OUT
svn update 1>>$OUT 2>>$OUT
date -R >>$OUT
echo >>$OUT

echo '2) uninstall & cleanup' >>$OUT
rm -frv \
    /usr/local/bin/?ybot \
    /usr/local/bin/?ydoc \
    /usr/local/bin/rebot \
    /usr/local/lib/python2.4/site-packages/robot \
    build \
    1>>$OUT 2>>$OUT
bash cleanup.sh >>$OUT
date -R >>$OUT
echo >>$OUT

echo '3) install' >>$OUT
python setup.py install 1>>$OUT 2>>$OUT
date -R >>$OUT
echo >>$OUT


# parameters for test execution
params="--outputdir $OUTPUTDIR --monitorcolors off"
data="atest/robot/"
pyinterpreter=/usr/local/bin/python2.4
jyinterpreter=/usr/jython/jython-2.2b2/jython
runner=/usr/local/lib/python2.4/site-packages/robot/runner.py

echo '4) execute python tests' >>$OUT
version=$($pyinterpreter $runner --version \
    | sed "s/ /SP/g" |  sed "s/(/PAR1/g" |  sed "s/)/PAR2/g")
python atest/run_atests.py $pyinterpreter \
    --name Python_Tests \
    --metadata Robot_Version:$version \
    $params $data 1>>$OUT 2>>$OUT
date -R >>$OUT
echo >>$OUT

echo '5) execute jython tests' >>$OUT
version=$($jyinterpreter $runner --version \
    | sed "s/ /SP/g" |  sed "s/(/PAR1/g" |  sed "s/)/PAR2/g")
python atest/run_atests.py $jyinterpreter \
    --name Jython_Tests \
    --metadata Robot_Version:$version \
    $params $data 1>>$OUT 2>>$OUT
date -R >>$OUT
echo >>$OUT

echo '6) combine reports' >> $OUT
rebot --name Robot_Acceptance_Tests \
  --metadata Full_Report:http://gaston.ntc.nokia.com:8000/artifacts/robot-core/report.html \
  --outputdir $OUTPUTDIR \
  --summary summary.html \
  --report report.html  \
  --log none \
  --SuiteStatLevel 3 \
  --TagStatCombine jybotNOTpybot \
  --TagStatCombine pybotNOTjybot \
  --TagStatExclude pybot \
  --TagStatExclude jybot \
  --TagStatLink jython-bug-*:http://jython.org/bugs/%1:Tracker \
  $OUTPUTDIR/?ybot-output.xml 1>>$OUT 2>>$OUT
rc=$?
date -R >>$OUT
echo >>$OUT

echo '7) remove over month old backups' >>$OUT
curtime=$(date +%s)  
month=$((60 * 60 * 24 * 30))
for dir in $OUTPUTDIR/old/2*;  do 
    dirtime=$(date -r $dir +%s)  
    if (( curtime - dirtime > month )); then 
        rm -rf $dir 1>>$OUT 2>>$OUT
        echo "removed $dir" >>$OUT
    else
        echo "kept $dir" >>$OUT
    fi
done
date -R >>$OUT
echo >>$OUT

echo '8) backup' >>$OUT
mkdir -pv $BACKUPDIR 1>>$OUT 2>>$OUT
for item in pybot-output.xml pybot-report.html pybot-log*.html \
            jybot-output.xml jybot-report.html jybot-log*.html \
            report.html summary.html; do
    cp -rv $OUTPUTDIR/$item $BACKUPDIR 1>>$OUT 2>>$OUT
done
cp $OUT $BACKUPDIR
date -R >>$OUT
echo >>$OUT

echo '9) done' >>$OUT
date -R >>$OUT
echo >>$OUT

exit $rc
