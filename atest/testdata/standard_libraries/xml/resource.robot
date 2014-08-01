*** Settings ***
Library            Collections
Library            OperatingSystem
Library            String

*** Variables ***
${TEST} =          ${CURDIR}/test.xml
${NS} =            ${CURDIR}/namespaces.xml
${DEFAULT NS} =    ${CURDIR}/default_namespaces.xml
${SIMPLE} =        <root><child id="1">text</child><c2><gc /></c2></root>
${ATTR NS} =       <root id="1" p:id="2" xmlns:p="xxx" />
${OUTPUT} =        %{TEMPDIR}/xmllib.xml
${INDENT} =        ${SPACE * 4}

*** Keywords ***
Get Etree Version
    ${et} =    Evaluate    robot.utils.ET    modules=robot
    [Return]    ${et.VERSION}

Parse XML To Test Variable
    [Arguments]    ${input}    ${var}    ${etree namespaces}=
    ${result} =    Parse XML    ${input}    ${etree namespaces}
    Set Test Variable    ${var}    ${result}

Element Should Have Attributes
    [Arguments]    ${source}    ${xpath}    @{attributes}
    ${elem} =    Get Element    ${source}    ${xpath}
    ${expected} =    Create Dictionary    @{attributes}
    Dictionaries Should Be Equal    ${elem.attrib}    ${expected}

Saved XML Should Equal
    [Arguments]    ${tree}    @{expected}
    Save XML    ${tree}    ${OUTPUT}
    ${content} =    Get File    ${OUTPUT}
    ${content} =    Split To Lines    ${content}
    ${expected} =    Catenate    SEPARATOR=\n
    ...    <?xml version='1.0' encoding='UTF-8'?>    @{expected}
    ${expected} =    Split To Lines    ${expected}
    Lists Should Be Equal    ${content}    ${expected}

Saved XML Should Equal File
    [Arguments]    ${tree}    ${expected}
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
    [Return]    @{result}

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
