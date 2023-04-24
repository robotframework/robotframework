*** Settings ***
Resource          atest_resource.robot

*** Variables ***
${DIR}            ${DATADIR}/parsing/custom

*** Test Cases ***
Single file
    [Documentation]    Also tests parser implemented as a module.
    Run Tests    --parser ${DIR}/custom.py    ${DIR}/tests.custom
    Validate Suite    ${SUITE}    Tests    ${DIR}/tests.custom
    ...    Passing=PASS
    ...    Failing=FAIL:Error message
    ...    Empty=FAIL:Test cannot be empty.

Directory
    [Documentation]    Also tests parser implemented as a class.
    Run Tests    --parser ${DIR}/CustomParser.py    ${DIR}
    Validate Directory Suite    Custom    custom=False

Directory with init
    Run Tests    --parser ${DIR}/CustomParser.py:init=True    ${DIR}
    Validate Directory Suite    📁    custom=True

Override Robot parser
    Run Tests    --parser ${DIR}/CustomParser.py:.robot    ${DIR}/tests.robot
    Validate Suite    ${SUITE}    Tests    ${DIR}/tests.robot
    ...    Test in Robot file=PASS
    Run Tests    --parser ${DIR}/CustomParser.py:ROBOT    ${DIR}
    Validate Suite    ${SUITE}     Custom    ${DIR}    custom=False
    ...    Test in Robot file=PASS
    Validate Suite    ${SUITE.suites[0]}    Tests    ${DIR}/tests.robot
    ...    Test in Robot file=PASS

Directory with init when parser does not support inits
    Parsing Should Fail    init
    ...    Parsing '${DIR}' failed:
    ...    'CustomParser' does not support parsing initialization files.

Incompatible parser
    Parsing Should Fail    parse=False
    ...    Importing parser '${DIR}/CustomParser.py' failed:
    ...    'CustomParser' does not have mandatory 'parse' method.
    Parsing Should Fail    extension=
    ...    Importing parser '${DIR}/CustomParser.py' failed:
    ...    'CustomParser' does not have mandatory 'EXTENSION' or 'extension' attribute.

Failing parser
    Parsing Should Fail    fail=True
    ...    Parsing '${DIR}${/}more.custom' failed:
    ...    Calling 'CustomParser.parse()' failed:
    ...    TypeError: Ooops!
    Parsing Should Fail    fail=True:init=True
    ...    Parsing '${DIR}' failed:
    ...    Calling 'CustomParser.parse_init()' failed:
    ...    TypeError: Ooops in init!

Bad return value
    Parsing Should Fail    bad_return=True
    ...    Parsing '${DIR}${/}more.custom' failed:
    ...    Calling 'CustomParser.parse()' failed:
    ...    TypeError: Return value should be 'robot.running.TestSuite', got 'string'.
    Parsing Should Fail    bad_return=True:init=True
    ...    Parsing '${DIR}' failed:
    ...    Calling 'CustomParser.parse_init()' failed:
    ...    TypeError: Return value should be 'robot.running.TestSuite', got 'integer'.

*** Keywords ***
Validate Suite
    [Arguments]    ${suite}    ${name}    ${source}    ${custom}=True    &{tests}
    ${source} =    Normalize Path    ${source}
    Should Be Equal    ${suite.name}     ${name}
    Should Be Equal As Strings   ${suite.source}    ${source}
    IF    ${custom}
        Should Be Equal    ${suite.metadata}[Parser]    Custom
    ELSE
        Should Not Contain    ${suite.metadata}     Parser
    END
    Should Contain Tests    ${suite}    &{tests}

Validate Directory Suite
    [Arguments]    ${name}    ${custom}=True
    Validate Suite    ${SUITE}    ${name}    ${DIR}    ${custom}
    ...    Passing=PASS
    ...    Failing=FAIL:Error message
    ...    Empty=FAIL:Test cannot be empty.
    ...    Test in Robot file=PASS
    ...    Yet another test=PASS
    Validate Suite    ${SUITE.suites[0]}    More    ${DIR}/more.custom
    ...    Yet another test=PASS
    Validate Suite    ${SUITE.suites[1]}    Tests    ${DIR}/tests.custom
    ...    Passing=PASS
    ...    Failing=FAIL:Error message
    ...    Empty=FAIL:Test cannot be empty.
    Validate Suite    ${SUITE.suites[2]}    Tests    ${DIR}/tests.robot    custom=False
    ...    Test in Robot file=PASS

Parsing should fail
    [Arguments]    ${config}    @{error}
    ${result} =    Run Tests    --parser ${DIR}/CustomParser.py:${config}    ${DIR}    output=None
    ${error} =    Catenate    @{error}
    Should Be Equal    ${result.rc}    ${252}
    Should Be Equal    ${result.stderr}    [ ERROR ] ${error}${USAGETIP}
