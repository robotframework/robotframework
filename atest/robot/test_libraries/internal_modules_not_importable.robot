*** Settings ***
Documentation     Robot's internal modules cannot be imported directly.
Suite Setup       Run Keywords
...    Create Directory    ${TESTDIR}${/}robot    AND
...    Run Tests    --pythonpath ${TESTDIR}    test_libraries/internal_modules_not_importable.robot
Suite Teardown    Remove Directory    ${TESTDIR}    recursively
Resource          atest_resource.robot

*** Variables ***
${TESTDIR}        %{TEMPDIR}${/}module_importing_14350

*** Test Cases ***
Internal modules cannot be imported directly
    Check Test Case    ${TESTNAME}

Internal modules can be imported through `robot.`
    Check Test Case    ${TESTNAME}

Standard libraries cannot be imported directly
    Check Test Case    ${TESTNAME}

Standard libraries can be imported through `robot.libraries.`
    Check Test Case    ${TESTNAME}

In test data standard libraries can be imported directly
    ${tc} =    Check Test Case    ${TESTNAME}
    Should Be Equal    ${tc.kws[0].full_name}    OperatingSystem.Directory Should Exist
    Should Be Equal    ${tc.kws[1].full_name}    OperatingSystem.Directory Should Exist
