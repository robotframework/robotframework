*** Settings ***
Resource          rebot_cli_resource.robot

*** Test Cases ***
Default Name, Doc & Metadata
    [Documentation]    Using default values (read from xml) for name, doc and metadata.
    Run Rebot    ${EMPTY}    ${INPUT FILE}
    Check Names    ${SUITE}    Normal
    Check Names    ${SUITE.tests[0]}    First One    Normal.
    Check Names    ${SUITE.tests[1]}    Second One    Normal.
    Should Be Equal    ${SUITE.doc}    Normal test cases
    Should Be Equal    ${SUITE.metadata['Something']}    My Value

Overriding Name, Doc & Metadata And Escaping
    [Documentation]    Overriding name, doc and metadata. Also tests escaping values.
    ${options} =    Catenate
    ...    -N this_is_overridden_next
    ...    --name "my COOL Name!!"
    ...    --doc "Even \\cooooler\\ doc!?"
    ...    --metadata something:New
    ...    --metadata "two parts:three parts here"
    ...    -M path:c:\\temp\\new.txt
    ...    -M esc:*?$&#!!
    Run Rebot    ${options}    ${INPUT FILE}
    Check Names    ${SUITE}    my COOL Name!!
    Check Names    ${SUITE.tests[0]}    First One    my COOL Name!!.
    Check Names    ${SUITE.tests[1]}    Second One    my COOL Name!!.
    Should Be Equal    ${SUITE.doc}    Even \\cooooler\\ doc!?
    Should Be Equal    ${SUITE.metadata['Something']}    New
    Should Be Equal    ${SUITE.metadata['two parts']}    three parts here
    Should Be Equal    ${SUITE.metadata['path']}    c:\\temp\\new.txt
    Should Be Equal    ${SUITE.metadata['esc']}    *?$&#!!
