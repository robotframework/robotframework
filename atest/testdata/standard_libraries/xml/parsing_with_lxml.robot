*** Settings ***
Suite Setup       Set lxml availability to suite metadata
Library           XML    use_lxml=yes
Resource          xml_resource.robot

*** Test Cases ***
Parse file using forwards slash as path separator
    ${root} =   Parse XML     ${CURDIR}/test.xml
    Should be equal     ${root.tag}     test

Parse file using system path separator
    ${root} =   Parse XML     ${CURDIR}${/}test.xml
    Should be equal     ${root.tag}     test

Parse file using pathlib.Path
    ${root} =   Parse XML     ${{pathlib.Path('${CURDIR}/test.xml')}}
    Should be equal     ${root.tag}     test

Parse string
    ${root} =   Parse XML     <simple>päivää</simple>
    Should be equal     ${root.tag}     simple
    Should be equal     ${root.text}     päivää

Parse string with encoding
    ${root} =   Parse XML     <?xml version="1.0" encoding="UTF-8"?><simple>päivää</simple>
    Should be equal     ${root.tag}     simple
    Should be equal     ${root.text}     päivää
    ${root} =   Parse XML     <?xml version='1.0' encoding='latin1' standalone='yes'?>\n<simple>päivää</simple>\n
    Should be equal     ${root.tag}     simple
    Should be equal     ${root.text}     päivää

Parse bytes
    ${root} =   Run With Bytes
    ...    Parse XML     <simple>päivää</simple>
    Should be equal     ${root.tag}     simple
    Should be equal     ${root.text}     päivää

Parse bytes with encoding
    ${root} =   Run With Bytes
    ...    Parse XML     <?xml version\="1.0" encoding\="UTF-8"?><simple>päivää</simple>
    Should be equal     ${root.tag}     simple
    Should be equal     ${root.text}     päivää
    ${root} =   Run With Bytes
    ...    Parse XML     <?xml version\='1.0' encoding\='latin1' standalone\='yes'?>\n<simple>päivää</simple>\n
    ...    encoding=latin1
    Should be equal     ${root.tag}     simple
    Should be equal     ${root.text}     päivää

Comments and processing instructions are removed
    ${xml} =    Catenate    SEPARATOR=\n
    ...    <!-- comment node -->
    ...    <?pi node?>
    ...    <root><!--c-->
    ...    <child id="1"/><?p?><child id="2"/>
    ...    </root>
    ...    <!--c--><?x?>
    Elements should be equal     ${xml}    <root>\n<child id="1"/><child id="2"/>\n</root>

Parse invalid file
    [Documentation]    FAIL GLOB: *Error: *
    Parse XML    ${CURDIR}${/}parsing.txt

Parse invalid string
    [Documentation]    FAIL GLOB: *Error: *
    Parse XML    <kekkonen>urho

Parse non-existing file
    [Documentation]    FAIL REGEXP: (IOError|FileNotFoundError|OSError): .*
    Parse XML    non-existing.xml
