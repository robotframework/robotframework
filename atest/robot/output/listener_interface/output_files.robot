*** Settings ***
Documentation   Testing that listener gets information about different output files. Tests also that the listener can be taken into use with path.
Suite Setup     Run Some Tests
Suite Teardown  Remove Listener Files
Force Tags      regression
Default Tags    pybot  jybot
Resource        listener_resource.robot

*** Variables ***
${LISTENERS}  ${CURDIR}${/}..${/}..${/}..${/}testresources${/}listeners

*** Test Cases ***
Output Files
    ${file} =  Get Listener File  ${ALL_FILE}
    ${exp} =  Catenate  SEPARATOR=\n  Debug: mydeb.txt  Output: myout.xml  Log: mylog.html  Report: myrep.html
    ...  Closing...\n
    Should End With  ${file}  ${exp}

Output Files With Java
    [Tags]  jybot
    ${file} =  Get Listener File  ${JAVA_FILE}
    ${exp} =  Catenate  SEPARATOR=\n  Debug (java): mydeb.txt  Output (java): myout.xml  Log (java): mylog.html  Report (java): myrep.html  The End\n
    Should End With  ${file}  ${exp}

*** Keywords ***
Run Some Tests
    Run Tests Without Processing Output  --listener "${LISTENERS}${/}ListenAll.py" --listener "${LISTENERS}${/}JavaListener.java" --log mylog.html --report myrep.html --output myout.xml --debugfile mydeb.txt  misc${/}pass_and_fail.robot
    Process Output  ${OUTDIR}${/}myout.xml
    Should Be Equal  ${SUITE.name}  Pass And Fail

