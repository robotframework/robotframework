*** Settings ***
Resource          data_formats/formats_resource.robot

*** Variables ***
${PARSING}            ${DATADIR}/parsing
${SUITE DIR}          %{TEMPDIR}/tmp

*** Test Cases ***
Directory Containing No Test Cases
    Run tests and check error
    ...    ${PARSING}/notests
    ...    Suite 'Notests' contains no tests or tasks.

File Containing No Test Cases
    Run tests and check error
    ...    ${PARSING}/empty_testcase_table.robot
    ...    Suite 'Empty Testcase Table' contains no tests or tasks.

Empty File
    Run tests and check error
    ...    ${ROBOTDIR}/empty.robot
    ...    Suite 'Empty' contains no tests or tasks.

Multisource Containing Empty File
    Run tests and check error
    ...    ${ROBOTDIR}/empty.robot ${ROBOTDIR}/sample.robot
    ...    Suite 'Empty' contains no tests or tasks.

Multisource With Empty Directory
    Run tests and check error
    ...    ${ROBOTDIR}/sample.robot ${PARSING}/notests
    ...    Suite 'Notests' contains no tests or tasks.

Multisource Containing Empty File With Non-standard Extension
    Run tests and check error
    ...    ${PARSING}/unsupported.log ${ROBOTDIR}/sample.robot
    ...    Suite 'Unsupported' contains no tests or tasks.

File With Invalid Encoding
    Run tests and check parsing error
    ...    ${PARSING}/invalid_encoding/invalid_encoding.robot
    ...    UnicodeDecodeError: .*
    ...    ${PARSING}/invalid_encoding/invalid_encoding.robot

Directory Containing File With Invalid Encoding
    Run tests and check parsing error
    ...    ${PARSING}/invalid_encoding/
    ...    UnicodeDecodeError: .*
    ...    ${PARSING}/invalid_encoding/invalid_encoding.robot

Multisource Containing File With Invalid Encoding
    Run tests and check parsing error
    ...    ${PARSING}/invalid_encoding/invalid_encoding.robot ${PARSING}/invalid_encoding/a_valid_file.robot
    ...    UnicodeDecodeError: .*
    ...    ${PARSING}/invalid_encoding/invalid_encoding.robot

File without read permission
    [Tags]    no-windows
    [Setup]    Create test data without permissions    ${SUITE DIR}/sample.robot
    Run tests and check parsing error
    ...    ${SUITE DIR}/sample.robot
    ...    (IOError|PermissionError): .*
    ...    ${SUITE DIR}/sample.robot
    [Teardown]    Remove test data without permissions    ${SUITE DIR}/sample.robot

Directory without read permission
    [Tags]    no-windows
    [Setup]    Create test data without permissions    ${SUITE DIR}
    Run tests and check parsing error
    ...    ${SUITE DIR}
    ...    (OSError|PermissionError): .*
    ...    ${SUITE DIR}
    ...    Reading directory
    [Teardown]    Remove test data without permissions    ${SUITE DIR}

*** Keywords ***
Run tests and check error
    [Arguments]    ${paths}   ${error}
    ${result}=    Run Tests Without Processing Output    ${EMPTY}    ${paths}
    Should be equal    ${result.rc}    ${252}
    Stderr Should Match Regexp    \\[ ERROR \\] ${error}${USAGE_TIP}

Run tests and check parsing error
    [Arguments]    ${paths}    ${error}    ${path}    ${prefix}=Parsing
    ${path}=    Normalize path    ${path}
    ${path}=    Regexp escape    ${path}
    Run tests and check error    ${paths}    ${prefix} '${path}' failed: ${error}

Create test data without permissions
    [Arguments]    ${remove permissions}
    Create directory    ${SUITE DIR}
    Copy file   ${ROBOTDIR}/sample.robot   ${SUITE DIR}
    Remove permissions    ${remove permissions}

Remove test data without permissions
    [Arguments]    ${remove permissions}
    Set read write execute      ${remove permissions}
    Remove directory    ${SUITE DIR}    recursive=True
