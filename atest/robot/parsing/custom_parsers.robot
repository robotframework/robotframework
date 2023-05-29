*** Settings ***
Resource          atest_resource.robot

*** Variables ***
${DIR}            ${{pathlib.Path(r'${DATADIR}/parsing/custom')}}

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
    Validate Directory Suite

Directory with init
    Run Tests    --parser ${DIR}/CustomParser.py:init=True    ${DIR}
    Validate Directory Suite    init=True

Extension with multiple parts
    [Documentation]    Also tests usage with `--parse-include`.
    Run Tests    --parser ${DIR}/CustomParser.py:multi.part.ext --parse-include *.multi.part.ext    ${DIR}
    Validate Suite    ${SUITE}    Custom    ${DIR}    custom=False
    ...    Passing=PASS
    Validate Suite    ${SUITE.suites[0]}    Tests    ${DIR}/tests.multi.part.ext
    ...    Passing=PASS

Override Robot parser
    Run Tests    --parser ${DIR}/CustomParser.py:.robot    ${DIR}/tests.robot
    Validate Suite    ${SUITE}    Tests    ${DIR}/tests.robot
    ...    Test in Robot file=PASS
    Run Tests    --parser ${DIR}/CustomParser.py:ROBOT    ${DIR}
    Validate Suite    ${SUITE}     Custom    ${DIR}    custom=False
    ...    Test in Robot file=PASS
    Validate Suite    ${SUITE.suites[0]}    Tests    ${DIR}/tests.robot
    ...    Test in Robot file=PASS

Multiple parsers
    Run Tests    --parser ${DIR}/CustomParser.py:ROBOT --PARSER ${DIR}/custom.py    ${DIR}
    Validate Directory Suite    custom_robot=True

Directory with init when parser does not support inits
    Parsing Should Fail    init
    ...    Parsing '${DIR}${/}__init__.init' failed:
    ...    'CustomParser' does not support parsing initialization files.

Incompatible parser
    Parsing Should Fail    parse=False
    ...    Importing parser '${DIR}${/}CustomParser.py' failed:
    ...    'CustomParser' does not have mandatory 'parse' method.
    Parsing Should Fail    extension=
    ...    Importing parser '${DIR}${/}CustomParser.py' failed:
    ...    'CustomParser' does not have mandatory 'EXTENSION' or 'extension' attribute.

Failing parser
    Parsing Should Fail    fail=True
    ...    Parsing '${DIR}${/}more.custom' failed:
    ...    Calling 'CustomParser.parse()' failed:
    ...    TypeError: Ooops!
    Parsing Should Fail    fail=True:init=True
    ...    Parsing '${DIR}${/}__init__.init' failed:
    ...    Calling 'CustomParser.parse_init()' failed:
    ...    TypeError: Ooops in init!

Bad return value
    Parsing Should Fail    bad_return=True
    ...    Parsing '${DIR}${/}more.custom' failed:
    ...    Calling 'CustomParser.parse()' failed:
    ...    TypeError: Return value should be 'robot.running.TestSuite', got 'string'.
    Parsing Should Fail    bad_return=True:init=True
    ...    Parsing '${DIR}${/}__init__.init' failed:
    ...    Calling 'CustomParser.parse_init()' failed:
    ...    TypeError: Return value should be 'robot.running.TestSuite', got 'integer'.

*** Keywords ***
Validate Suite
    [Arguments]    ${suite}    ${name}    ${source}    ${custom}=True    &{tests}
    ${source} =    Normalize Path    ${source}
    Should Be Equal    ${suite.name}     ${name}
    Should Be Equal As Strings    ${suite.source}    ${source}
    IF    ${custom}
        Should Be Equal    ${suite.metadata}[Parser]    Custom
    ELSE
        Should Not Contain    ${suite.metadata}     Parser
    END
    Should Contain Tests    ${suite}    &{tests}

Validate Directory Suite
    [Arguments]    ${init}=False    ${custom_robot}=False
    Validate Suite    ${SUITE}    ${{'📁' if ${init} else 'Custom'}}    ${DIR}    ${init}
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
    Validate Suite    ${SUITE.suites[2]}    Tests    ${DIR}/tests.robot    custom=${custom robot}
    ...    Test in Robot file=PASS
    FOR    ${test}    IN    @{SUITE.all_tests}
        IF    ${init}
            Should Contain Tags    ${test}            tag from init
            Should Be Equal        ${test.timeout}    42 seconds
            IF    '${test.name}' != 'Empty'
                Check Log Message    ${test.setup.msgs[0]}       setup from init
                Check Log Message    ${test.teardown.msgs[0]}    teardown from init
            END
        ELSE
            Should Not Be True    ${test.tags}
            Should Not Be True    ${test.timeout}
            Should Not Be True    ${test.setup}
            Should Not Be True    ${test.teardown}
        END
    END

Parsing should fail
    [Arguments]    ${config}    @{error}
    ${result} =    Run Tests    --parser ${DIR}/CustomParser.py:${config}    ${DIR}    output=None
    ${error} =    Catenate    @{error}
    Should Be Equal    ${result.rc}    ${252}
    Should Be Equal    ${result.stderr}    [ ERROR ] ${error}${USAGETIP}
