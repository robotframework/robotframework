*** Settings ***
Library            Collections
Library            OperatingSystem
Library            String

*** Variables ***
${TEST} =          ${CURDIR}/test.xml
${NS} =            ${CURDIR}/namespaces.xml
${NO NS IN NS} =   <ns:root xmlns:ns="uri"><no><ns:yes><no>.</no></ns:yes></no></ns:root>
${SIMPLE} =        <root><child id="1">text</child><c2><gc /></c2></root>
${ATTR NS} =       <root id="1" p:id="2" xmlns:p="xxx" />
${OUTPUT} =        %{TEMPDIR}/xmllib.xml
${INDENT} =        ${SPACE * 4}

*** Keywords ***
Get Etree Version
    ${et} =    Evaluate    robot.utils.ET    modules=robot
    RETURN    ${et.VERSION}

Run With Bytes
    [Arguments]    ${kw}    ${string}    @{args}    ${encoding}=UTF-8    &{kws}
    ${bytes} =    Encode string to bytes    ${string}    ${encoding}
    ${result} =    Run Keyword    ${kw}    ${bytes}    @{args}    &{kws}
    RETURN    ${result}

Parse XML To Test Variable
    [Arguments]    ${input}    ${var}    &{config}
    ${result} =    Parse XML    ${input}    &{config}
    Set Test Variable    ${var}    ${result}

Element Should Have Attributes
    [Arguments]    ${source}    ${xpath}    &{expected}
    ${elem} =    Get Element    ${source}    ${xpath}
    Dictionaries Should Be Equal    ${elem.attrib}    ${expected}

Saved XML Should Equal
    [Arguments]    ${tree}    @{expected}
    Remove File    ${OUTPUT}
    Save XML    ${tree}    ${OUTPUT}
    ${expected} =    Catenate    SEPARATOR=\n    @{expected}
    XML Content Should Be    ${expected}

Saved XML Should Equal File
    [Arguments]    ${tree}    ${expected}
    Remove File    ${OUTPUT}
    Save XML    ${tree}    ${OUTPUT}
    ${content} =    Get File    ${OUTPUT}
    ${content} =    Split To Lines    ${content}
    ${expected} =    Get File    ${expected}
    ${expected} =    Split To Lines    ${expected}
    Lists Should Be Equal    ${content}    ${expected}

Run Keyword Depending On Etree Version
    [Arguments]    ${etree 1.3 keyword}    ${etree 1.2 keyword}=No Operation
    ${version} =    Get Etree Version
    @{result} =    Run Keyword If    "${version}" >= "1.3"
    ...    ${etree 1.3 keyword}
    ...    ELSE
    ...    ${etree 1.2 keyword}
    RETURN    @{result}

Test Attribute Namespace Parsing
     [Arguments]    ${elem}
     Element Attribute Should Be    ${elem}    id    1
     Element Attribute Should Be    ${elem}    {xxx}id    2
     ${version} =    Get Etree Version
     ${expected} =    Set Variable If    "${version}" >= "1.3"
     ...    <root xmlns:ns0="xxx" id="1" ns0:id="2" />
     ...    <root id="1" ns0:id="2" xmlns:ns0="xxx" />
     Saved XML Should Equal    ${elem}    ${expected}
     Elements Should Be Equal    ${elem}    ${OUTPUT}

Test Attribute Namespace Parsing With lxml
     [Arguments]    ${elem}
     Element Attribute Should Be    ${elem}    id    1
     Element Attribute Should Be    ${elem}    {xxx}id    2
     Saved XML Should Equal    ${elem}    <root xmlns:p="xxx" id="1" p:id="2"/>
     Elements Should Be Equal    ${elem}    ${OUTPUT}

Set lxml availability to suite metadata
     ${lib} =    Get Library Instance    XML
     Set Suite Metadata    lxml    ${lib.lxml_etree}

XML Content Should Be
    [Arguments]    ${expected}    ${encoding}=UTF-8
    ${actual} =    Get File    ${OUTPUT}    ${encoding}
    @{actual} =    Split To Lines    ${actual}
    ${expected} =    Split To Lines    ${expected}
    Should Be Equal    ${actual[0].lower()}    <?xml version='1.0' encoding='${encoding.lower()}'?>
    Lists Should Be Equal    ${actual[1:]}    ${expected}

Remove Output File
    Remove File    ${OUTPUT}
