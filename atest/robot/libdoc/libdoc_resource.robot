*** Settings ***
Resource          atest_resource.robot
Library           LibDocLib.py    @{INTERPRETER.libdoc}
Library           OperatingSystem

*** Variables ***
${TESTDATADIR}    ${DATADIR}/libdoc
${OUTPREFIX}      %{TEMPDIR}${/}robot-libdoc-test-file
${OUTXML}         ${OUTPREFIX}.xml
${OUTHTML}        ${OUTPREFIX}.html

*** Keywords ***
Run Libdoc And Set Output
    [Arguments]    ${arguments}
    ${OUTPUT}=    Run Libdoc    ${arguments}
    Set Suite Variable    ${OUTPUT}

Run Libdoc And Parse Output
    [Arguments]    ${arguments}
    Remove File    ${OUTXML}
    Run Libdoc And Set Output    ${arguments} ${OUTXML}
    Should Not Contain    ${output}    --help    Execution failed:\n\n${output}    no values
    Log File    ${OUTXML}
    ${LIBDOC}=    Parse Xml    ${OUTXML}
    Set Suite Variable    ${LIBDOC}

Run Libdoc And Verify Output
    [Arguments]    ${args}    @{expected}
    ${output}=    Run Libdoc    ${args}
    ${expected}=    Catenate    SEPARATOR=\n    @{expected}
    Should Match    ${output}   ${expected}

Run Libdoc And Parse Model From HTML
    [Arguments]    ${args}
    Run Libdoc    ${args} ${OUT HTML}
    ${MODEL} =    Get Libdoc Model From HTML    ${OUT HTML}
    Set Suite Variable    ${MODEL}

Doc Should Contain In HTML
    [Arguments]    ${object}    ${expected}
    Should Contain    ${object['doc']}    ${expected}

Name Should Be
    [Arguments]    ${name}
    Element Attribute Should Be    ${LIBDOC}    name    ${name}

Doc Should Start With
    [Arguments]    @{doc}
    ${doc}=    Catenate     SEPARATOR=    @{doc}
    Element Text Should Match    ${LIBDOC}    ${doc}*    doc

Doc Should Be
    [Arguments]    @{doc}
    ${doc}=    Catenate     SEPARATOR=    @{doc}
    Element Text Should Be    ${LIBDOC}    ${doc}    doc

Version Should Match
    [Arguments]    ${version}
    Element Text Should Match    ${LIBDOC}    ${version}    version

Version Should Be
    [Arguments]    ${version}
    Element Text Should Be    ${LIBDOC}    ${version}    version

Type Should Be
    [Arguments]    ${type}
    Element Attribute Should Be    ${LIBDOC}    type    ${type}

Scope Should Be
    [Arguments]    ${scope}
    Element Text Should Be    ${LIBDOC}    ${scope}    scope

Named Args Should Be
    [Arguments]    ${namedargs}
    Element Text Should Be    ${LIBDOC}    ${namedargs}    namedargs

Generated Should Be Defined
    Element Attribute Should Match    ${LIBDOC}    generated    *

Should Have No Init
    ${inits} =    Get Elements    ${LIBDOC}    init
    Should Be Empty    ${inits}

Init Doc Should Start With
    [Arguments]    ${index}    @{doc}
    ${kws}=   Get Elements    ${LIBDOC}   init
    ${doc}=    Catenate     SEPARATOR=    @{doc}
    Element Text Should Match    ${kws[${index}]}    ${doc}*    doc

Init Doc Should Be
    [Arguments]    ${index}    @{doc}
    ${kws}=   Get Elements    ${LIBDOC}    init
    ${doc}=    Catenate     SEPARATOR=    @{doc}
    Element Text Should Be    ${kws[${index}]}    ${doc}    doc

Init Arguments Should Be
    [Arguments]    ${index}   @{expected}
    ${args}=    Get Keyword Arguments    ${index}    type=init
    Should Be Equal    ${args}    ${expected}

Keyword Name Should Be
    [Arguments]    ${index}   ${name}
    ${elements}=   Get Elements    ${LIBDOC}    kw
    Element Attribute Should Be    ${elements[${index}]}    name    ${name}

Keyword Arguments Should Be
    [Arguments]    ${index}    @{expected}
    ${args}=    Get Keyword Arguments    ${index}
    Should Be Equal    ${args}    ${expected}

Keyword Doc Should Start With
    [Arguments]    ${index}    @{doc}
    ${kws}=   Get Elements    ${LIBDOC}   kw
    ${doc}=    Catenate     SEPARATOR=    @{doc}
    Element Text Should Match    ${kws[${index}]}    ${doc}*    doc

Keyword Doc Should Be
    [Arguments]    ${index}    @{doc}
    ${kws}=   Get Elements    ${LIBDOC}    kw
    ${doc}=    Catenate     SEPARATOR=    @{doc}
    Element Text Should Be    ${kws[${index}]}    ${doc}    doc

Keyword Tags Should Be
    [Arguments]    ${index}    @{expected}
    ${kws}=    Get Elements    ${LIBDOC}    kw
    ${tags}=   Get Elements Texts    ${kws[${index}]}    tags/tag
    Should Be Equal    ${tags}    ${expected}

Get Keyword Arguments
    [Arguments]    ${index}   ${type}=kw
    ${kws}=    Get Elements    ${LIBDOC}    ${type}
    ${args}=    Get Elements Texts   ${kws[${index}]}    arguments/arg
    [Return]    ${args}

Keyword Count Should Be
    [Arguments]    ${expected}   ${type}=kw
    ${kws}=    Get Elements    ${LIBDOC}    ${type}
    Length Should Be    ${kws}    ${expected}

Remove Output Files
    Remove Files    ${OUTPREFIX}*
