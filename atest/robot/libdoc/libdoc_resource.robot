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
${OUTJSON}        ${OUTBASE}.json
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
    Run Libdoc    ${args} ${OUTHTML}
    ${MODEL} =    Get Libdoc Model From HTML    ${OUTHTML}
    Set Suite Variable    ${MODEL}

Run Libdoc And Parse Model From JSON
    [Arguments]    ${args}
    Run Libdoc    ${args} ${OUTJSON}
    ${model_string}=    Get File    ${OUTJSON}
    ${MODEL} =    Evaluate    json.loads($model_string)
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
    Element Attribute Should Be    ${LIBDOC}    specversion    3

Should Have No Init
    ${inits} =    Get Elements    ${LIBDOC}    xpath=inits/init
    Should Be Empty    ${inits}

Init Doc Should Start With
    [Arguments]    ${index}    @{doc}
    ${inits}=   Get Elements    ${LIBDOC}   xpath=inits/init
    ${doc}=    Catenate     SEPARATOR=    @{doc}
    ${text} =    Get Element Text    ${inits}[${index}]    xpath=doc
    Should Start With    ${text}    ${doc}

Init Doc Should Be
    [Arguments]    ${index}    @{doc}
    ${kws}=   Get Elements    ${LIBDOC}    xpath=inits/init
    ${doc}=    Catenate     SEPARATOR=    @{doc}
    Element Text Should Be    ${kws}[${index}]    ${doc}    xpath=doc

Init Arguments Should Be
    [Arguments]    ${index}   @{expected}
    Verify Arguments Structure    ${index}    inits/init    ${expected}

Keyword Name Should Be
    [Arguments]    ${index}   ${name}
    ${elements}=   Get Elements    ${LIBDOC}    xpath=keywords/kw
    Element Attribute Should Be    ${elements}[${index}]    name    ${name}

Keyword Arguments Should Be
    [Arguments]    ${index}    @{expected}
    Verify Arguments Structure    ${index}    keywords/kw    ${expected}

Verify Arguments Structure
    [Arguments]    ${index}   ${xpath}    ${expected}
    ${kws}=    Get Elements    ${LIBDOC}    xpath=${xpath}
    ${arg_elems}=    Get Elements    ${kws}[${index}]    xpath=arguments/arg
    FOR    ${arg_elem}    ${exp_repr}    IN ZIP     ${arg_elems}    ${expected}
        ${kind}=        Get Element Attribute        ${arg_elem}    kind
        ${required}=    Get Element Attribute        ${arg_elem}    required
        ${repr}=        Get Element Attribute        ${arg_elem}    repr
        ${name}=        Get Element Optional Text    ${arg_elem}    name
        ${type}=       Get Element List Texts       ${arg_elem}    type
        ${default}=     Get Element Optional Text    ${arg_elem}    default
        ${arg_model}=    Create Dictionary
        ...    kind=${kind}
        ...    name=${name}
        ...    type=${type}
        ...    default=${default}
        ...    repr=${repr}
        Run Keyword And Continue On Failure
        ...    Verify Argument Model    ${arg_model}    ${exp_repr}
        Run Keyword And Continue On Failure
        ...    Should Be Equal    ${repr}    ${exp_repr}
    END
    Should Be True    len($arg_elems) == len($expected)

Get Element List Texts
    [Arguments]    ${source}    ${xpath}
    ${elem}=    Get Elements    ${source}    ${xpath}
    Return From Keyword If    len($elem) == 0    @{EMPTY}
    ${texts}    Create List
    FOR    ${element}    IN    @{elem}
        ${text}    Get Element Text    ${element}
        Append To List    ${texts}    ${text}
    END
    [Return]    ${texts}

Get Element Optional Text
    [Arguments]    ${source}    ${xpath}
    ${elem}=    Get Elements    ${source}    ${xpath}
    ${text}=    Run Keyword If    len($elem) == 1
    ...   Get Element Text    ${elem}[0]    .
    ...   ELSE   Set Variable   ${NONE}
    [Return]    ${text}

Verify Argument Model
    [Arguments]    ${arg_model}    ${expected_repr}    ${json}=False
    Log  ${arg_model}
    IF    ${json}
        ${repr}=   Get Repr From Json Arg Model    ${arg_model}
    ELSE
        ${repr}=   Get Repr From Arg Model    ${arg_model}
    END
    Should Be Equal As Strings    ${repr}    ${expected_repr}
    Should Be Equal As Strings    ${arg_model}[repr]    ${expected_repr}

Keyword Doc Should Start With
    [Arguments]    ${index}    @{doc}
    ${kws}=   Get Elements    ${LIBDOC}   xpath=keywords/kw
    ${doc}=    Catenate     SEPARATOR=\n    @{doc}
    ${text} =    Get Element Text    ${kws}[${index}]    xpath=doc
    Should Start With    ${text}    ${doc}

Keyword Doc Should Be
    [Arguments]    ${index}    @{doc}
    ${kws}=   Get Elements    ${LIBDOC}    xpath=keywords/kw
    ${doc}=    Catenate     SEPARATOR=\n    @{doc}
    Element Text Should Be    ${kws}[${index}]    ${doc}    xpath=doc

Keyword Tags Should Be
    [Arguments]    ${index}    @{expected}
    ${kws}=    Get Elements    ${LIBDOC}    xpath=keywords/kw
    ${tags}=   Get Elements Texts    ${kws}[${index}]    xpath=tags/tag
    Should Be Equal    ${tags}    ${expected}

Keyword Source Should Be
    [Arguments]    ${index}    ${source}    ${xpath}=keywords/kw
    ${kws}=    Get Elements    ${LIBDOC}    xpath=${xpath}
    ${source} =    Relative Source    ${source}    %{TEMPDIR}
    Element Attribute Should Be    ${kws}[${index}]    source    ${source}

Keyword Should Not Have Source
    [Arguments]    ${index}    ${xpath}=keywords/kw
    ${kws}=    Get Elements    ${LIBDOC}    xpath=${xpath}
    Element Should Not Have Attribute    ${kws}[${index}]    source

Keyword Lineno Should Be
    [Arguments]    ${index}    ${lineno}    ${xpath}=keywords/kw
    ${kws}=    Get Elements    ${LIBDOC}    xpath=${xpath}
    Element Attribute Should Be    ${kws}[${index}]    lineno    ${lineno}

Keyword Should Not Have Lineno
    [Arguments]    ${index}    ${xpath}=keywords/kw
    ${kws}=    Get Elements    ${LIBDOC}    xpath=${xpath}
    Element Should Not Have Attribute    ${kws}[${index}]    lineno

Keyword Should Be Deprecated
    [Arguments]    ${index}
    ${kws}=    Get Elements    ${LIBDOC}    xpath=keywords/kw
    Element Attribute Should be    ${kws}[${index}]    deprecated    true

Keyword Should Not Be Deprecated
    [Arguments]    ${index}
    ${kws}=    Get Elements    ${LIBDOC}    xpath=keywords/kw
    Element Should Not Have Attribute    ${kws}[${index}]    deprecated

Keyword Count Should Be
    [Arguments]    ${expected}   ${type}=keywords/kw
    ${kws}=    Get Elements    ${LIBDOC}    xpath=${type}
    Length Should Be    ${kws}    ${expected}

Remove Output Files
    Remove Files    ${OUTBASE}*

Should Be Equal Multiline
    [Arguments]    ${actual}    @{expected}
    ${expected} =    Catenate    SEPARATOR=\n    @{expected}
    Should Be Equal As Strings    ${actual}    ${expected}

List of Dict Should Be Equal
    [Arguments]    ${list1}    ${list2}
    FOR    ${dict1}    ${dict2}    IN ZIP    ${list1}    ${list2}
        Dictionaries Should Be Equal    ${dict1}    ${dict2}
    END
