*** Settings ***
Test Teardown     Remove File    ${OUTDIR}/${OUTFILE}
Resource          atest_resource.robot

*** Test Cases ***
File Suite
    Run Tests    --settag cmdlinetag    misc/normal.robot
    Check Test Tags    First One    cmdlinetag    f1    t1    t2
    Check Test Tags    Second One    cmdlinetag    d1    d_2    f1

Directory Suite
    Run Tests    --settag CmdLineTag    misc/suites
    Check Test Tags    Third in Suite 1    CmdLineTag    d1    d2    f1
    Check Test Tags    SubSuite1 First    CmdLineTag    f1    t1
    Check Test Tags    SubSuite2 First    CmdLineTag    f1

Multi-source Suite
    Run Tests    --settag cmdlinetag    misc/normal.robot misc/pass_and_fail.robot
    Check Test Tags    First One    cmdlinetag    f1    t1    t2
    Check Test Tags    Pass    cmdlinetag    force    pass

Use Set Tag Multiple Times
    Run Tests    -G cmdlinetag --settag anothertag --settag 3rdtag    misc/normal.robot
    Check Test Tags    First One    3rdtag    anothertag    cmdlinetag    f1    t1
    ...    t2

Set Tag Set Also In Test Data
    Run Tests    --settag F1    misc/normal.robot
    Check Test Tags    First One    f1    t1    t2

Set Same Tag Multiple Times
    Run Tests    --settag CtaG --settag ctag    misc/normal.robot
    Check Test Tags    First One    CtaG    f1    t1    t2
