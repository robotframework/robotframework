*** Settings ***
Variables        valid.json
Variables        pythonpath.json
Variables        ./invalid.json
Variables        ..${/}variables${/}non_dict.json
Variables        valid.json    arguments    not    accepted
Variables        non_existing.Json
Variables        invalid_encoding.json
Variables        valid3.JSON
Test Template    Should Be Equal

*** Variables ***
@{EXPECTED LIST}      one    ${2}
&{EXPECTED DICT}      a=1    b=${2}    3=${EXPECTED LIST}    key with spaces=value with spaces


*** Test Cases ***
Valid JSON file
    ${STRING}     Hello, YAML!
    ${INTEGER}    ${42}
    ${FLOAT}      ${3.14}
    ${LIST}       ${EXPECTED LIST}
    ${DICT}       ${EXPECTED DICT}
    ${BOOL}       ${TRUE}
    ${NULL}       ${NULL}

Valid JSON file with uper case extension
    ${STRING IN JSON}     Hello, YAML!
    ${INTEGER IN JSON}    ${42}
    ${FLOAT IN JSON}      ${3.14}
    ${LIST IN JSON}       ${EXPECTED LIST}
    ${DICT IN JSON}       ${EXPECTED DICT}
    ${BOOL IN JSON}       ${TRUE}
    ${NULL IN JSON}       ${NULL}

Non-ASCII strings
    ${NON}    äscii
    ${NÖN}    äscii

Dictionary is dot-accessible
    ${DICT.a}                1
    ${DICT.b}                ${2}

Nested dictionary is dot-accessible
    ${NESTED DICT.dict}      ${EXPECTED DICT}
    ${NESTED DICT.dict.a}    1
    ${NESTED DICT.dict.b}    ${2}

Dictionary inside list is dot-accessible
    ${LIST WITH DICT[1].key}               value
    ${LIST WITH DICT[2].dict}              ${EXPECTED DICT}
    ${LIST WITH DICT[2].nested[0].leaf}    value

JSON file in PYTHONPATH
    ${JSON FILE IN PYTHONPATH}    ${TRUE}

Import Variables keyword
    [Setup]    Import Variables    ${CURDIR}/valid2.json
    ${VALID 2}    imported successfully

JSON file from CLI
    ${JSON FILE FROM CLI}    woot!
    ${JSON FILE FROM CLI2}     kewl!
