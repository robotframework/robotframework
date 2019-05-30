*** Settings ***
Variables        valid3.yml
Variables        pythonpath2.yml
Variables        ./invalid.YML
Variables        ..${/}variables${/}non_dict2.yml
Variables        valid3.yml    arguments    not    accepted
Variables        non_existing.Yml
Variables        invalid_encoding2.yml
Test Template    Should Be Equal

*** Variables ***
@{EXPECTED LIST}      one    ${2}
&{EXPECTED DICT}      a=1    b=${2}    ${3}=${EXPECTED LIST}    key with spaces=value with spaces

*** Test Cases ***
Valid YAML file (with .yml extension)
    ${STRING}     Hello, YAML!
    ${INTEGER}    ${42}
    ${FLOAT}      ${3.14}
    ${LIST}       ${EXPECTED LIST}
    ${DICT}       ${EXPECTED DICT}

Non-ASCII strings
    ${NON}    äscii
    ${NÖN}    äscii

Dictionary is dot-accessible
    ${DICT.a}                1
    ${DICT.b}                ${2}
    ${NESTED DICT.dict}      ${DICT}
    ${NESTED DICT.dict.a}    1
    ${NESTED DICT.dict.b}    ${2}

YAML file in PYTHONPATH
    ${YAML FILE IN PYTHONPATH}    ${TRUE}

Import Variables keyword
    [Setup]    Import Variables    ${CURDIR}/valid4.yml
    ${VALID 4}    imported successfully

YAML file from CLI
    ${YAML FILE FROM CLI}    woot!
