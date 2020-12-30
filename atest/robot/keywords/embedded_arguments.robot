*** Settings ***
Suite Setup       Run Tests    ${EMPTY}    keywords/embedded_arguments.robot keywords/embedded_arguments_match_all.robot
Resource          atest_resource.robot

*** Test Cases ***
Embedded Arguments In User Keyword Name
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message    ${tc.kws[0].kws[0].msgs[0]}    This is always executed
    Check Keyword Data    ${tc.kws[0]}    User Peke Selects Advanced Python From Webshop    \${name}, \${book}
    Check Log Message    ${tc.kws[2].kws[0].msgs[0]}    This is always executed
    Check Keyword Data    ${tc.kws[2]}    User Juha Selects Playboy From Webshop    \${name}, \${book}
    File Should Contain    ${OUTFILE}
    ...    name="User Peke Selects Advanced Python From Webshop"
    File Should Contain    ${OUTFILE}
    ...    sourcename="User \${user} Selects \${item} From Webshop"
    File Should Not Contain    ${OUTFILE}    sourcename="Log"

Complex Embedded Arguments
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message    ${tc.kws[0].kws[0].msgs[0]}    feature-works
    Check Log Message    ${tc.kws[1].kws[0].msgs[0]}    test case-is *executed*
    Check Log Message    ${tc.kws[2].kws[0].msgs[0]}    issue-is about to be done!
    File Should Contain    ${OUTFILE}    sourcename="\${prefix:Given|When|Then} this
    File Should Not Contain    ${OUTFILE}    sourcename="Log"

Embedded Arguments with BDD Prefixes
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Keyword Data    ${tc.kws[0]}    Given user x selects y from webshop
    Check Keyword Data    ${tc.kws[1]}    When user x selects y from webshop
    Check Keyword Data    ${tc.kws[2]}    Then user x selects y from webshop    \${x}, \${y}
    File Should Contain    ${OUTFILE}
    ...    name="Given user x selects y from webshop"
    File Should Contain    ${OUTFILE}
    ...    sourcename="User \${user} Selects \${item} From Webshop"
    File Should Not Contain    ${OUTFILE}    sourcename="Log"

Argument Namespaces with Embedded Arguments
    Check Test Case    ${TEST NAME}
    File Should Contain    ${OUTFILE}    name="My embedded warrior" 
    File Should Contain    ${OUTFILE}    sourcename="My embedded \${var}"
    File Should Not Contain    ${OUTFILE}    sourcename="Log"

Embedded Arguments as Variables
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Keyword Data    ${tc.kws[0]}    User \${42} Selects \${EMPTY} From Webshop    \${name}, \${item}
    Check Keyword Data    ${tc.kws[2]}    User \${name} Selects \${SPACE * 10} From Webshop    \${name}, \${item}
    File Should Contain    ${OUTFILE}
    ...    name="User \${42} Selects \${EMPTY} From Webshop"
    File Should Contain    ${OUTFILE}
    ...    sourcename="User \${user} Selects \${item} From Webshop"
    File Should Contain    ${OUTFILE}
    ...    name="User \${name} Selects \${SPACE * 10} From Webshop"
    File Should Contain    ${OUTFILE}
    ...    sourcename="User \${user} Selects \${item} From Webshop"
    File Should Not Contain    ${OUTFILE}    sourcename="Log">

Non-Existing Variable in Embedded Arguments
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Keyword Data    ${tc.kws[0]}    User \${non existing} Selects \${variables} From Webshop    status=FAIL

Non-Existing Variable in Embedded Arguments and Positional Arguments
    Check Test Case    ${TEST NAME}

Non-Existing Variable in Embedded Arguments and in Positional Arguments
    Check Test Case    ${TEST NAME}

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

Custom Regexp Matching Variables When Regexp Does No Match Them
    Check Test Case    ${TEST NAME}

Regexp Extensions Are Not Supported
    Check Test Case    ${TEST NAME}
    Creating Keyword Failed    1
    ...    Regexp extensions like \${x:(?x)re} are not supported
    ...    Regexp extensions are not allowed in embedded arguments.

Invalid Custom Regexp
    Check Test Case    ${TEST NAME}
    Creating Keyword Failed    2
    ...    Invalid \${x:(} Regexp
    ...    Compiling embedded arguments regexp failed: *
    ...    pattern=yes

Escaping Values Given As Embedded Arguments
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Keyword Data    ${tc.kws[0]}    User \\\${nonex} Selects \\\\ From Webshop    \${name}, \${item}
    Check Keyword Data    ${tc.kws[2]}    User \\ Selects \\ \\ From Webshop    \${name}, \${item}

Embedded Arguments Syntax Is Case Insensitive
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Keyword Data    ${tc.kws[0]}    x Gets y From The z
    Check Keyword Data    ${tc.kws[1]}    x gets y from the z
    Check Keyword Data    ${tc.kws[2]}    x GETS y from the z
    Check Keyword Data    ${tc.kws[3]}    x gets y FROM THE z

Embedded Arguments Syntax is Space Sensitive
    Check Test Case    ${TEST NAME}

Embedded Arguments Syntax is Underscore Sensitive
    Check Test Case    ${TEST NAME}

Embedded Arguments In Resource File
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Keyword Data    ${tc.kws[0]}    embedded_args_in_uk_1.Juha Uses Resource File    \${ret}

Embedded Arguments In Resource File Used Explicitly
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Keyword Data    ${tc.kws[0]}    embedded_args_in_uk_1.peke uses resource file    \${ret}

Embedded And Positional Arguments Do Not Work Together
    Check Test Case    ${TEST NAME}

Keyword with embedded args cannot be used as "normal" keyword
    Check Test Case    ${TEST NAME}

Creating keyword with both normal and embedded arguments fails
    Creating Keyword Failed    0
    ...    Keyword with \${embedded} and normal args is invalid
    ...    Keyword cannot have both normal and embedded arguments.
    Check Test Case    ${TEST NAME}

Keyword matching multiple keywords in test case file
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message    ${tc.kws[0].kws[0].msgs[0]}    foo+tc+bar
    Check Log Message    ${tc.kws[1].kws[0].msgs[0]}    foo-tc-bar
    Check Log Message    ${tc.kws[2].kws[0].msgs[0]}    foo+tc+bar+tc+zap

Keyword matching multiple keywords in one resource file
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message    ${tc.kws[0].kws[0].msgs[0]}    foo+r1+bar
    Check Log Message    ${tc.kws[1].kws[0].msgs[0]}    foo-r1-bar

Keyword matching multiple keywords in different resource files
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message    ${tc.kws[0].kws[0].msgs[0]}    foo-r1-bar
    Check Log Message    ${tc.kws[1].kws[0].msgs[0]}    foo-r2-bar

Keyword matching multiple keywords in one and different resource files
    Check Test Case    ${TEST NAME}

Same name with different regexp works
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message    ${tc.kws[0].kws[0].msgs[0]}    a car
    Check Log Message    ${tc.kws[1].kws[0].msgs[0]}    a dog
    Check Log Message    ${tc.kws[2].kws[0].msgs[0]}    a cow

Same name with different regexp matching multiple fails
    Check Test Case    ${TEST NAME}

Same name with same regexp fails
    Check Test Case    ${TEST NAME}

Match all allowed
    Check Test Case    ${TEST NAME}

*** Keywords ***
Creating Keyword Failed
    [Arguments]    ${index}    ${name}    ${error}    ${pattern}=
    ${source} =    Normalize Path    ${DATADIR}/keywords/embedded_arguments.robot
    ${message} =    Catenate
    ...    Error in test case file '${source}':
    ...    Creating keyword '${name}' failed: ${error}
    Check Log Message    ${ERRORS[${index}]}    ${message}    ERROR    pattern=${pattern}
