*** Settings ***
Suite Setup     Run Tests  --loglevel TRACE  keywords/trace_log_keyword_arguments.robot
Force Tags      regression  pybot  jybot
Resource        atest_resource.robot


*** Variables ***
${NON ASCII}  u'Hyv\\xe4\\xe4 P\\xe4iv\\xe4\\xe4'
${OBJECT REPR}  u'Circle is 360\\xb0, Hyv\\xe4\\xe4 \\xfc\\xf6t\\xe4, \\u0989\\u09c4 \\u09f0 \\u09fa \\u099f \\u09eb \\u09ea \\u09b9'

*** Test Cases ***

Only Mandatory Arguments
    Check Argument Value Trace  \${mand1}=u'arg1' | \${mand2}=u'arg2'
    ...  u'arg1' | u'arg2'

Mandatory And Default Arguments
    Check Argument Value Trace  \${mand}=u'mandatory' | \${default}=u'default value'
    ...  u'mandatory'

Multiple Default Values
    Check Argument Value Trace  \${a1}=u'10' | \${a2}=u'2' | \${a3}=u'30' | \${a4}=4
    ...  u'10' | a3=u'30'

Named Arguments
    Check Argument Value Trace  \${mand}=u'mandatory' | \${default}=u'bar'
    ...  u'mandatory' | default=u'bar'

Named Arguments when Name Is Not Matching
    Check Argument Value Trace  \${mand}=u'mandatory' | \${default}=u'foo=bar'
    ...  u'mandatory' | u'foo=bar'

Variable Number of Arguments with UK
    Check Argument Value Trace  \${mand}=u'a' | \@{vargs}=[u'b', u'c', u'd']
    ...  \${mand}=u'mandatory' | \@{vargs}=[u'a', u'b', u'c', u'd']
    ...  \${mand}=u'mandatory' | \@{vargs}=[]

Variable Number of Arguments with Library Keyword
    Check Argument Value Trace  u'a' | u'b' | u'c' | u'd'
    ...  u'mandatory' | u'a' | u'b' | u'c' | u'd'
    ...  u'mandatory'

Arguments With Run Keyword
    ${tc}=  Check Test Case  ${TEST NAME}
    Check Log Message  ${tc.kws[1].msgs[0]}  Arguments: [ u'Log Many' | u'\@{VALUES}' ]  TRACE
    Check Log Message  ${tc.kws[1].kws[0].msgs[0]}  Arguments: [ u'a' | u'b' | u'c' | u'd' ]  TRACE

Non String Object as Argument
    Check Argument Value Trace  \${mand}=True | \${default}=1.0
    ...  True | default=1.0
    ...  \${mand}=-123 | \@{vargs}=[1.0]
    ...  -123 | 1.0

None as Argument
    Check UK Default, Library KW Default, UK Varargs and Library KW Varargs  None

Non Ascii String as Argument
    Check UK Default, Library KW Default, UK Varargs and Library KW Varargs  ${NON ASCII}

Object With Unicode Repr as Argument
    Check UK Default, Library KW Default, UK Varargs and Library KW Varargs  ${OBJECT REPR}

*** Keywords ***
Check Argument Value Trace
    [Arguments]  @{expected}
    ${tc} =  Check Test Case  ${TEST NAME}
    ${length} =  Get Length  ${expected}
    :FOR  ${index}  IN RANGE  0  ${length}
    \    Check Log Message  ${tc.kws[${index}].msgs[0]}  
    \    ...  Arguments: [ @{expected}[${index}] ]  TRACE

Check UK Default, Library KW Default, UK Varargs and Library KW Varargs
    [Arguments]  ${value}
    Check Argument Value Trace  \${mand}=${value} | \${default}=${value}
    ...  ${value} | default=${value}
    ...  \${mand}=${value} | \@{vargs}=[${value}]
    ...  ${value} | ${value}
    
