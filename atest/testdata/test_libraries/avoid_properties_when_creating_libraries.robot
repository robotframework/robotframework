*** Settings ***
Suite Setup       Keyword
Library           AvoidProperties.py
Test Template     Attribute value should be

*** Test Cases ***
Property
    normal_property

Classmethod property
    classmethod_property    classmethod=True

Cached property
    cached_property

Non-data descriptor
    non_data_descriptor    2

Classmethod non-data descriptor
    classmethod_non_data_descriptor    2    classmethod=True

Data descriptor
    data_descriptor

Classmethod data descriptor
    classmethod_data_descriptor    classmethod=True

*** Keywords ***
Attribute value should be
    [Arguments]    ${attr}    ${expected}=1    ${classmethod}=False
    ${lib} =    Get Library Instance    AvoidProperties
    IF    sys.version_info >= (3, 9) or not ${classmethod}
        Should Be Equal As Integers    ${lib.${attr}}    ${expected}
    END
    TRY
        Run Keyword    ${attr}
    EXCEPT    No keyword with name '${attr}' found.
        No Operation
    END
