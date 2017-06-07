*** Settings ***
Resource      atest_resource.robot

*** Variables ***
${INPUT 1}      ${DATADIR}${/}misc${/}pass_and_fail.robot
${INPUT 2}      ${DATADIR}${/}misc${/}suites
${INPUT 3}      ${DATADIR}${/}testdoc
${OUTFILE}      %{TEMPDIR}/testdoc-output.html
${ARGFILE 1}    %{TEMPDIR}/testdoc_argfile_1.txt
${ARGFILE 2}    %{TEMPDIR}/testdoc_argfile_2.txt

*** Test Cases ***
One input
    Run TestDoc    ${INPUT 1}
    Testdoc Should Contain    "name":"Pass And Fail"    "title":"Pass And Fail"    "numberOfTests":2
    Outfile Should Have Correct Line Separators
    Output Should Contain Outfile

Variables and imports are not processes
    Run TestDoc    ${INPUT 3}
    Testdoc Should Contain    "name":"Testdoc"    "title":"Testdoc"    "numberOfTests":1
    Outfile Should Have Correct Line Separators
    Output Should Contain Outfile

Many inputs
    Run TestDoc    --exclude    t1    --title    Nön-ÄSCII
    ...    ${INPUT 1}    ${INPUT2}    ${INPUT 3}
    Testdoc Should Contain    "name":"Pass And Fail &amp; Suites &amp; Testdoc"    "title":"Nön-ÄSCII"    "numberOfTests":8
    Testdoc Should Not Contain    "name":"Suite4 First"
    Outfile Should Have Correct Line Separators
    Output Should Contain Outfile

Argument file
    Create Argument File    ${ARGFILE 1}
    ...    --name Testing argument file
    ...    --doc Overridden from cli
    ...    ${EMPTY}
    ...    \# I'm a comment and I'm OK! And so are empty rows around me too.
    ...    ${EMPTY}
    ...    --exclude pass
    Create Argument File    ${ARGFILE 2}
    ...    --title My title!
    ...    ${INPUT 1}
    Run TestDoc
    ...    --name    Overridden by argument file
    ...    --argumentfile    ${ARGFILE 1}
    ...    --doc    The doc
    ...    -A    ${ARGFILE 2}
    Testdoc Should Contain    "name":"Testing argument file"    "title":"My title!"    "numberOfTests":1
    Outfile Should Have Correct Line Separators
    Output Should Contain Outfile

Invalid usage
    Run TestDoc    rc=252
    Should Be Equal    ${OUTPUT}    Expected at least 2 arguments, got 1.${USAGE TIP}

*** Keyword ***
Run TestDoc
    [Arguments]    @{args}    &{expected}
    Remove File    ${OUTFILE}
    ${result} =    Run Process    @{INTERPRETER.testdoc}    @{args}    ${OUTFILE}    stderr=STDOUT
    Should Be Equal As Integers    ${result.rc}    ${expected.get('rc', 0)}
    ...    Unpexted rc ${result.rc}. Output was:\n${result.stdout}    values=False
    Set Test Variable    ${OUTPUT}    ${result.stdout}

Testdoc Should Contain
    [Arguments]    @{expected}
    ${testdoc}=    Get File    ${OUTFILE}
    : FOR     ${exp}    IN    @{expected}
    \    Should Contain    ${testdoc}   ${exp}

Testdoc Should Not Contain
    [Arguments]    @{expected}
    ${testdoc}=    Get File    ${OUTFILE}
    : FOR     ${exp}    IN    @{expected}
    \    Should Not Contain    ${testdoc}   ${exp}

Outfile Should Have Correct Line Separators
    File should have correct line separators    ${OUTFILE}

Output Should Contain Outfile
    [Documentation]    Printed outfile may be in different formats.
    ...                IronPython seems to like c:\olddos~1\format~2.ext
    Should Not Contain    ${OUTPUT}    ERROR
    File Should Exist    ${OUTPUT}
    Remove File    ${OUTFILE}
    File Should Not Exist    ${OUTPUT}

Create Argument File
    [Arguments]    ${path}    @{content}
    ${content} =    Catenate    SEPARATOR=\n    @{content}
    Create File    ${path}    ${content}
