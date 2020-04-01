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
    Should Not Contain    ${OUTPUT}    --help    Execution failed:\n\n${OUTPUT}    values=False
    Log File    ${OUTXML}
    Validate Spec    ${OUTXML}
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
    [Arguments]    ${scope}    ${old}=${{ {'GLOBAL': 'global', 'SUITE': 'test suite', 'TEST': 'test case'}[$scope] }}
    Element Attribute Should Be    ${LIBDOC}    scope    ${scope}
    # 'scope' element should be removed in RF 4.0.
    Element Text Should Be    ${LIBDOC}    ${old}    xpath=scope

Named Args Should Be
    [Arguments]    ${namedargs}
    Element Attribute Should Be    ${LIBDOC}    namedargs    ${namedargs}
    # 'namedargs' element should be removed in RF 4.0.
    Element Text Should Be    ${LIBDOC}
    ...    ${{'yes' if $namedargs == 'true' else 'no'}}    xpath=namedargs

Source Should Be
    [Arguments]    ${source}
    ${source} =    Relative Source    ${source}    %{TEMPDIR}
    Element Attribute Should Be    ${LIBDOC}    source    ${source}

Lineno Should Be
    [Arguments]    ${lineno}
    Element Attribute Should Be    ${LIBDOC}    lineno    ${lineno}

Generated Should Be Defined
    Element Attribute Should Match    ${LIBDOC}    generated    ????-??-??T??:??:??Z

Spec version should be correct
    Element Attribute Should Be    ${LIBDOC}    specversion    2

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

Get Keyword Arguments
    [Arguments]    ${index}   ${type}=kw
    ${kws}=    Get Elements    ${LIBDOC}    xpath=${type}
    ${args}=    Get Elements Texts   ${kws}[${index}]    xpath=arguments/arg
    [Return]    ${args}

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

Keyword Source Should Be
    [Arguments]    ${index}    ${source}    ${xpath}=kw
    ${kws}=    Get Elements    ${LIBDOC}    xpath=${xpath}
    ${source} =    Relative Source    ${source}    %{TEMPDIR}
    Element Attribute Should Be    ${kws}[${index}]    source    ${source}

Keyword Should Not Have Source
    [Arguments]    ${index}    ${xpath}=kw
    ${kws}=    Get Elements    ${LIBDOC}    xpath=${xpath}
    Element Should Not Have Attribute    ${kws}[${index}]    source

Keyword Lineno Should Be
    [Arguments]    ${index}    ${lineno}    ${xpath}=kw
    ${kws}=    Get Elements    ${LIBDOC}    xpath=${xpath}
    Element Attribute Should Be    ${kws}[${index}]    lineno    ${lineno}

Keyword Should Not Have Lineno
    [Arguments]    ${index}    ${xpath}=kw
    ${kws}=    Get Elements    ${LIBDOC}    xpath=${xpath}
    Element Should Not Have Attribute    ${kws}[${index}]    lineno

Keyword Should Be Deprecated
    [Arguments]    ${index}
    ${kws}=    Get Elements    ${LIBDOC}    xpath=kw
    Element Attribute Should be    ${kws}[${index}]    deprecated    true

Keyword Should Not Be Deprecated
    [Arguments]    ${index}
    ${kws}=    Get Elements    ${LIBDOC}    xpath=kw
    Element Should Not Have Attribute    ${kws}[${index}]    deprecated

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
