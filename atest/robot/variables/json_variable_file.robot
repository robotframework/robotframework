*** Settings ***
Suite Setup      Run Tests    --variablefile "${VARDIR}/cli.json" -V "${VARDIR}/cli2.json" --pythonpath "${VARDIR}"
...              variables/json_variable_file.robot
Resource         atest_resource.robot

*** Variables ***
${VARDIR}        ${DATADIR}/../testresources/res_and_var_files

*** Test Cases ***
Valid JSON file
    Check Test Case    ${TESTNAME}

Valid JSON file with uper case extension
    Check Test Case    ${TESTNAME}

Non-ASCII strings
    Check Test Case    ${TESTNAME}

Dictionary is dot-accessible
    Check Test Case    ${TESTNAME}

Nested dictionary is dot-accessible
    Check Test Case    ${TESTNAME}

Dictionary inside list is dot-accessible
    Check Test Case    ${TESTNAME}

JSON file in PYTHONPATH
    Check Test Case    ${TESTNAME}

Import Variables keyword
    Check Test Case    ${TESTNAME}

JSON file from CLI
    Check Test Case    ${TESTNAME}

Invalid JSON file
    Processing should have failed    0    4    invalid.json
    ...    ${EMPTY}
    ...    JSONDecodeError*

Non-mapping JSON file
    Processing should have failed    1    5    non_dict.json
    ...    ${EMPTY}
    ...    JSON variable file must be a mapping, got list.

JSON files do not accept arguments
    Processing should have failed    2    6    valid.json
    ...    with arguments ['arguments', 'not', 'accepted']${SPACE}
    ...    JSON variable files do not accept arguments.
    ...    pattern=False

Non-existing JSON file
    Importing should have failed    3    7
    ...    Variable file 'non_existing.Json' does not exist.

JSON with invalid encoding
    Processing should have failed    4    8    invalid_encoding.json
    ...    ${EMPTY}
    ...    UnicodeDecodeError*

*** Keywords ***
Processing should have failed
    [Arguments]    ${index}    ${lineno}    ${file}    ${arguments}    ${error}    ${pattern}=True
    ${path} =    Normalize Path    ${DATADIR}/variables/${file}
    Importing should have failed    ${index}    ${lineno}
    ...    Processing variable file '${path}' ${arguments}failed:
    ...    ${error}
    ...    pattern=${pattern}

Importing should have failed
    [Arguments]    ${index}    ${lineno}    @{error}    ${pattern}=True
    Error In File    ${index}    variables/json_variable_file.robot    ${lineno}
    ...    @{error}
    ...    pattern=${pattern}
