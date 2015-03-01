*** Settings ***
Library           XML
Resource          xml_resource.robot

*** Test Cases ***
Parse file using forwards slash as path separator
    ${root} =   Parse XML     ${CURDIR}/test.xml
    Should be equal     ${root.tag}     test

Parse file using system path separator
    ${root} =   Parse XML     ${CURDIR}${/}test.xml
    Should be equal     ${root.tag}     test

Parse string
    ${root} =   Parse XML     <simple>päivää</simple>
    Should be equal     ${root.tag}     simple
    Should be equal     ${root.text}     päivää

Parse invalid file
    [Documentation]    FAIL GLOB: *Error: *
    Parse XML    ${CURDIR}${/}parsing.txt

Parse invalid string
    [Documentation]    FAIL GLOB: *Error: *
    Parse XML    <kekkonen>urho

Parse non-existing file
    [Documentation]    FAIL REGEXP: (IO|FileNotFound)Error: .*
    Parse XML    non-existing.xml
