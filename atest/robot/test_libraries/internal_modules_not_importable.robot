*** Setting ***
Documentation     Robot's internal modules cannot be imported directly.
Suite Setup       Run Keywords
...    Create Directory    ${TESTDIR}${/}robot    AND
...    Run Tests    --pythonpath ${TESTDIR}    test_libraries/internal_modules_not_importable.robot
Suite Teardown    Remove Directory    ${TESTDIR}    recursively
Force Tags        regression    jybot    pybot
Resource          atest_resource.robot

*** Variable ***
${TESTDIR}        %{TEMPDIR}${/}module_importing_14350

*** Test Case ***
Internal modules cannot be imported directly
    Check Test Case    ${TESTNAME}

Internal modules can be imported through `robot.`
    Check Test Case    ${TESTNAME}
