*** Settings ***
Suite Setup       Run Tests    --pythonpath ${DATADIR}/test_libraries    test_libraries/library_decorator.robot
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

When importing a module and there is one decorated class, the class is used as a library
    Check Test Case    ${TESTNAME}

When importing a module and there are multiple decorated classes, the module is used as a library
    Check Test Case    ${TESTNAME}

When importing class explicitly, module can have multiple decorated classes
    Check Test Case    ${TESTNAME}

Imported decorated classes are not considered to be libraries automatically
    Check Test Case    ${TESTNAME}

Set library info
    [Template]    Library should have been imported
    LibraryDecorator.py                    scope=TEST      keywords=3
    LibraryDecoratorWithArgs.py            scope=SUITE     keywords=1    version=1.2.3    listener=True
    LibraryDecoratorWithAutoKeywords.py    scope=GLOBAL    keywords=2
    multiple_library_decorators.Class2     scope=SUITE     keywords=1
    extend_decorated_library.py            scope=TEST      keywords=2    version=extended

*** Keywords ***
Library should have been imported
    [Arguments]    ${name}    @{}    ${version}=<unknown>    ${scope}    ${keywords}    ${listener}=False
    IF    $name.endswith('.py')
        ${name} =    Normalize path    ${DATADIR}/test_libraries/${name}
    END
    Syslog Should Contain
    ...    Imported library '${name}' with arguments [ ]
    ...    (version ${version}, class type, ${scope} scope, ${keywords} keywords${{', with listener' if ${listener} else ''}})
