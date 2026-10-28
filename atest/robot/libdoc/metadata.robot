*** Settings ***
Resource          libdoc_resource.robot
Test Setup        Remove File    ${OUT HTML}

*** Test Cases ***
HTML model
    Run Libdoc And Parse Model From HTML
    ...    --metadata URL:https://example.com ${TESTDATADIR}/module.py
    Should Be Equal    ${MODEL}[metadata][URL]    https://example.com

JSON model
    Run Libdoc And Parse Model From JSON
    ...    --metadata URL:https://example.com ${TESTDATADIR}/module.py
    Should Be Equal    ${MODEL}[metadata][URL]    https://example.com

Multiple metadata
    ${args}=    Catenate    --metadata URL:https://example.com
    ...    --metadata Source:https://github.com/example/lib
    ...    ${TESTDATADIR}/module.py
    Run Libdoc And Parse Model From JSON    ${args}
    Should Be Equal    ${MODEL}[metadata][URL]    https://example.com
    Should Be Equal    ${MODEL}[metadata][Source]    https://github.com/example/lib

Metadata is omitted when not used
    Run Libdoc And Parse Model From JSON    ${TESTDATADIR}/module.py
    Dictionary Should Not Contain Key    ${MODEL}    metadata

XML output and round trip
    Run Libdoc And Parse Output    --metadata URL:https://example.com ${TESTDATADIR}/module.py
    Run Libdoc And Parse Model From JSON    ${OUTXML}
    Should Be Equal    ${MODEL}[metadata][URL]    https://example.com

Metadata value can contain colons
    Run Libdoc And Parse Model From JSON
    ...    --metadata URL:https://example.com:8080/path ${TESTDATADIR}/module.py
    Should Be Equal    ${MODEL}[metadata][URL]    https://example.com:8080/path

Library metadata
    Run Libdoc And Parse Model From JSON    ${TESTDATADIR}/MetadataAttribute.py
    Should Be Equal    ${MODEL}[metadata][Homepage]    https://example.com
    Should Be Equal    ${MODEL}[metadata][License]    Apache-2.0

Metadata from decorator
    Run Libdoc And Parse Model From JSON    ${TESTDATADIR}/Metadata.py
    Should Be Equal    ${MODEL}[metadata][Homepage]    https://example.com
    Should Be Equal    ${MODEL}[metadata][License]    Apache-2.0

CLI metadata is merged with library metadata
    ${args}=    Catenate    --metadata Homepage:https://example.org
    ...    --metadata Generated:yes
    ...    ${TESTDATADIR}/MetadataAttribute.py
    Run Libdoc And Parse Model From JSON    ${args}
    Should Be Equal    ${MODEL}[metadata][Homepage]    https://example.org
    Should Be Equal    ${MODEL}[metadata][License]    Apache-2.0
    Should Be Equal    ${MODEL}[metadata][Generated]    yes

Invalid metadata
    [Template]    Run libdoc and verify error
    --metadata invalid ${TESTDATADIR}/module.py ${OUT HTML}
    ...    Invalid metadata 'invalid'. Metadata must be given in 'name:value' format.
    --metadata :value ${TESTDATADIR}/module.py ${OUT HTML}
    ...    Invalid metadata ':value'. Metadata must be given in 'name:value' format.
    --metadata name: ${TESTDATADIR}/module.py ${OUT HTML}
    ...    Invalid metadata 'name:'. Metadata must be given in 'name:value' format.

*** Keywords ***
Run libdoc and verify error
    [Arguments]    ${args}    @{error}    ${fatal}=True
    IF    ${fatal}
        Run Libdoc And Verify Output    ${args}    @{error}    ${USAGE TIP[1:]}
        File Should Not Exist    ${OUT HTML}
    ELSE
        Run Libdoc And Verify Output    ${args}    @{error}
        File Should Exist    ${OUT HTML}
    END
