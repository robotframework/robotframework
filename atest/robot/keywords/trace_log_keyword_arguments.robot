*** Settings ***
Suite Setup       Run Tests    --loglevel TRACE    keywords/trace_log_keyword_arguments.robot
Resource          atest_resource.robot

*** Test Cases ***
Only Mandatory Arguments
    Check Argument Value Trace
    ...    \${mand1}='arg1' | \${mand2}='arg2'
    ...    'arg1' | 'arg2'

Mandatory And Default Arguments
    Check Argument Value Trace
    ...    \${mand}='mandatory' | \${default}='default value'
    ...   'mandatory'

Multiple Default Values
    Check Argument Value Trace
    ...    \${a1}='10' | \${a2}='2' | \${a3}='30' | \${a4}=4
    ...    10 | a3=30

Named Arguments
    Check Argument Value Trace
    ...    \${mand}='mandatory' | \${default}='bar'
    ...    'mandatory' | default='bar'

Named Arguments when Name Is Not Matching
    Check Argument Value Trace
    ...    \${mand}='mandatory' | \${default}='foo=bar'
    ...    'mandatory' | 'foo=bar'

Variable Number of Arguments
    Check Argument Value Trace
    ...    \${mand}='a' | \@{vargs}=['b', 'c', 'd']
    ...    'a' | 'b' | 'c' | 'd'
    ...    \${mand}='mandatory' | \@{vargs}=['a', 'b', 'c', 'd']
    ...    'mandatory' | 'a' | 'b' | 'c' | 'd'
    ...    \${mand}='mandatory' | \@{vargs}=[]
    ...    'mandatory'

Named only
    Check Argument Value Trace
    ...    \${no1}='a' | \${no2}='b'
    ...    no1='a' | no2='b'

Kwargs
    Check Argument Value Trace
    ...    \&{kwargs}={}
    ...    ${EMPTY}
    ...    \&{kwargs}={'a': '1', 'b': 2, 'c': '3'}
    ...    a='override' | b=2 | a='1' | c='3'

All args
    Check Argument Value Trace
    ...    \${positional}='1' | \@{varargs}=['2', '3'] | \${named_only}='4' | \&{kwargs}={'free': '5'}
    ...    '1' | '2' | '3' | named_only='4' | free='5'

Non String Object as Argument
    Check Argument Value Trace
    ...    \${mand}=True | \${default}=1.0
    ...    True | default=1.0
    ...    \${mand}=-123 | \@{vargs}=[1.0]
    ...    -123 | 1.0

None as Argument
    Check UKW Default, LKW Default, UKW Varargs, and LKW Varargs    None

Non Ascii String as Argument
    Check UKW Default, LKW Default, UKW Varargs, and LKW Varargs    "Hyvää 'Päivää'\\n"

Object With Unicode Repr as Argument
    Check UKW Default, LKW Default, UKW Varargs, and LKW Varargs
    ...    'Circle is 360°, Hyvää üötä, \u0989\u09c4 \u09f0 \u09fa \u099f \u09eb \u09ea \u09b9'

Arguments With Run Keyword
    ${tc}=    Check Test Case    ${TEST NAME}
    Check Log Message    ${tc.kws[1].msgs[0]}    Arguments: [ '\${keyword name}' | '\@{VALUES}' ]    TRACE
    Check Log Message    ${tc.kws[1].kws[0].msgs[0]}    Arguments: [ 'a' | 'b' | 'c' | 'd' ]    TRACE

Embedded Arguments
    ${tc}=    Check Test Case    ${TEST NAME}
    Check Log Message    ${tc.kws[0].msgs[0]}    Arguments: [ \${first}='foo' | \${second}=42 | \${what}='UK' ]    TRACE
    Check Log Message    ${tc.kws[1].msgs[0]}    Arguments: [ 'bar' | 'Embedded Arguments' ]                       TRACE
    Check Log Message    ${tc.kws[2].msgs[0]}    Arguments: [ \${embedded}='embedded' | \${normal}='argument' ]    TRACE
    Check Log Message    ${tc.kws[3].msgs[0]}    Arguments: [ \${embedded}='embedded' | \${normal}='argument' ]    TRACE
    FOR    ${kw}    IN    @{tc.kws}
        Check Log Message    ${kw.msgs[-1]}    Return: None    TRACE
        Length Should Be     ${kw.msgs}    2
    END

*** Keywords ***
Check Argument Value Trace
    [Arguments]    @{expected}
    ${tc} =    Check Test Case    ${TEST NAME}
    ${length} =    Get Length    ${expected}
    FOR    ${index}    IN RANGE    0    ${length}
        Check Log Message    ${tc.kws[${index}].msgs[0]}    Arguments: [ ${expected}[${index}] ]    TRACE
    END

Check UKW Default, LKW Default, UKW Varargs, and LKW Varargs
    [Arguments]    ${value}
    Check Argument Value Trace
    ...    \${mand}=${value} | \${default}=${value}
    ...    ${value} | default=${value}
    ...    \${mand}=${value} | \@{vargs}=[${value}]
    ...    ${value} | ${value}
