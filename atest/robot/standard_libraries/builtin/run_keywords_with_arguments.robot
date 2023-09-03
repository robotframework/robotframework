*** Settings ***
Documentation   Testing Run Keywords when used with AND. Tests without AND are in
...             run_keywords.robot.
Suite Setup     Run Tests  ${EMPTY}  standard_libraries/builtin/run_keywords_with_arguments.robot
Resource        atest_resource.robot

*** Test Cases ***
With arguments
    ${tc}=  Test Should Have Correct Keywords  BuiltIn.Should Be Equal  BuiltIn.No Operation  BuiltIn.Log Many  BuiltIn.Should Be Equal
    Check Log Message  ${tc.kws[0].kws[2].msgs[1]}  1

Should fail with failing keyword
    Test Should Have Correct Keywords  BuiltIn.No Operation  BuiltIn.Should Be Equal

Should support keywords and arguments from variables
    ${tc}=  Test Should Have Correct Keywords  BuiltIn.Should Be Equal  BuiltIn.No Operation  BuiltIn.Log Many  BuiltIn.Should Be Equal As Integers
    Check Log Message  ${tc.kws[0].kws[2].msgs[0]}  hello
    Check Log Message  ${tc.kws[0].kws[2].msgs[1]}  1
    Check Log Message  ${tc.kws[0].kws[2].msgs[2]}  2
    Check Log Message  ${tc.kws[0].kws[2].msgs[3]}  3

AND must be upper case
    ${tc}=  Test Should Have Correct Keywords  BuiltIn.Log Many  no kw
    Check Log Message  ${tc.kws[0].kws[0].msgs[1]}  and

AND must be whitespace sensitive
    ${tc}=  Test Should Have Correct Keywords  BuiltIn.Log Many  no kw
    Check Log Message  ${tc.kws[0].kws[0].msgs[1]}  A ND

Escaped AND
    ${tc}=  Test Should Have Correct Keywords  BuiltIn.Log Many  no kw
    Check Log Message  ${tc.kws[0].kws[0].msgs[1]}  AND

AND from Variable
    ${tc}=  Test Should Have Correct Keywords  BuiltIn.Log Many  no kw
    Check Log Message  ${tc.kws[0].kws[0].msgs[1]}  AND

AND in List Variable
    ${tc}=  Test Should Have Correct Keywords  BuiltIn.Log Many  no kw
    Check Log Message  ${tc.kws[0].kws[0].msgs[1]}  AND

Escapes in List Variable should be handled correctly
    ${tc}=  Test Should Have Correct Keywords  BuiltIn.Log Many  no kw
    Check Log Message  ${tc.kws[0].kws[0].msgs[0]}  1
    Check Log Message  ${tc.kws[0].kws[0].msgs[1]}  AND
    Check Log Message  ${tc.kws[0].kws[0].msgs[2]}  2
    Check Log Message  ${tc.kws[0].kws[0].msgs[3]}  Log Many
    Check Log Message  ${tc.kws[0].kws[0].msgs[4]}  x\${escaped}
    Check Log Message  ${tc.kws[0].kws[0].msgs[5]}  c:\\temp

AND as last argument should raise an error
    Test Should Have Correct Keywords  BuiltIn.Log Many  BuiltIn.No Operation

Consecutive AND's
    Test Should Have Correct Keywords  BuiltIn.Log Many

AND as first argument should raise an error
    Check Test Case  ${TESTNAME}

Keywords names needing escaping
    Test Should Have Correct Keywords
    ...    Needs \\escaping \\\${notvar}    Needs \\escaping \\\${notvar}

Keywords names needing escaping as variable
    Test Should Have Correct Keywords
    ...    Needs \\escaping \\\${notvar}    Needs \\escaping \\\${notvar}
    ...    kw_index=1

In test teardown with non-existing variable in keyword name
    Check Test Case    ${TESTNAME}
