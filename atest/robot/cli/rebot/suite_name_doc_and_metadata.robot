*** Settings ***
Resource          rebot_cli_resource.robot

*** Test Cases ***
Default Name, Doc & Metadata
    [Documentation]    Using default values (read from xml) for name, doc and metadata.
    Run Rebot    ${EMPTY}    ${INPUT FILE}
    Check All Names    ${SUITE}    Normal
    Should Be Equal    ${SUITE.doc}    Normal test cases
    Should Be Equal    ${SUITE.metadata['Something']}    My Value

Overriding Name, Doc & Metadata And Escaping
    [Documentation]    Overriding name, doc and metadata. Also tests escaping values.
    ${options} =    Catenate
    ...    -N this_is_overridden_next
    ...    --name "my COOL Name.!!."
    ...    --doc "Even \\cooooler\\ doc!?"
    ...    --metadata something:New!
    ...    --metadata "two parts:three parts here"
    ...    -M path:c:\\temp\\new.txt
    ...    -M esc:*?$&#!!
    Run Rebot    ${options}    ${INPUT FILE}
    Check All Names    ${SUITE}    my COOL Name.!!.
    Should Be Equal    ${SUITE.doc}    Even \\cooooler\\ doc!?
    Should Be Equal    ${SUITE.metadata['Something']}    New!
    Should Be Equal    ${SUITE.metadata['two parts']}    three parts here
    Should Be Equal    ${SUITE.metadata['path']}    c:\\temp\\new.txt
    Should Be Equal    ${SUITE.metadata['esc']}    *?$&#!!

Documentation and metadata from external file
    ${path} =    Normalize Path    ${DATADIR}/cli/runner/doc.txt
    ${value} =    Get File    ${path}
    Run Rebot    --doc ${path} --metadata name:${path}    ${INPUT FILE}
    Check All Names    ${SUITE}    Normal
    Should Be Equal    ${SUITE.doc}    ${value.rstrip()}
    Should Be Equal    ${SUITE.metadata['name']}    ${value.rstrip()}
    Run Rebot    --doc " ${path}" --metadata "name: ${path}" -M dir:.    ${INPUT FILE}
    Check All Names    ${SUITE}    Normal
    Should Be Equal    ${SUITE.doc}    ${path}
    Should Be Equal    ${SUITE.metadata['name']}    ${path}
    Should Be Equal    ${SUITE.metadata['dir']}    .

Invalid external file
    [Tags]    no-windows
    ${path} =    Normalize Path    %{TEMPDIR}/file.txt
    Create File    ${path}
    Evaluate    os.chmod('${path}', 0)
    Run Rebot Without Processing Output    --doc ${path}    ${INPUT FILE}
    Stderr Should Match    [[] ERROR []] Invalid value for option '--doc': Reading documentation from '${path}' failed: *${USAGE TIP}\n
    [Teardown]    Remove File    ${path}

*** Keywords ***
Check All Names
    [Arguments]    ${suite}    ${name}
    Check Names    ${suite}    ${name}
    Check Names    ${suite.tests[0]}    First One    ${name}.
    Check Names    ${suite.tests[1]}    Second One    ${name}.
