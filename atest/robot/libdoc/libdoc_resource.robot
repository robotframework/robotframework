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
    Validate XML Spec    ${OUTXML}
    ${LIBDOC}=    Parse Xml    ${OUTXML}
    Set Suite Variable    ${LIBDOC}

Run Libdoc And Verify Output
    [Arguments]    ${args}    @{expected}
    VAR    ${expected}    @{expected}    separator=\n
    ${output}=    Run Libdoc    ${args}
    Should Match    ${output}   ${expected}\n

Run Libdoc And Parse Model From HTML
    [Arguments]    ${args}
    Run Libdoc    ${args} ${OUTHTML}
    ${MODEL} =    Get Libdoc Model From HTML    ${OUTHTML}
    Set Suite Variable    ${MODEL}

Run Libdoc And Parse Model From JSON
    [Arguments]    ${args}
    Run Libdoc    ${args} ${OUTJSON}
    Validate JSON spec    ${OUTJSON}
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
    [Arguments]    ${scope}
    Element Attribute Should Be    ${LIBDOC}    scope    ${scope}

Source Should Be
    [Arguments]    ${source}
    ${source} =    Normalize Path    ${source}
    Element Attribute Should Be    ${LIBDOC}    source    ${source}

Lineno Should Be
    [Arguments]    ${lineno}
    Element Attribute Should Be    ${LIBDOC}    lineno    ${lineno}

Generated Should Be Defined
    # For example, '1970-01-01T00:00:01+00:00'.
    Element Attribute Should Match    ${LIBDOC}    generated    ????-??-??T??:??:?????:??

Generated Should Be
    [Arguments]    ${generated}
    Generated Should Be Defined
    Element Attribute Should Be    ${LIBDOC}    generated    ${generated}

Spec version should be correct
    Element Attribute Should Be    ${LIBDOC}    specversion    6

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
    FOR    ${arg_elem}    ${exp_repr}    IN ZIP     ${arg_elems}    ${expected}    mode=STRICT
        IF    $INTERPRETER.version_info >= (3, 11)
            ${exp_repr} =    Replace String    ${exp_repr}    | None = None    = None
        END
        ${kind}=        Get Element Attribute        ${arg_elem}    kind
        ${required}=    Get Element Attribute        ${arg_elem}    required
        ${repr}=        Get Element Attribute        ${arg_elem}    repr
        ${name}=        Get Element Optional Text    ${arg_elem}    name
        ${types}=       Get Elements                 ${arg_elem}    type
        IF    not $types
            ${type}=    Set Variable                 ${None}
        ELSE IF    len($types) == 1
            ${type}=    Get Type                     ${types}[0]
        ELSE
            Fail        Cannot have more than one <type> element
        END
        ${default}=     Get Element Optional Text    ${arg_elem}    default
        ${arg_model}=    Create Dictionary
        ...    kind=${kind}
        ...    name=${name}
        ...    type=${type}
        ...    default=${default}
        ...    repr=${repr}
        Verify Argument Model    ${arg_model}    ${exp_repr}
        Should Be Equal    ${repr}    ${exp_repr}
    END

Return Type Should Be
    [Arguments]    ${index}    ${name}    @{nested}
    ${kws}=    Get Elements    ${LIBDOC}    xpath=keywords/kw
    VAR    ${kw}    ${kws}[${index}]
    IF    $name.upper() == 'NONE'
        Element Should Not Exist    ${kw}    returntype
        RETURN
    END
    Element Attribute Should Be    ${kw}    name    ${name}    xpath=returntype
    ${type_elems} =    Get Elements    ${kw}    returntype/type
    FOR    ${elem}    ${expected}    IN ZIP    ${type_elems}    ${nested}    mode=STRICT
        Element Attribute Should Be    ${elem}    name    ${expected}
    END

Get Type
    [Arguments]    ${elem}
    ${children} =    Get Elements    ${elem}    type
    ${nested} =    Create List
    FOR    ${child}    IN    @{children}
        ${type} =    Get Type    ${child}
        Append To List    ${nested}    ${type}
    END
    ${type} =    Get Element Attribute    ${elem}    name
    IF    $elem.get('union') == 'true'
        ${type} =    Catenate    SEPARATOR=${SPACE}|${SPACE}    @{nested}
    ELSE IF    $nested
        ${args} =    Catenate    SEPARATOR=,${SPACE}    @{nested}
        ${type} =    Set Variable    ${type}\[${args}]
    END
    RETURN    ${type}

Get Element Optional Text
    [Arguments]    ${source}    ${xpath}
    ${elems}=    Get Elements    ${source}    ${xpath}
    ${text}=    IF    len($elems) == 1    Get Element Text    ${elems}[0]
    RETURN    ${text}

Verify Argument Model
    [Arguments]    ${arg_model}    ${expected_repr}    ${json}=False
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
    ${text}=    Get Element Text    ${kws}[${index}]    xpath=doc
    Should Start With    ${text}    ${doc}

Keyword Doc Should Be
    [Arguments]    ${index}    @{doc}
    ${kws}=   Get Elements    ${LIBDOC}    xpath=keywords/kw
    ${doc}=    Catenate     SEPARATOR=\n    @{doc}
    Element Text Should Be    ${kws}[${index}]    ${doc}    xpath=doc

Keyword Shortdoc Should Be
    [Arguments]    ${index}    @{doc}
    ${kws}=   Get Elements    ${LIBDOC}    xpath=keywords/kw
    ${doc}=    Catenate     SEPARATOR=\n    @{doc}
    Element Text Should Be    ${kws}[${index}]    ${doc}    xpath=shortdoc

Keyword Tags Should Be
    [Arguments]    ${index}    @{expected}
    ${kws}=    Get Elements    ${LIBDOC}    xpath=keywords/kw
    ${tags}=   Get Elements Texts    ${kws}[${index}]    xpath=tags/tag
    Should Be Equal    ${tags}    ${expected}

Specfile Tags Should Be
    [Arguments]    @{expected}
    ${tags}=    Get Elements Texts    ${LIBDOC}    xpath=tags/tag
    Should Be Equal    ${tags}    ${expected}

Keyword Source Should Be
    [Arguments]    ${index}    ${source}    ${xpath}=keywords/kw
    ${kws}=    Get Elements    ${LIBDOC}    xpath=${xpath}
    ${source} =    Normalize Path    ${source}
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

Keyword Should Be Private
    [Arguments]    ${index}
    ${kws}=    Get Elements    ${LIBDOC}    xpath=keywords/kw
    Element Attribute Should be    ${kws}[${index}]    private    true

Keyword Should Not Be Private
    [Arguments]    ${index}
    ${kws}=    Get Elements    ${LIBDOC}    xpath=keywords/kw
    Element Should Not Have Attribute    ${kws}[${index}]    private

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
    [Arguments]    ${actual}    @{expected}    ${start}=False
    ${expected} =    Catenate    SEPARATOR=\n    @{expected}
    IF    not ${start}
        Should Be Equal As Strings    ${actual}    ${expected}
    ELSE
        Should Start With    ${actual}    ${expected}
    END

List of Dict Should Be Equal
    [Arguments]    ${list1}    ${list2}
    FOR    ${dict1}    ${dict2}    IN ZIP    ${list1}    ${list2}
        Dictionaries Should Be Equal    ${dict1}    ${dict2}
    END

DataType Enum Should Be
    [Arguments]    ${index}    ${name}    ${doc}    @{exp_members}
    ${enums}=   Get Elements    ${LIBDOC}   xpath=typedocs/type[@type='Enum']
    Element Attribute Should Be    ${enums}[${index}]     name   ${name}
    Element Text Should Be    ${enums}[${index}]     ${doc}    xpath=doc
    ${members}=    Get Elements    ${enums}[${index}]    xpath=members/member
    FOR   ${member}    ${exp_member}    IN ZIP    ${members}    ${exp_members}
        ${attrs}=    Get Element Attributes    ${member}
        Element Attribute Should Be    ${member}    name     ${{${exp_member}}}[name]
        Element Attribute Should Be    ${member}    value    ${{${exp_member}}}[value]
    END

DataType TypedDict Should Be
    [Arguments]    ${index}    ${name}    ${doc}    @{exp_items}
    ${dicts}=   Get Elements    ${LIBDOC}   xpath=typedocs/type[@type='TypedDict']
    Element Attribute Should Be    ${dicts}[${index}]     name   ${name}
    Element Text Should Be    ${dicts}[${index}]     ${doc}    xpath=doc
    ${items}=    Get Elements    ${dicts}[${index}]    xpath=items/item
    FOR   ${exp_item}    IN    @{exp_items}
        ${exp}=    Evaluate    json.loads($exp_item)
        FOR    ${item}    IN    @{items}
            ${cur}=    Get Element Attributes    ${item}
            IF    $cur['key'] == $exp['key']
                Should Be Equal    ${cur}[key]     ${exp}[key]
                Should Be Equal    ${cur}[type]    ${exp}[type]
                IF    'required' in $exp
                    Should Be Equal    ${cur}[required]    ${exp}[required]
                END
                BREAK
            END
        END
    END

DataType Custom Should Be
    [Arguments]    ${index}    ${name}    ${doc}
    ${types}=   Get Elements    ${LIBDOC}   xpath=typedocs/type[@type='Custom']
    Element Attribute Should Be    ${types}[${index}]     name      ${name}
    Element Text Should Be         ${types}[${index}]     ${doc}    xpath=doc

DataType Standard Should Be
    [Arguments]    ${index}    ${name}    ${doc}
    ${types}=   Get Elements    ${LIBDOC}   xpath=typedocs/type[@type='Standard']
    Element Attribute Should Be    ${types}[${index}]     name       ${name}
    Element Text Should Match      ${types}[${index}]     ${doc}*    xpath=doc

Usages Should Be
    [Arguments]    ${index}    ${type}    ${name}    @{expected}
    ${elem} =    Get Element    ${LIBDOC}   xpath=typedocs/type[${{${index} + 1}}]
    Element Attribute Should Be    ${elem}    type    ${type}
    Element Attribute Should Be    ${elem}    name    ${name}
    @{usages} =    Get Elements    ${elem}    usages/usage
    Should Be Equal    ${{len($usages)}}    ${{len($expected)}}
    FOR    ${usage}    ${kw}    IN ZIP    ${usages}    ${expected}
        Element Text Should Be    ${usage}    ${kw}
    END

Accepted Types Should Be
    [Arguments]    ${index}    ${type}    ${name}    @{expected}
    ${elem} =    Get Element    ${LIBDOC}   xpath=typedocs/type[${{${index} + 1}}]
    Element Attribute Should Be    ${elem}    type    ${type}
    Element Attribute Should Be    ${elem}    name    ${name}
    @{accepts} =    Get Elements    ${elem}    accepts/type
    Should Be Equal    ${{len($accepts)}}    ${{len($expected)}}
    FOR    ${acc}    ${type}    IN ZIP    ${accepts}    ${expected}
        Element Text Should Be    ${acc}    ${type}
    END

Typedoc links should be
    [Arguments]    ${kw}    ${arg}    ${typedoc}    @{nested typedocs}
    ${type} =    Get Element    ${LIBDOC}    keywords/kw[${${kw} + 1}]/arguments/arg[${${arg} + 1}]/type
    Typedoc link should be    ${type}    ${typedoc}
    ${nested} =    Get Elements    ${type}    type
    Length Should Be    ${nested}    ${{len($nested_typedocs)}}
    FOR    ${type}    ${typedoc}    IN ZIP    ${nested}    ${nested typedocs}
        Typedoc link should be    ${type}    ${typedoc}
    END

Typedoc link should be
    [Arguments]    ${type}    ${typedoc}
    IF    ':' in $typedoc
        ${typename}    ${typedoc} =    Split String    ${typedoc}    :
    ELSE
        ${typename} =    Set Variable    ${typedoc}
    END
    Element Attribute Should Be    ${type}    name       ${typename}
    Element Attribute Should Be    ${type}    typedoc    ${{$typedoc or None}}
