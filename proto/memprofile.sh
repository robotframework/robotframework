#!/bin/bash
python ../src/robot/rebot.py $1 &
rebotpid=$!
echo $rebotpid
while ps -ef | grep $rebotpid; do
	top -b -p $rebotpid -n 1
	sleep 1
done

