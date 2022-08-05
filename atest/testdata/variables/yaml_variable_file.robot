*** Settings ***
Variables        valid.yaml
Variables        valid.yml
Variables        pythonpath.yaml
Variables        ./invalid.YAML
Variables        ..${/}variables${/}non_dict.yaml
Variables        valid.yaml    arguments    not    accepted
Variables        non_existing.Yaml
Variables        invalid_encoding.yaml
Test Template    Should Be Equal

*** Variables ***
@{EXPECTED LIST}      one    ${2}
&{EXPECTED DICT}      a=1    b=${2}    ${3}=${EXPECTED LIST}    key with spaces=value with spaces

*** Test Cases ***
Valid YAML file
    ${STRING}     Hello, YAML!
    ${INTEGER}    ${42}
    ${FLOAT}      ${3.14}
    ${LIST}       ${EXPECTED LIST}
    ${DICT}       ${EXPECTED DICT}

Valid YML file
    ${STRING IN YML}     Hello, YML!
    ${INTEGER IN YML}    ${42}
    ${FLOAT IN YML}      ${3.14}
    ${LIST IN YML}       ${EXPECTED LIST}
    ${DICT IN YML}       ${EXPECTED DICT}

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

YAML file in PYTHONPATH
    ${YAML FILE IN PYTHONPATH}    ${TRUE}

Import Variables keyword
    [Setup]    Import Variables    ${CURDIR}/valid2.yaml
    ${VALID 2}    imported successfully

YAML file from CLI
    ${YAML FILE FROM CLI}    woot!
    ${YML FILE FROM CLI}     kewl!
