*** Settings ***
Resource          cli_resource.robot

*** Test Cases ***
Default Name, Doc & Metadata
    Run Tests    ${EMPTY}    ${TESTFILE}
    Check All Names    ${SUITE}    Normal
    Should Be Equal    ${SUITE.doc}    Normal test cases
    Should Be Equal    ${SUITE.metadata['Something']}    My Value

Overriding Name, Doc & Metadata And Escaping
    ${options} =    Catenate
    ...    -l log.html
    ...    -N this_is_overridden_next
    ...    --name "my COOL Name.!!."
    ...    --doc "Even \\cooooler\\ doc!?"
    ...    --metadata something:new!
    ...    --metadata "Two Parts:three part VALUE"
    ...    -M path:c:\\temp\\new.txt
    ...    -M esc:*?$&#!!
    Run Tests    ${options}    ${TESTFILE}
    Check All Names    ${SUITE}    my COOL Name.!!.
    Should Be Equal    ${SUITE.doc}    Even \\cooooler\\ doc!?
    Should Be Equal    ${SUITE.metadata['Something']}    new!
    Should Be Equal    ${SUITE.metadata['Two Parts']}    three part VALUE
    Should Be Equal    ${SUITE.metadata['path']}    c:\\temp\\new.txt
    Should Be Equal    ${SUITE.metadata['esc']}    *?$&#!!
    File Should Contain    ${OUTDIR}/log.html    Something
    File Should Not Contain    ${OUTDIR}/log.html    something

Documentation and metadata from external file
    ${path} =    Normalize Path    ${DATADIR}/cli/runner/doc.txt
    ${value} =    Get File    ${path}
    Run Tests    --doc ${path} --metadata name:${path}    ${TEST FILE}
    Check All Names    ${SUITE}    Normal
    Should Be Equal    ${SUITE.doc}    ${value.rstrip()}
    Should Be Equal    ${SUITE.metadata['name']}    ${value.rstrip()}
    Run Tests    --doc " ${path}" --metadata "name: ${path}" -M dir:%{TEMPDIR}    ${TEST FILE}
    Check All Names    ${SUITE}    Normal
    Should Be Equal    ${SUITE.doc}    ${path}
    Should Be Equal    ${SUITE.metadata['name']}    ${path}
    Should Be Equal    ${SUITE.metadata['dir']}    %{TEMPDIR}

Invalid external file
    [Tags]    no-windows
    ${path} =    Normalize Path    %{TEMPDIR}/file.txt
    Create File    ${path}
    Evaluate    os.chmod('${path}', 0)
    Run Tests Without Processing Output    --doc ${path}    ${TEST FILE}
    Stderr Should Match    [[] ERROR []] Invalid value for option '--doc': Reading documentation from '${path}' failed: *${USAGE TIP}\n
    [Teardown]    Remove File    ${path}

*** Keywords ***
Check All Names
    [Arguments]    ${suite}    ${name}
    Check Names    ${suite}    ${name}
    Check Names    ${suite.tests[0]}    First One    ${name}.
    Check Names    ${suite.tests[1]}    Second One    ${name}.
