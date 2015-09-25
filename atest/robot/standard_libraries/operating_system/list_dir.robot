*** Settings ***
Suite Setup       Run Tests    ${EMPTY}    standard_libraries/operating_system/list_dir.robot
Resource          atest_resource.robot

*** Variables ***
${BASE}           %{TEMPDIR}${/}robot-os-tests
${DIR}            foodir
${F1}             foo.txt
${F2}             nön-äscïï.txt

*** Test Cases ***
List And Count Directory
    ${tc} =    Check Test Case    ${TESTNAME}
    Verify List And Count Messages    ${tc.kws[0]}    3 items    \n${F1}\n${DIR}\n${F2}
    Verify List And Count Messages    ${tc.kws[-1]}    0 items

List And Count Files In Directory
    ${tc} =    Check Test Case    ${TESTNAME}
    Verify List And Count Messages    ${tc.kws[0]}    2 files    \n${F1}\n${F2}
    Verify List And Count Messages    ${tc.kws[-1]}    0 files

List And Count Directories In Directory
    ${tc} =    Check Test Case    ${TESTNAME}
    Verify List And Count Messages    ${tc.kws[0]}    1 directory    \n${DIR}
    Verify List And Count Messages    ${tc.kws[-1]}    0 directories

List And Count Directory With Patterns
    ${tc} =    Check Test Case    ${TESTNAME}
    Verify List And Count Messages    ${tc.kws[0]}    2 items    \n${F1}\n${F2}
    Verify List And Count Messages    ${tc.kws[1]}    2 items    \n${F1}\n${DIR}
    Verify List And Count Messages    ${tc.kws[2]}    0 items

List And Count Files In Directory With Patterns
    ${tc} =    Check Test Case    ${TESTNAME}
    Verify List And Count Messages    ${tc.kws[0]}    2 files    \n${F1}\n${F2}
    Verify List And Count Messages    ${tc.kws[1]}    1 file    \n${F1}
    Verify List And Count Messages    ${tc.kws[2]}    0 files

List And Count Directories In Directory With Patterns
    ${tc} =    Check Test Case    ${TESTNAME}
    Verify List And Count Messages    ${tc.kws[0]}    1 directory    \n${DIR}
    Verify List And Count Messages    ${tc.kws[-1]}    0 directories

List Directory With Absolute
    ${tc} =    Check Test Case    ${TESTNAME}
    Verify List Message    ${tc.kws[0]}    2 items    \n${BASE}${/}${F1}\n${BASE}${/}${F2}
    Verify List Message    ${tc.kws[2]}    2 files    \n${BASE}${/}${F1}\n${BASE}${/}${F2}
    Verify List Message    ${tc.kws[4]}    1 directory    \n${BASE}${/}${DIR}

*** Keywords ***
Verify List And Count Messages
    [Arguments]    ${kw}    ${count}    ${files}=
    Verify List Message    ${kw.kws[0]}    ${count}    ${files}
    Verify Count Message    ${kw.kws[1]}    ${count}

Verify List Message
    [Arguments]    ${kw}    ${count}    ${files}=
    Check Log Message    ${kw.msgs[0]}    Listing contents of directory '<a href="file://${BASE}">${BASE}</a>'.    HTML
    Check Log Message    ${kw.msgs[-2]}    ${count}:${files}

Verify Count Message
    [Arguments]    ${kw}    ${count}
    Check Log Message    ${kw.msgs[0]}    Listing contents of directory '<a href="file://${BASE}">${BASE}</a>'.    HTML
    Check Log Message    ${kw.msgs[1]}    ${count}.
