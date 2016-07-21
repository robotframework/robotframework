*** Settings ***
Resource      atest_resource.robot

*** Variables ***
${INPUT 1}    ${CURDIR}${/}..${/}..${/}testdata${/}misc${/}pass_and_fail.robot
${INPUT 2}    ${CURDIR}${/}..${/}..${/}testdata${/}misc${/}suites
${INPUT 3}    ${CURDIR}${/}..${/}..${/}testdata${/}testdoc
${OUTFILE}    %{TEMPDIR}${/}testdoc-output.html


*** Test Cases ***
One input
    ${output}=    Run TestDoc    ${INPUT 1}
    Testdoc Should Contain    "name":"Pass And Fail"    "title":"Pass And Fail"    "numberOfTests":2
    Outfile Should Have Correct Line Separators
    Output Should Contain Outfile    ${output}

Variables and imports are not processes
    ${output}=    Run TestDoc    ${INPUT 3}
    Testdoc Should Contain    "name":"Testdoc"    "title":"Testdoc"    "numberOfTests":1
    Outfile Should Have Correct Line Separators
    Output Should Contain Outfile    ${output}

Many inputs
    ${output}=    Run TestDoc    --exclude t1 --title Nön-ÄSCII ${INPUT 1} ${INPUT2} ${INPUT 3}
    Testdoc Should Contain    "name":"Pass And Fail &amp; Suites &amp; Testdoc"    "title":"Nön-ÄSCII"    "numberOfTests":8
    Testdoc Should Not Contain    "name":"Suite4 First"
    Outfile Should Have Correct Line Separators
    Output Should Contain Outfile    ${output}

Invalid usage
    ${output}=    Run TestDoc    ${EMPTY}    252
    Should Be Equal    ${output}    Expected at least 2 arguments, got 1.${USAGE TIP}


*** Keyword ***
Run TestDoc
    [Arguments]    ${args}    ${expected rc}=0
    @{args} =    Split Command line    ${args}
    ${result}=   Run Process  @{INTERPRETER.testdoc}  @{args}  ${OUTFILE}
    Should Be Equal As Numbers   ${result.rc}    ${expected rc}
    [Return]    ${result.stdout}

Testdoc Should Contain
    [Arguments]    @{expected}
    ${testdoc}=    Get File    ${OUTFILE}
    : FOR     ${exp}    IN   @{expected}
    \    Should Contain    ${testdoc}   ${exp}

Testdoc Should Not Contain
    [Arguments]    @{expected}
    ${testdoc}=    Get File    ${OUTFILE}
    : FOR     ${exp}    IN   @{expected}
    \    Should Not Contain    ${testdoc}   ${exp}

Outfile Should Have Correct Line Separators
    File should have correct line separators    ${OUTFILE}

Output Should Contain Outfile
    [Arguments]    ${output}
    [Documentation]    Printed outfile may be in different formats.
    ...                IronPython seems to like c:\olddos~1\format~2.ext
    Should Not Contain    ${output}    ERROR
    File Should Exist    ${output}
    Remove File    ${OUTFILE}
    File Should Not Exist    ${output}
