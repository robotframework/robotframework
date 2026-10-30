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
