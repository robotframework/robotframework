*** Settings ***
Suite Setup       Run Tests    ${EMPTY}    keywords/embedded_arguments.robot keywords/embedded_arguments_match_all.robot
Resource          atest_resource.robot

*** Test Cases ***
Embedded Arguments In User Keyword Name
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message          ${tc[0, 0, 0]}    This is always executed
    Check Keyword Data         ${tc[0]}          User Peke Selects Advanced Python From Webshop    \${name}, \${book}
    Check Log Message          ${tc[2, 0, 0]}    This is always executed
    Check Keyword Data         ${tc[2]}          User Juha Selects Playboy From Webshop    \${name}, \${book}
    File Should Contain        ${OUTFILE}        name="User Peke Selects Advanced Python From Webshop"
    File Should Contain        ${OUTFILE}        source_name="User \${user} Selects \${item} From Webshop"
    File Should Not Contain    ${OUTFILE}        source_name="Log"

Complex Embedded Arguments
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message          ${tc[0, 0, 0]}    feature-works
    Check Log Message          ${tc[1, 0, 0]}    test case-is *executed*
    Check Log Message          ${tc[2, 0, 0]}    issue-is about to be done!
    File Should Contain        ${OUTFILE}        source_name="\${prefix:Given|When|Then} this
    File Should Not Contain    ${OUTFILE}        source_name="Log"

Embedded Arguments with BDD Prefixes
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Keyword Data         ${tc[0]}      Given user x selects y from webshop
    Check Keyword Data         ${tc[1]}      When user x selects y from webshop
    Check Keyword Data         ${tc[2]}      Then user x selects y from webshop    \${x}, \${y}
    File Should Contain        ${OUTFILE}    name="Given user x selects y from webshop"
    File Should Contain        ${OUTFILE}    source_name="User \${user} Selects \${item} From Webshop"
    File Should Not Contain    ${OUTFILE}    source_name="Log"

Argument Namespaces with Embedded Arguments
    Check Test Case    ${TEST NAME}
    File Should Contain        ${OUTFILE}    name="My embedded warrior"
    File Should Contain        ${OUTFILE}    source_name="My embedded \${var}"
    File Should Not Contain    ${OUTFILE}    source_name="Log"

Embedded Arguments as Variables
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Keyword Data         ${tc[0]}      User \${42} Selects \${EMPTY} From Webshop    \${name}, \${item}
    Check Keyword Data         ${tc[2]}      User \${name} Selects \${SPACE * 10} From Webshop    \${name}, \${item}
    File Should Contain        ${OUTFILE}    name="User \${42} Selects \${EMPTY} From Webshop"
    File Should Contain        ${OUTFILE}    source_name="User \${user} Selects \${item} From Webshop"
    File Should Contain        ${OUTFILE}    name="User \${name} Selects \${SPACE * 10} From Webshop"
    File Should Contain        ${OUTFILE}    source_name="User \${user} Selects \${item} From Webshop"
    File Should Not Contain    ${OUTFILE}    source_name="Log">

Embedded Arguments as List And Dict Variables
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Keyword Data    ${tc[1]}    User \@{i1} Selects \&{i2} From Webshop    \${o1}, \${o2}

Non-Existing Variable in Embedded Arguments
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Keyword Data    ${tc[0]}    User \${non existing} Selects \${variables} From Webshop    status=FAIL

Invalid List Variable as Embedded Argument
    Check Test Case    ${TEST NAME}

Invalid Dict Variable as Embedded Argument
    Check Test Case    ${TEST NAME}

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

Non Matching Variable Is Accepted With Custom Regexp (But Not For Long)
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message    ${tc[0][0]}
    ...    Embedded argument 'x' got value 'foo' that does not match custom pattern 'bar'. The argument is still accepted, but this behavior will change in Robot Framework 8.0.    WARN

Partially Matching Variable Is Accepted With Custom Regexp (But Not For Long)
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message    ${tc[0][0]}
    ...    Embedded argument 'x' got value 'ba' that does not match custom pattern 'bar'. The argument is still accepted, but this behavior will change in Robot Framework 8.0.    WARN
    Check Log Message    ${tc[0][1]}
    ...    Embedded argument 'y' got value 'zapzap' that does not match custom pattern '...'. The argument is still accepted, but this behavior will change in Robot Framework 8.0.    WARN

Non String Variable Is Accepted With Custom Regexp
    Check Test Case    ${TEST NAME}

Custom regexp with inline flag
    Check Test Case    ${TEST NAME}

Invalid Custom Regexp
    Check Test Case    ${TEST NAME}
    Creating Keyword Failed    0    310
    ...    Invalid \${x:(} Regexp
    ...    Compiling embedded arguments regexp failed: *

Escaping Values Given As Embedded Arguments
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Keyword Data    ${tc[0]}    User \\\${nonex} Selects \\\\ From Webshop    \${name}, \${item}
    Check Keyword Data    ${tc[2]}    User \\ Selects \\ \\ From Webshop    \${name}, \${item}

Embedded Arguments Syntax Is Case Insensitive
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Keyword Data    ${tc[0]}    x Gets y From The z
    Check Keyword Data    ${tc[1]}    x gets y from the z
    Check Keyword Data    ${tc[2]}    x GETS y from the z
    Check Keyword Data    ${tc[3]}    x gets y FROM THE z

Embedded Arguments Syntax is Space Sensitive
    Check Test Case    ${TEST NAME}

Embedded Arguments Syntax is Underscore Sensitive
    Check Test Case    ${TEST NAME}

Embedded Arguments In Resource File
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Keyword Data    ${tc[0]}    embedded_args_in_uk_1.Juha Uses Resource File    \${ret}

Embedded Arguments In Resource File Used Explicitly
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Keyword Data    ${tc[0]}    embedded_args_in_uk_1.peke uses resource file    \${ret}

Keyword with only embedded arguments doesn't accept normal arguments
    Check Test Case    ${TEST NAME}

Keyword with embedded args cannot be used as "normal" keyword
    Check Test Case    ${TEST NAME}

Keyword with both embedded and normal arguments
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log message    ${tc[0, 0, 0]}    2 horses are walking
    Check Log message    ${tc[1, 0, 0]}    2 horses are swimming
    Check Log message    ${tc[2, 0, 0]}    3 dogs are walking

Keyword with both embedded and normal arguments with too few arguments
    Check Test Case    ${TEST NAME}

Keyword matching multiple keywords in test case file
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message    ${tc[0, 0, 0]}    foo+tc+bar
    Check Log Message    ${tc[1, 0, 0]}    foo-tc-bar
    Check Log Message    ${tc[2, 0, 0]}    foo+tc+bar+tc+zap

Keyword matching multiple keywords in one resource file
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message    ${tc[0, 0, 0]}    foo+r1+bar
    Check Log Message    ${tc[1, 0, 0]}    foo-r1-bar

Keyword matching multiple keywords in different resource files
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message    ${tc[0, 0, 0]}    foo-r1-bar
    Check Log Message    ${tc[1, 0, 0]}    foo-r2-bar

Keyword matching multiple keywords in one and different resource files
    Check Test Case    ${TEST NAME}

Same name with different regexp works
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message    ${tc[0, 0, 0]}    a car
    Check Log Message    ${tc[1, 0, 0]}    a dog
    Check Log Message    ${tc[2, 0, 0]}    a cow

Same name with different regexp matching multiple fails
    Check Test Case    ${TEST NAME}

Same name with same regexp fails
    Check Test Case    ${TEST NAME}

Match all allowed
    Check Test Case    ${TEST NAME}

*** Keywords ***
Creating Keyword Failed
    [Arguments]    ${index}    ${lineno}    ${name}    ${error}
    Error In File    ${index}    keywords/embedded_arguments.robot    ${lineno}
    ...    Creating keyword '${name}' failed: ${error}
