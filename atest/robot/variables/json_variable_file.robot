*** Settings ***
Suite Setup      Run Tests    --variablefile ${VARDIR}/cli.json -V ${VARDIR}/cli2.json --pythonpath ${VARDIR}
...              variables/json_variable_file.robot
Force Tags       require-json
Resource         atest_resource.robot

*** Variables ***
${VARDIR}        ${DATADIR}/../testresources/res_and_var_files

*** Test Cases ***
Valid JSON file
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
