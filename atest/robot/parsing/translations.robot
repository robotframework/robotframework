*** Settings ***
Resource         atest_resource.robot

*** Test Cases ***
Built-in language
    Run Tests    --language fi    parsing/finnish/tests.robot
    Validate Translations

Custom language
    Run Tests    --lang ${DATADIR}/parsing/custom-lang.py    parsing/custom.robot
    Validate Translations

Task translations
    [Documentation]    Also test that '--language' works when running a directory.
    Run Tests    --language fi --rpa    parsing/finnish
    Validate Task Translations

Invalid
    ${result} =    Run Tests Without Processing Output    --lang bad    parsing/finnish.robot
    Should Be Equal        ${result.rc}        ${252}
    Should Be Empty        ${result.stdout}
    ${error} =    Catenate    SEPARATOR=\n
    ...    Invalid value for option '--language': Importing language file 'bad' failed: ModuleNotFoundError: No module named 'bad'
    ...    Traceback \\(most recent call last\\):
    ...    .*${USAGE TIP}
    Should Match Regexp    ${result.stderr}    (?s)^\\[ ERROR \\] ${error}$

*** Keywords ***
Validate Translations
    Should Be Equal    ${SUITE.doc}                   Suite documentation.
    Should Be Equal    ${SUITE.metadata}[Metadata]    Value
    Should Be Equal    ${SUITE.setup.name}            Suite Setup
    Should Be Equal    ${SUITE.teardown.name}         Suite Teardown
    Should Be Equal    ${SUITE.status}                PASS
    ${tc} =            Check Test Case                Test without settings
    Should Be Equal    ${tc.doc}                      ${EMPTY}
    Should Be Equal    ${tc.tags}                     ${{['test', 'tags']}}
    Should Be Equal    ${tc.timeout}                  1 minute
    Should Be Equal    ${tc.setup.name}               Test Setup
    Should Be Equal    ${tc.teardown.name}            Test Teardown
    Should Be Equal    ${tc.body[0].name}             Test Template
    Should Be Equal    ${tc.body[0].tags}             ${{['keyword', 'tags']}}
    ${tc} =            Check Test Case                Test with settings
    Should Be Equal    ${tc.doc}                      Test documentation.
    Should Be Equal    ${tc.tags}                     ${{['test', 'tags', 'own tag']}}
    Should Be Equal    ${tc.timeout}                  ${NONE}
    Should Be Equal    ${tc.setup.name}               ${NONE}
    Should Be Equal    ${tc.teardown.name}            ${NONE}
    Should Be Equal    ${tc.body[0].name}             Keyword
    Should Be Equal    ${tc.body[0].doc}              Keyword documentation.
    Should Be Equal    ${tc.body[0].tags}             ${{['keyword', 'tags', 'own tag']}}
    Should Be Equal    ${tc.body[0].timeout}          1 hour
    Should Be Equal    ${tc.body[0].teardown.name}    BuiltIn.No Operation

Validate Task Translations
    ${tc} =            Check Test Case                Task without settings
    Should Be Equal    ${tc.doc}                      ${EMPTY}
    Should Be Equal    ${tc.tags}                     ${{['task', 'tags']}}
    Should Be Equal    ${tc.timeout}                  1 minute
    Should Be Equal    ${tc.setup.name}               Task Setup
    Should Be Equal    ${tc.teardown.name}            Task Teardown
    Should Be Equal    ${tc.body[0].name}             Task Template
    ${tc} =            Check Test Case                Task with settings
    Should Be Equal    ${tc.doc}                      Task documentation.
    Should Be Equal    ${tc.tags}                     ${{['task', 'tags', 'own tag']}}
    Should Be Equal    ${tc.timeout}                  ${NONE}
    Should Be Equal    ${tc.setup.name}               ${NONE}
    Should Be Equal    ${tc.teardown.name}            ${NONE}
    Should Be Equal    ${tc.body[0].name}             BuiltIn.Log
