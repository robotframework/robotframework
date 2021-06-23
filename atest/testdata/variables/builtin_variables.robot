*** Settings ***
Library         OperatingSystem
Library         Collections

*** Variables ***
${TEMPDIR}  Cannot be overridden
${TRUE}  Cannot be overridden
${SPACE}  Cannot be overridden
${TEST_NAME}  Cannot be overridden
${1234}  Can be overridden
${-4.1}  Can be overridden

*** Test Cases ***
Integer Variables
    [Documentation]  FAIL  Variable '${FF}' not found.
    ${one} =  Convert To Integer  1
    ${minus_two} =  Convert To Integer  -2
    Should Be Equal  ${1}  ${one}
    Should Be Equal  ${ - 2 }  ${minus_two}
    Should Be True  repr(${12345}) == '12345'
    Should Be True  repr(${123456789012345678901234567890}).strip('L') == '123456789012345678901234567890'
    Log  No automatic hex conversion ${FF}

Integer Variables With Base
    [Documentation]  FAIL STARTS:  Variable '${0b123}' not found.
    Should Be Equal  ${0xFF}    ${255}
    Should Be Equal  ${ 0 X A}  ${10}
    Should Be Equal  ${0b1010}  ${10}
    Should Be Equal  ${0B0}     ${0O0}
    Should Be Equal  ${0o10}    ${8}
    Log  This fails: ${0b123}

Float Variables
    ${pi} =  Convert To Number  3.14
    Should Be Equal  ${3.14}  ${pi}
    Should Be Equal  ${ + 3 . 1 4 }  ${pi}
    Should Be Equal  ${1E6}  ${1000000}
    Should Be Equal  ${+1 e 3}  ${1000}
    Should Be True  ${-2.1e3} == ${-2100} == ${-2100.0}
    Should Be True  ${123456789012345.67890} < ${1.235e14}

Boolean Variables
    Should Be True  ${TRUE}
    Should Be True  ${true}
    Should Be True  ${ t R u E }
    Should Not Be True  ${FALSE}
    Should Not Be True  ${false}
    Should Not Be True  ${F a ls E}
    ${t} =  Evaluate  True
    ${f} =  Evaluate  False
    Should Be Equal  ${TRUE}  ${t}
    Should Be Equal  ${False}  ${f}
    Should Be Equal  ${True} catenated with ${False}  ${True} catenated with ${False}

\${None} And \${null}
    ${n} =  Evaluate  None
    Should Be Equal  ${None}  ${n}
    Should Be Equal  ${n u l l}  ${None}
    Should Not Be Equal  ${no ne}  None
    Should Be Equal  ${None} catenated with ${null}  None catenated with None

\${SPACE}
    Should Be Equal  ${SPACE}  \ \
    Should Be Equal  ${SPACE * 5}  \ \ \ \ \ \
    Should Be Equal  -${SPACE}-${SPACE*2}-${SPACE}-  - - \ - -

\${EMPTY}
    Should Be Equal  ${EMPTY}  \
    Should Be Equal  ${EMPTY * 5}  \
    Should Be Equal  -${empty}-${emp_ty*2}-${EMP ty}-  ----

\@{EMPTY}
    Should Be True   @{EMPTY} == []
    Should Be True   @{EMPTY}+@{EMPTY} == []
    Should Be Equal  @{empty}  value  @{emp_ty}  value  @{EMP ty}
    ${value} =  Catenate  @{EMPTY}  @{EMPTY}
    Should Be Equal  ${value}    ${EMPTY}

\&{EMPTY}
    Should Be True   &{EMPTY} == {}
    Should Be Equal  value  value  &{empty}  &{emp_ty}  &{EMP ty}

\@{EMPTY} and \&{EMPTY} cannot be modified
    ${result} =    Create Dictionary    list=@{EMPTY}    dict=&{EMPTY}
    ${list} =    Get From Dictionary    ${result}    list
    ${dict} =    Get From Dictionary    ${result}    dict
    Append To List       ${list}    value
    Set To Dictionary    ${dict}    key=value
    Should Be True   @{list} == ['value']
    Should Be True   &{dict} == {'key': 'value'}
    Should Be True   @{EMPTY} == []
    Should Be True   &{EMPTY} == {}

\${/}
    ${exp} =  Evaluate  os.sep  modules=os
    Should Be Equal  ${/}  ${exp}
    Should Be Equal  ${/}foo${/}  ${exp}foo${exp}

\${:}
    ${exp} =  Evaluate  os.pathsep  modules=os
    Should Be Equal  ${:}  ${exp}

\${\\n}
    ${exp} =  Evaluate  os.linesep  modules=os
    Should Be Equal  ${\n}  ${exp}

\${TEMPDIR}
    ${exp} =  Evaluate  tempfile.gettempdir().rstrip('/')  modules=tempfile
    Should Be Equal  ${TEMPDIR}  ${exp}
    Directory Should Exist  ${TEMPDIR}
    Should Not End With  ${TEMPDIR}  /
    Should Not End With  ${TEMPDIR}  \\
    Should Start With  \${TEMPDIR}  $

\${EXECDIR}
    ${exp} =  Evaluate  os.path.abspath('.')  modules=os
    Should Be Equal  ${EXECDIR}  ${exp}
    Directory Should Exist  ${EXECDIR}
    Should Not End With  ${EXECDIR}  /
    Should Not End With  ${EXECDIR}  \\
    Should Start With  \${EXECDIR}  $

$CURDIR
    Directory Should Exist  ${CURDIR}
    Should Not End With  ${CURDIR}  /
    Should Not End With  ${CURDIR}  \\
    Comment  $\{CURDIR} is resolved differently than other variables and cannot be escaped with a backslash before it
    Should Start With  $\{CURDIR}  $

\${LOG LEVEL}
    Should Be Equal  ${LOG_LEVEL}  INFO
    Set Log Level  trace
    Should Be Equal  ${LOG_LEVEL}  TRACE
    Set Log Level  NONE
    Should Be Equal  ${LOG_LEVEL}  NONE
    [Teardown]  Set Log Level  INFO

Built-In Variables Cannot Be Overridden In Variable Table Or From CLI
    [Documentation]  Except for number variabels
    Should Not Be Equal  ${TEMPDIR}  Cannot be overridden
    Should Not Be Equal  ${TRUE}  Cannot be overridden
    Should Not Be Equal  ${SPACE}  Cannot be overridden
    Should Not Be Equal  ${TEST_NAME}  Cannot be overridden
    Should Not Be Equal  ${FALSE}  CLI

Number Variables Can Be Overridden In Variable Table And From CLI
    Should Be Equal  ${1234}  Can be overridden
    Should Be Equal  ${-4.1}  Can be overridden
    Should Be Equal  ${77}  CLI

Built-In Variables Can Be Overridden In Local Scope 1
    ${TEMPDIR} =  Set Variable  Local value 1
    ${TRUE} =  Set Variable  Local value 2
    ${SPACE} =  Set Variable  Local value 3
    ${TEST_NAME} =  Set Variable  Local value 4
    ${1} =  Set Variable  Local value 5
    Should Be Equal  ${TEMPDIR}  Local value 1
    Should Be Equal  ${TRUE}  Local value 2
    Should Be Equal  ${SPACE}  Local value 3
    Should Be Equal  ${TEST_NAME}  Local value 4
    Should Be Equal  ${1}  Local value 5

Built-In Variables Can Be Overridden In Local Scope 2
    Should Not Be Equal  ${TEMPDIR}  Local value 1
    Should Not Be Equal  ${TRUE}  Local value 2
    Should Not Be Equal  ${SPACE}  Local value 3
    Should Not Be Equal  ${TEST_NAME}  Local value 4
    Should Not Be Equal  ${1}  Local value 5
