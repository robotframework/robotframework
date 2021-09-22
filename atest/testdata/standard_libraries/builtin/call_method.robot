*** Settings ***
Variables         objects_for_call_method.py

*** Test Cases ***
Call Method
    Call Method    ${obj}    my_method
    Should Be True    ${obj.args} == ()
    Call Method    ${obj}    my_method    arg
    Should Be True    ${obj.args} == ('arg',)
    Call Method    ${obj}    my_method    a1    a2
    Should Be True    ${obj.args} == ('a1','a2')

Call Method Returns
    ${res} =    Call Method    my_str    upper
    Should Be Equal    ${res}    MY_STR
    ${a}    ${b}    ${c} =    Call Method    a,b,c    split    ,
    Should Be Equal    ${a}    a
    Should Be Equal    ${b}    b
    Should Be Equal    ${c}    c

Called Method Fails
    [Documentation]    FAIL Calling method 'my_method' failed: Expected failure
    Call Method    ${obj}    my_method    FAIL!

Call Method With Kwargs
    ${ret} =    Call Method    ${obj}    kwargs    first    arg3=new
    Should Be Equal    ${ret}    first, default, arg3: new
    ${ret} =    Call Method    ${obj}    kwargs    arg1=first    arg3=new
    Should Be Equal    ${ret}    first, default, arg3: new
    ${ret} =    Call Method    ${obj}    kwargs    k1=override    arg1=override
    ...    k2=2    k3=3   arg2=2    k4=4    arg1=1    k5=5    k1=1
    Should Be Equal    ${ret}    1, 2, k1: 1, k2: 2, k3: 3, k4: 4, k5: 5

Equals in non-kwargs must be escaped
    [Documentation]    FAIL STARTS: Calling method 'my_method' failed: TypeError:
    ${ret} =    Call Method    ${obj}    kwargs    arg1\=here    arg2\\\=\=
    ...    arg3\\=    arg4====
    Should Be Equal    ${ret}    arg1=here, arg2\\==, arg3\\: , arg4: ===
    Call Method    ${obj}    my_method    this=fails

Call Method From Module
    ${path} =    Call Method    ${{os.path}}    join    ${CURDIR}    foo    bar.txt
    Should Be Equal    ${path}    ${CURDIR}${/}foo${/}bar.txt

Call Non Existing Method
    [Documentation]    FAIL MyObject object does not have method 'non_existing'.
    Call Method    ${obj}    non_existing
