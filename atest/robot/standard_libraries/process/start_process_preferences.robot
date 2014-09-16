*** Settings ***
Suite Setup      Run Tests    ${EMPTY}    standard_libraries/process/start_process_preferences.robot
Force Tags       regression    pybot    jybot
Resource         process_resource.robot

*** Test Cases ***
Explicitly run Operating System library keyword
    ${test}=   Check Test Case    ${TESTNAME}
    Should Be Equal  ${test.kws[0].name}  \${handle} = OperatingSystem.Start Process

Explicitly run Process library keyword
    ${test}=   Check Test Case    ${TESTNAME}
    Should Be Equal  ${test.kws[0].name}  \${handle} = Process.Start Process

Implicitly run Process library keyword
    ${test}=   Check Test Case    ${TESTNAME}
    Should Be Equal  ${test.kws[0].name}  \${handle} = Process.Start Process

Implicitly run Operating System library keyword when library search order is set
    ${test}=   Check Test Case    ${TESTNAME}
    Should Be Equal  ${test.kws[1].name}  \${handle} = OperatingSystem.Start Process

Process switch
    Check Test Case   ${TESTNAME}
