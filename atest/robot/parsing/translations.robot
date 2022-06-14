*** Settings ***
Resource         atest_resource.robot

*** Test Cases ***
Built-in language
    Run Tests    --lang fi    parsing/finnish.robot
    Validate Translations

Custom language
    Run Tests    --lang ${DATADIR}/parsing/custom-lang.py    parsing/custom.robot
    Validate Translations

*** Keywords ***
Validate Translations
    Should Be Equal    ${SUITE.doc}                   Suite documentation.
    Should Be Equal    ${SUITE.metadata}[Metadata]    Value
    Should Be Equal    ${SUITE.setup.name}            Suite Setup
    Should Be Equal    ${SUITE.teardown.name}         Suite Teardown
    Should Be Equal    ${SUITE.status}                PASS
    ${tc} =            Check Test Case                Test without settings
    Should Be Equal    ${tc.doc}                      ${EMPTY}
    Should Be Equal    ${tc.tags}                     ${{['forced tag', 'default tag']}}
    Should Be Equal    ${tc.timeout}                  1 minute
    Should Be Equal    ${tc.setup.name}               Test Setup
    Should Be Equal    ${tc.teardown.name}            Test Teardown
    Should Be Equal    ${tc.body[0].name}             Test Template
    ${tc} =            Check Test Case                Test with settings
    Should Be Equal    ${tc.doc}                      Test documentation.
    Should Be Equal    ${tc.tags}                     ${{['forced tag', 'own tag']}}
    Should Be Equal    ${tc.timeout}                  ${NONE}
    Should Be Equal    ${tc.setup.name}               ${NONE}
    Should Be Equal    ${tc.teardown.name}            ${NONE}
    Should Be Equal    ${tc.body[0].name}             Keyword
    Should Be Equal    ${tc.body[0].doc}              Keyword documentation.
    Should Be Equal    ${tc.body[0].tags}             ${{['kw tag']}}
    Should Be Equal    ${tc.body[0].timeout}          1 hour
    Should Be Equal    ${tc.body[0].teardown.name}    BuiltIn.No Operation

