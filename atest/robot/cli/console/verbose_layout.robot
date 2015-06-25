*** Settings ***
Suite Setup     Run Tests  --variable FAIL:YES --log mylog.html --report myreport.html --debugfile mydebug.txt  misc/suites/subsuites
Force Tags      regression   pybot  jybot
Resource        console_resource.robot

*** Test Cases ***
Top Level Suite Start
    Check Stdout Contains  ${SEP_LINE1}\n Subsuites${SPACE * 69}\n ${SEP_LINE1}\n

Top Level Suite End
    ${status} =  Create Status Line  Subsuites  61  FAIL
    Check Stdout Contains  ${SEP_LINE1}\n ${status}\n ${MSG_211}\n ${SEP_LINE1}\n

Nested Suite Start
    Check Stdout Contains  ${SEP_LINE1}\n Subsuites.Sub1 :: Normal test cases${SPACE * 43}\n ${SEP_LINE1}\n

Nested Suite End
    ${status} =  Create Status Line  Subsuites.Sub2 :: Normal test cases  35  PASS
    Check Stdout Contains  ${SEP_LINE2}\n ${status}\n ${MSG_110}\n ${SEP_LINE1}\n

Passing Test
    ${status} =  Create Status Line  SubSuite2 First  55  PASS
    Check Stdout Contains  ${SEP_LINE1}\n ${status}\n ${SEP_LINE2}\n

Failing Test
    ${status} =  Create Status Line  SubSuite1 First  55  FAIL
    Check Stdout Contains  ${SEP_LINE1}\n ${status}\n This test was doomed to fail: YES != NO\n ${SEP_LINE2}\n

Outputs
    ${stdout} =  Get Stdout
    ${outputs} =  Evaluate  '''${stdout.replace('\\','\\\\')}'''.split('${SEP_LINE1}')[-1]
    Should Match Regexp  ${outputs}  Debug: \ \ .*mydebug.txt\n Output: \ .*output.xml\n Log: \ \ \ \ .*mylog.html\n Report: \ .*myreport.html\n

Long Documentation Should Be Cut
    ${doc} =  Evaluate  '0123456789' * 10
    Run Tests  --name My_Name --doc start${doc}end  misc/normal.robot
    ${expbase} =  Evaluate  'My Name :: start' + '0123456789'*5
    Check Stdout Contains  ${SEP_LINE1}\n ${expbase}012345678...\n ${SEP_LINE1}\n
    Check Stdout Contains  ${SEP_LINE2}\n ${expbase}... | PASS |\n

Long Name Should Be Cut
    ${name} =  Evaluate  '0123456789' * 10
    Run Tests  --name start${name}end --doc whatever  misc/normal.robot
    ${expbase} =  Evaluate  'start' + '0123456789'*6
    Check Stdout Contains  ${SEP_LINE1}\n ${expbase}0123456789...\n ${SEP_LINE1}\n
    Check Stdout Contains  ${SEP_LINE2}\n ${expbase}0... | PASS |\n

Layout Is Not Broken When There Are Warnings
    Run Tests    ${EMPTY}    misc/warnings_and_errors.robot
    Stdout Should Be    warnings_and_errors_stdout.txt
    Stderr Should Be    warnings_and_errors_stderr.txt
