*** Settings ***
Library          multiload.py    num=1    AS    Test1
Library          multiload.py    num=2    AS    Test1
Library          multiload.py    num=3    AS    Test1

*** Test Cases ***
Load the same library multiple times using different parameters
    ${num}=      Get Num
    Should Be Equal As Numbers    ${num}    1
    BuiltIn.Import Library    ${CURDIR}/multiload.py    num=4    AS    Test4
    BuiltIn.Import Library    ${CURDIR}/multiload.py    num=4    AS    Test1
    ${num}=      Test1.Get Num
    Should Be Equal As Numbers    ${num}    1
    ${num}=      Test4.Get Num
    Should Be Equal As Numbers    ${num}    4
