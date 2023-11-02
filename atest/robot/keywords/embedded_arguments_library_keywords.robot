*** Settings ***
Suite Setup     Run Tests    ${EMPTY}    keywords/embedded_arguments_library_keywords.robot
Resource        atest_resource.robot

*** Test Cases ***
Embedded Arguments In Library Keyword Name
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message  ${tc.kws[0].msgs[0]}    This is always executed
    Check Keyword Data    ${tc.kws[0]}    embedded_args_in_lk_1.User Peke Selects Advanced Python From Webshop    \${name}, \${book}
    Check Log Message  ${tc.kws[2].msgs[0]}    This is always executed
    Check Keyword Data    ${tc.kws[2]}    embedded_args_in_lk_1.User Juha selects Playboy from webshop    \${name}, \${book}
    File Should Contain    ${OUTFILE}
    ...    name="User Peke Selects Advanced Python From Webshop"
    File Should Contain    ${OUTFILE}
    ...    owner="embedded_args_in_lk_1"
    File Should Contain    ${OUTFILE}
    ...    source_name="User \${user} Selects \${item} From Webshop"
    File Should Not Contain    ${OUTFILE}    source_name="Log"

Complex Embedded Arguments
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message    ${tc.kws[0].msgs[0]}    feature-works
    Check Log Message    ${tc.kws[1].msgs[0]}    test case-is *executed*
    Check Log Message    ${tc.kws[2].msgs[0]}    issue-is about to be done!
    File Should Contain    ${OUTFILE}    source_name="\${prefix:Given|When|Then} this
    File Should Not Contain    ${OUTFILE}    source_name="Log"

Embedded Arguments with BDD Prefixes
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Keyword Data    ${tc.kws[0]}    embedded_args_in_lk_1.Given user x selects y from webshop
    Check Keyword Data    ${tc.kws[1]}    embedded_args_in_lk_1.When user x selects y from webshop
    Check Keyword Data    ${tc.kws[2]}    embedded_args_in_lk_1.Then user x selects y from webshop    \${x}, \${y}
    File Should Contain    ${OUTFILE}    name="Given user x selects y from webshop"
    File Should Contain    ${OUTFILE}    owner="embedded_args_in_lk_1"
    File Should Contain    ${OUTFILE}    source_name="User \${user} Selects \${item} From Webshop"
    File Should Not Contain    ${OUTFILE}    source_name="Log"

Argument Namespaces with Embedded Arguments
    Check Test Case    ${TEST NAME}
    File Should Contain    ${OUTFILE}    name="My embedded warrior"
    File Should Contain    ${OUTFILE}    owner="embedded_args_in_lk_1"
    File Should Contain    ${OUTFILE}    source_name="My embedded \${var}"
    File Should Not Contain    ${OUTFILE}    source_name="Log"

Embedded Arguments as Variables
    ${tc} =    Check Test Case    ${TEST NAME}
    File Should Contain    ${OUTFILE}
    ...    name="User \${42} Selects \${EMPTY} From Webshop"
    File Should Contain    ${OUTFILE}
    ...    owner="embedded_args_in_lk_1"
    File Should Contain    ${OUTFILE}
    ...    source_name="User \${user} Selects \${item} From Webshop"
    File Should Contain    ${OUTFILE}
    ...    name="User \${name} Selects \${SPACE * 10} From Webshop"
    File Should Not Contain    ${OUTFILE}    source_name="Log"

Embedded Arguments as List And Dict Variables
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Keyword Data    ${tc.kws[1]}    embedded_args_in_lk_1.User \@{inp1} Selects \&{inp2} From Webshop    \${out1}, \${out2}

Non-Existing Variable in Embedded Arguments
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Keyword Data    ${tc.kws[0]}    embedded_args_in_lk_1.User \${non existing} Selects \${variables} From Webshop    status=FAIL

Custom Embedded Argument Regexp
    Check Test Case    ${TEST NAME}

Custom Regexp With Curly Braces
    Check Test Case    ${TEST NAME}

Custom Regexp With Escape Chars
    Check Test Case    ${TEST NAME}

Grouping Custom Regexp
    Check Test Case    ${TEST NAME}

Custom Regexp Matching Variables
    Check Test Case    ${TEST NAME}

Non Matching Variable Is Accepted With Custom Regexp (But Not For Long)
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message    ${tc.body[0].msgs[0]}
    ...    Embedded argument 'x' got value 'foo' that does not match custom pattern 'bar'. The argument is still accepted, but this behavior will change in Robot Framework 8.0.    WARN

Partially Matching Variable Is Accepted With Custom Regexp (But Not For Long)
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message    ${tc.body[0].msgs[0]}
    ...    Embedded argument 'x' got value 'ba' that does not match custom pattern 'bar'. The argument is still accepted, but this behavior will change in Robot Framework 8.0.    WARN
    Check Log Message    ${tc.body[0].msgs[1]}
    ...    Embedded argument 'y' got value 'zapzap' that does not match custom pattern '...'. The argument is still accepted, but this behavior will change in Robot Framework 8.0.    WARN

Non String Variable Is Accepted With Custom Regexp
    Check Test Case    ${TEST NAME}

Embedded Arguments Syntax is Space Sensitive
    Check Test Case    ${TEST NAME}

Embedded Arguments Syntax is Underscore Sensitive
    Check Test Case    ${TEST NAME}

Keyword matching multiple keywords in library file
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message    ${tc.kws[0].msgs[0]}    foo+lib+bar
    Check Log Message    ${tc.kws[1].msgs[0]}    foo-lib-bar
    Check Log Message    ${tc.kws[2].msgs[0]}    foo+lib+bar+lib+zap

Keyword matching multiple keywords in different library files
    Check Test Case    ${TEST NAME}

Keyword with only embedded arguments doesn't accept normal arguments
    Check Test Case    ${TEST NAME}

Keyword with embedded args cannot be used as "normal" keyword
    Check Test Case    ${TEST NAME}

Keyword with both embedded and normal arguments
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log message    ${tc.body[0].msgs[0]}    2 horses are walking
    Check Log message    ${tc.body[1].msgs[0]}    2 horses are swimming
    Check Log message    ${tc.body[2].msgs[0]}    3 dogs are walking

Conversion with embedded and normal arguments
    Check Test Case    ${TEST NAME}

Keyword with both embedded and normal arguments with too few arguments
    Check Test Case    ${TEST NAME}

Must accept at least as many positional arguments as there are embedded arguments
    Check Test Case    ${TESTNAME}
    Error in library    embedded_args_in_lk_1
    ...    Adding keyword 'Wrong \${number} of embedded \${args}' failed:
    ...    Keyword must accept at least as many positional arguments as it has embedded arguments.

Optional Non-Embedded Args Are Okay
    Check Test Case    ${TESTNAME}

Varargs With Embedded Args Are Okay
    Check Test Case    ${TESTNAME}

Lists are not expanded when keyword accepts varargs
    Check Test Case    ${TESTNAME}

Same name with different regexp works
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message    ${tc.kws[0].msgs[0]}    a car
    Check Log Message    ${tc.kws[1].msgs[0]}    a dog
    Check Log Message    ${tc.kws[2].msgs[0]}    a cow

Same name with different regexp matching multiple fails
    Check Test Case    ${TEST NAME}

Same name with same regexp fails
    Check Test Case    ${TEST NAME}
