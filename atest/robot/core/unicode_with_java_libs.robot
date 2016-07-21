*** Setting ***
Suite Setup       Run Tests    ${EMPTY}    core/unicode_with_java_libs.robot
Force Tags        require-jython
Resource          atest_resource.robot
Variables         ../../resources/unicode_vars.py

*** Test Case ***
Unicode In Xml Output
    ${test} =    Check Test Case    Unicode
    Check Log Message    ${test.kws[0].msgs[0]}    ${MESSAGE1}
    Check Log Message    ${test.kws[0].msgs[1]}    ${MESSAGE2}
    Check Log Message    ${test.kws[0].msgs[2]}    ${MESSAGE3}

Unicode Object
    ${test} =    Check Test Case    Unicode Object
    Check Log Message    ${test.kws[0].msgs[0]}    ${MESSAGES}
    Check Log Message    ${test.kws[0].msgs[1]}    \${obj} = ${MESSAGES}
    Check Log Message    ${test.kws[1].msgs[0]}    ${MESSAGES}

Unicode Error
    Check Test Case    Unicode Error    FAIL    ${MESSAGES}
