*** Settings ***
Suite Setup      Run Tests    --variablefile ${VARDIR}/cli.yaml --pythonpath ${VARDIR}    variables/yml_variable_file.robot
Force Tags       require-yaml
Resource         atest_resource.robot

*** Variables ***
${VARDIR}        ${DATADIR}/../testresources/res_and_var_files

*** Test Cases ***
Valid YAML file (with .yml extension)
    Check Test Case    ${TESTNAME}

Non-ASCII strings
    [Tags]    no-ipy
    Check Test Case    ${TESTNAME}

Dictionary is dot-accessible
    Check Test Case    ${TESTNAME}

YAML file in PYTHONPATH
    Check Test Case    ${TESTNAME}

YAML file from CLI
    Check Test Case    ${TESTNAME}

Import Variables keyword
    Check Test Case    ${TESTNAME}

Invalid YAML file
    Processing should have failed    0    invalid.YML
    ...    ${EMPTY}    ComposerError*

Non-mapping YAML file
    Processing should have failed    1    non_dict2.yml
    ...    ${EMPTY}    YAML variable file must be a mapping, got list.

YAML files do not accept arguments
    Processing should have failed    2    valid3.yml
    ...    with arguments ? arguments | not | accepted ?${SPACE}
    ...    YAML variable files do not accept arguments.

Non-existing YAML file (.Yml extension)
    Importing should have failed    3
    ...    Variable file 'non_existing.Yml' does not exist.

YAML with invalid encoding
    Processing should have failed    4    invalid_encoding2.yml
    ...    ${EMPTY}    UnicodeDecodeError*

*** Keywords ***
Processing should have failed
    [Arguments]    ${index}    ${file}    ${arguments}    ${error}
    ${path} =    Normalize Path    ${DATADIR}/variables/${file}
    Importing should have failed    ${index}
    ...    Processing variable file '${path}' ${arguments}failed: ${error}

Importing should have failed
    [Arguments]    ${index}    ${error}
    ${path} =    Normalize Path    ${DATADIR}/variables/yml_variable_file.robot
    Check Log Message    @{ERRORS}[${index}]
    ...    Error in file '${path}': ${error}    ERROR    pattern=yes

