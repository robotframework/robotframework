*** Settings ***
Suite Setup      Run Tests    ${EMPTY}    running/detect_recursion.robot
Library          GetNestingLevel.py
Resource         atest_resource.robot

*** Test Cases ***
Infinite recursion
    Check Test Case    ${TESTNAME}

Infinite cyclic recursion
    Check Test Case    ${TESTNAME}

Infinite recursion with Run Keyword
    Check Test Case    ${TESTNAME}

Infinitely recursive for loop
    Check Test Case    ${TESTNAME}

Recursion below the recursion limit is ok
    [Documentation]    Also verifies that recursion limit blown earlier doesn't affect subsequent tests
    Check Test Case    ${TESTNAME}

Recursion limit is over 140 started keywords
    ${tc} =    Check Test Case    Infinite recursion
    ${level} =    Get Nesting Level    ${tc}
    Should Be True    140 < ${level} < 160

Recursion limit can be raised with `sys.setrecursionlimit`
    [Setup]    Should Be True    sys.getrecursionlimit() == 1000
    # Raise limit with executed tests using sitecustomize.py.
    Create File    %{TEMPDIR}/sitecustomize.py    import sys; sys.setrecursionlimit(1500)
    Set Environment Variable    PYTHONPATH    %{TEMPDIR}
    # Also raise limit here to be able to process created outputs.
    Evaluate    sys.setrecursionlimit(1500)
    Run Tests    -t "Infinite recursion"    running/detect_recursion.robot
    ${tc} =    Check Test Case    Infinite recursion
    ${level} =    Get Nesting Level    ${tc}
    Should Be True    220 < ${level} < 240
    [Teardown]    Run Keywords
    ...    Remove File    %{TEMPDIR}/sitecustomize.py    AND
    ...    Evaluate    sys.setrecursionlimit(1000)
