*** Settings ***
Library         Recursion.py
Resource        conversion.resource
Test Tags       require-py3.12

*** Test Cases ***
Valid recursion
    Validate List    ${{(((1,),),)}}
    ${list} =    Create Nested List    50
    Validate List    ${list}

Recursion error
    ${list} =    Create Nested List    200
    Conversion Should Fail
    ...    Validate List    ${list}
    ...    arg_name=data    arg_type=list
    ...    type=dict[str, JSON], list[JSON], string, integer, float, boolean or None
    ...    error=RecursionError:    except_type=START

Nested recursion error
    Conversion Should Fail    Validate Nested    [[1]]
    ...    arg_name=data    type=Nested
    ...    error=Item '0' got value '[1]' (list) that cannot be converted to Nested: Item '0' got value '1' (integer) that cannot be converted to Nested.
