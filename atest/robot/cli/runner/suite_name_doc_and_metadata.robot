*** Settings ***
Resource          cli_resource.robot

*** Test Cases ***
Default Name, Doc & Metadata
    Run tests    ${EMPTY}    ${TESTFILE}
    Check Names    ${SUITE}    Normal
    Check Names    ${SUITE.tests[0]}    First One    Normal.
    Check Names    ${SUITE.tests[1]}    Second One    Normal.
    Should Be Equal    ${SUITE.doc}    Normal test cases
    Should Be Equal    ${SUITE.metadata['Something']}    My Value

Overriding Name, Doc & Metadata And Escaping
    ${options} =    Catenate
    ...    -l log.html
    ...    -N this_is_overridden_next
    ...    --name "my COOL Name.!!."
    ...    --doc "Even \\cooooler\\ doc!?"
    ...    --metadata something:new
    ...    --metadata "Two Parts:three part VALUE"
    ...    -M path:c:\\temp\\new.txt
    ...    -M esc:*?$&#!!
    Run Tests    ${options}    ${TESTFILE}
    Check Names    ${SUITE}    my COOL Name.!!.
    Check Names    ${SUITE.tests[0]}    First One    my COOL Name.!!..
    Check Names    ${SUITE.tests[1]}    Second One    my COOL Name.!!..
    Should Be Equal    ${SUITE.doc}    Even \\cooooler\\ doc!?
    Should Be Equal    ${SUITE.metadata['Something']}    new
    Should Be Equal    ${SUITE.metadata['Two Parts']}    three part VALUE
    Should Be Equal    ${SUITE.metadata['path']}    c:\\temp\\new.txt
    Should Be Equal    ${SUITE.metadata['esc']}    *?$&#!!
    File Should Contain    ${OUTDIR}/log.html    Something
    File Should Not Contain    ${OUTDIR}/log.html    something
