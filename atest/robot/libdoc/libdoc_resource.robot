*** Settings ***
Resource          atest_resource.robot
Library           LibDocLib.py    ${INTERPRETER}
Library           OperatingSystem

*** Variables ***
${TESTDATADIR}    ${DATADIR}/libdoc
${LIBNAME}        robot-libdoc-test-file
${OUTBASE}        %{TEMPDIR}${/}${LIBNAME}
${OUTXML}         ${OUTBASE}.xml
${OUTHTML}        ${OUTBASE}.html
${NEWDIR_XML}     %{TEMPDIR}${/}tempdir${/}${LIBNAME}.xml
${NEWDIR_HTML}    %{TEMPDIR}${/}tempdir${/}${LIBNAME}.html

*** Keywords ***
Run Libdoc And Set Output
    [Arguments]    ${arguments}
    ${OUTPUT}=    Run Libdoc    ${arguments}
    Set Suite Variable    ${OUTPUT}

Run Libdoc And Parse Output
    [Arguments]    ${arguments}
    Remove File    ${OUTXML}
    Run Libdoc And Set Output    ${arguments} ${OUTXML}
    Should Not Contain    ${OUTPUT}    --help    Execution failed:\n\n${output}    no values
    Log File    ${OUTXML}
    ${LIBDOC}=    Parse Xml    ${OUTXML}
    Set Suite Variable    ${LIBDOC}

Run Libdoc And Verify Output
    [Arguments]    ${args}    @{expected}
    ${output}=    Run Libdoc    ${args}
    ${expected}=    Catenate    SEPARATOR=\n    @{expected}
    Should Match    ${output}   ${expected}\n

Run Libdoc And Parse Model From HTML
    [Arguments]    ${args}
    Run Libdoc    ${args} ${OUT HTML}
    ${MODEL} =    Get Libdoc Model From HTML    ${OUT HTML}
    Set Suite Variable    ${MODEL}

Name Should Be
    [Arguments]    ${name}
    Element Attribute Should Be    ${LIBDOC}    name    ${name}

Format Should Be
    [Arguments]    ${format}
    Element Attribute Should Be    ${LIBDOC}    format    ${format}

Doc Should Start With
    [Arguments]    @{doc}
    ${doc}=    Catenate     SEPARATOR=\n    @{doc}
    Element Text Should Match    ${LIBDOC}    ${doc}*    doc

Doc Should Be
    [Arguments]    @{doc}
    ${doc}=    Catenate     SEPARATOR=\n    @{doc}
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
    ${inits} =    Get Elements    ${LIBDOC}    xpath=init
    Should Be Empty    ${inits}

Init Doc Should Start With
    [Arguments]    ${index}    @{doc}
    ${inits}=   Get Elements    ${LIBDOC}   xpath=init
    ${doc}=    Catenate     SEPARATOR=    @{doc}
    ${text} =    Get Element Text    ${inits}[${index}]    xpath=doc
    Should Start With    ${text}    ${doc}

Init Doc Should Be
    [Arguments]    ${index}    @{doc}
    ${kws}=   Get Elements    ${LIBDOC}    xpath=init
    ${doc}=    Catenate     SEPARATOR=    @{doc}
    Element Text Should Be    ${kws}[${index}]    ${doc}    xpath=doc

Init Arguments Should Be
    [Arguments]    ${index}   @{expected}
    ${args}=    Get Keyword Arguments    ${index}    type=init
    Should Be Equal    ${args}    ${expected}

Keyword Name Should Be
    [Arguments]    ${index}   ${name}
    ${elements}=   Get Elements    ${LIBDOC}    xpath=kw
    Element Attribute Should Be    ${elements}[${index}]    name    ${name}

Keyword Arguments Should Be
    [Arguments]    ${index}    @{expected}
    ${args}=    Get Keyword Arguments    ${index}
    Should Be Equal    ${args}    ${expected}

Keyword Doc Should Start With
    [Arguments]    ${index}    @{doc}
    ${kws}=   Get Elements    ${LIBDOC}   xpath=kw
    ${doc}=    Catenate     SEPARATOR=\n    @{doc}
    ${text} =    Get Element Text    ${kws}[${index}]    xpath=doc
    Should Start With    ${text}    ${doc}

Keyword Doc Should Be
    [Arguments]    ${index}    @{doc}
    ${kws}=   Get Elements    ${LIBDOC}    xpath=kw
    ${doc}=    Catenate     SEPARATOR=\n    @{doc}
    Element Text Should Be    ${kws}[${index}]    ${doc}    xpath=doc

Keyword Tags Should Be
    [Arguments]    ${index}    @{expected}
    ${kws}=    Get Elements    ${LIBDOC}    xpath=kw
    ${tags}=   Get Elements Texts    ${kws}[${index}]    xpath=tags/tag
    Should Be Equal    ${tags}    ${expected}

Keyword Should Be Deprecated
    [Arguments]    ${index}
    ${kws}=    Get Elements    ${LIBDOC}    xpath=kw
    Element Attribute Should be    ${kws}[${index}]    deprecated    true

Keyword Should Not Be Deprecated
    [Arguments]    ${index}
    ${kws}=    Get Elements    ${LIBDOC}    xpath=kw
    Element Attribute Should be    ${kws}[${index}]    deprecated    false

Get Keyword Arguments
    [Arguments]    ${index}   ${type}=kw
    ${kws}=    Get Elements    ${LIBDOC}    xpath=${type}
    ${args}=    Get Elements Texts   ${kws}[${index}]    xpath=arguments/arg
    [Return]    ${args}

Keyword Count Should Be
    [Arguments]    ${expected}   ${type}=kw
    ${kws}=    Get Elements    ${LIBDOC}    xpath=${type}
    Length Should Be    ${kws}    ${expected}

Remove Output Files
    Remove Files    ${OUTBASE}*

Should Be Equal Multiline
    [Arguments]    ${actual}    @{expected}
    ${expected} =    Catenate    SEPARATOR=\n    @{expected}
    Should Be Equal As Strings    ${actual}    ${expected}
