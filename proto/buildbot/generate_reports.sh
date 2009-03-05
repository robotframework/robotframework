#!/bin/bash
cd $1
rm *.xml *html
unzip outputs.zip
command="rebot --name Robot_Framework_Acceptance_Tests --splitoutputs 1 output.xml"
echo "Executing command: " $command
$command
exit $?

