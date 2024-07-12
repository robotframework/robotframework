*** Settings ***
Suite Setup       Keyword
Library           AvoidProperties.py
Test Template     Attribute value should be

*** Test Cases ***
Property
    normal_property

Classmethod property
    classmethod_property

Cached property
    cached_property

Non-data descriptor
    non_data_descriptor    2

Classmethod non-data descriptor
    classmethod_non_data_descriptor

Data descriptor
    data_descriptor

Classmethod data descriptor
    classmethod_data_descriptor

*** Keywords ***
Attribute value should be
    [Arguments]    ${attr}    ${expected}=1
    IF    'classmethod' not in $attr
        ${lib} =    Get Library Instance    AvoidProperties
        Should Be Equal As Integers    ${lib.${attr}}    ${expected}
    END
    TRY
        Run Keyword    ${attr}
    EXCEPT    No keyword with name '${attr}' found.
        No Operation
    END
