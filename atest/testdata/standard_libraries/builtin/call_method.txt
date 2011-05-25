*** Settings ***
Variables       objects_for_call_method.py

*** Test Cases ***

Call Method
    Call Method  ${obj}  my_method
    Should Be True  ${obj.args} == ()
    Call Method  ${obj}  my_method  arg
    Should Be True  ${obj.args} == ('arg',)
    Call Method  ${obj}  my_method  a1  a2
    Should Be True  ${obj.args} == ('a1','a2')

Call Method Returns
    ${res} =  Call Method  my_str  upper
    Should Be Equal  ${res}  MY_STR
    ${a}  ${b}  ${c} =  Call Method  a,b,c  split  ,
    Should Be Equal  ${a}  a
    Should Be Equal  ${b}  b
    Should Be Equal  ${c}  c

Call Method From Module
    ${path} =  Call Method  ${os.path}  join  ${CURDIR}  foo  bar.txt
    Should Be Equal  ${path}  ${CURDIR}${/}foo${/}bar.txt

Call Non Existing Method
    [Documentation]  FAIL Object 'String presentation of MyObject' does not have a method 'non_existing'
    Call Method  ${obj}  non_existing

Call Java Method
    ${isempty} =  Call Method  ${hashtable}  isEmpty
    Should Be True  ${isempty}
    Call Method  ${hashtable}  put  myname  myvalue
    ${value} =  Call Method  ${hashtable}  get  myname
    Should Be Equal  ${value}  myvalue
    ${isempty} =  Call Method  ${hashtable}  isEmpty
    Should Not Be True  ${isempty}

Call Non Existing Java Method
    [Documentation]  FAIL Object '{myname=myvalue}' does not have a method 'nonExisting'
    Call Method  ${hashtable}  nonExisting

