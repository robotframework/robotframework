*** Settings ***
Suite Setup      Run Tests    --variablefile ${VARDIR}/cli.yaml -V ${VARDIR}/cli.YML --pythonpath ${VARDIR}
...              variables/yaml_variable_file.robot
Force Tags       require-yaml
Resource         atest_resource.robot

*** Variables ***
${VARDIR}        ${DATADIR}/../testresources/res_and_var_files

*** Test Cases ***
Valid YAML file
    Check Test Case    ${TESTNAME}

Valid YML file
    Check Test Case    ${TESTNAME}

Non-ASCII strings
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
    Processing should have failed    0    5    invalid.YAML
    ...    ${EMPTY}
    ...    ComposerError*

Non-mapping YAML file
    Processing should have failed    1    6    non_dict.yaml
    ...    ${EMPTY}
    ...    YAML variable file must be a mapping, got list.

YAML files do not accept arguments
    Processing should have failed    2    7    valid.yaml
    ...    with arguments ? arguments | not | accepted ?${SPACE}
    ...    YAML variable files do not accept arguments.

Non-existing YAML file
    Importing should have failed    3    8
    ...    Variable file 'non_existing.Yaml' does not exist.

YAML with invalid encoding
    Processing should have failed    4    9    invalid_encoding.yaml
    ...    ${EMPTY}
    ...    UnicodeDecodeError*

*** Keywords ***
Processing should have failed
    [Arguments]    ${index}    ${lineno}    ${file}    ${arguments}    ${error}
    ${path} =    Normalize Path    ${DATADIR}/variables/${file}
    Importing should have failed    ${index}    ${lineno}
    ...    Processing variable file '${path}' ${arguments}failed:
    ...    ${error}

Importing should have failed
    [Arguments]    ${index}    ${lineno}    @{error}
    Error In File    ${index}    variables/yaml_variable_file.robot    ${lineno}
    ...    @{error}

