*** Settings ***
Suite Setup       Run Tests    ${EMPTY}    test_libraries/library_decorator.robot
Resource          atest_resource.robot

*** Test Cases ***
Library decorator disables automatic keyword discovery
    Check Test Case    ${TESTNAME}

Static and class methods when automatic keyword discovery is disabled
    Check Test Case    ${TESTNAME}

Library decorator with arguments disables automatic keyword discovery by default
    Check Test Case    ${TESTNAME}

Library decorator can enable automatic keyword discovery
    Check Test Case    ${TESTNAME}

Set library info
    [Template]    Library should have been imported
    LibraryDecorator.py                    scope=TEST      keywords=3
    LibraryDecoratorWithArgs.py            scope=SUITE     keywords=1    version=1.2.3    listener=True
    LibraryDecoratorWithAutoKeywords.py    scope=GLOBAL    keywords=2

*** Keywords ***
Library should have been imported
    [Arguments]    ${name}    @{}    ${version}=<unknown>    ${scope}    ${keywords}    ${listener}=False
    ${path} =    Normalize path    ${DATADIR}/test_libraries/${name}
    Syslog Should Contain
    ...    Imported library '${path}' with arguments [ ]
    ...    (version ${version}, class type, ${scope} scope, ${keywords} keywords${{', with listener' if ${listener} else ''}})
