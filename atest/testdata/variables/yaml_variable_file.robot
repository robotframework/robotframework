*** Settings ***
Variables        valid.yaml
Variables        pythonpath.yaml
Variables        ./invalid.YAML
Variables        ..${/}variables${/}non_dict.yaml
Variables        valid.yaml    arguments    not    accepted
Variables        non_existing.Yaml
Test Template    Should Be Equal

*** Variables ***
@{EXPECTED LIST}      one    ${2}
&{EXPECTED DICT}      a=1    b=${2}    ${3}=${EXPECTED LIST}

*** Test Cases ***
Valid YAML file
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
    [Setup]    Import Variables    ${CURDIR}/valid2.yaml
    ${VALID 2}    imported successfully

YAML file from CLI
    ${YAML FILE FROM CLI}    woot!
