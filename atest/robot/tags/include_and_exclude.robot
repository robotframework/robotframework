*** Settings ***
Documentation     Test --include and --exclude with Robot.
...
...               These options working together with --suite and --test
...               is tested in filter_by_names.robot suite file.
Test Template     Run And Check Include And Exclude
Resource          atest_resource.robot

*** Variables ***
# Note: Tests using the `robot:exclude` tag in
# atest\testdata\tags\include_and_exclude.robot
# are automatically excluded.
${DATA SOURCES}   tags/include_and_exclude.robot
@{INCL_ALL}       Incl-1    Incl-12    Incl-123
@{EXCL_ALL}       Excl-1    Excl-12    Excl-123
@{ALL}            @{INCL_ALL}    @{EXCL_ALL}

*** Test Cases ***
No Includes Or Excludes
    ${EMPTY}    @{ALL}

Empty iclude and exclude are ignored
    --include= --exclude=    @{ALL}

One Include
    --include incl1    @{INCL_ALL}

Matching And Non Matching Includes
    -i INCL3 -i nonexisting    Incl-123

More Includes
    -i incl2 --include incl3 -i _ --include incl2    Incl-12    Incl-123

Includes With AND
    --include incl1ANDincl2     Incl-12    Incl-123
    -i incl1ANDincl2ANDincl3    Incl-123

Includes With OR
    --include incl3ORnonex         Incl-123
    --include incl3ORincl2         Incl-12    Incl-123
    --include nonexORxxxORincl2    Incl-12    Incl-123

Include With Patterns
    --include incl?              @{INCL_ALL}
    -i i*3 -i no*match           Incl-123
    -i i*3ANDforce -i *2NOTe*    Incl-12    Incl-123
    -i "incl?* OR nonex"         @{INCL_ALL}

One Exclude
    --exclude excl1    @{INCL_ALL}

Matching And Non Matching Excludes
    -e EXCL3 -e nonexisting    @{INCL_ALL}    Excl-1    Excl-12

More Excludes
    --exclude excl3 -e excl2    @{INCL_ALL}    Excl-1

Exclude With AND
    --exclude excl1ANDexcl2     @{INCL_ALL}    Excl-1
    -e excl1ANDexcl2ANDexcl3    @{INCL_ALL}    Excl-1    Excl-12

Exclude With OR
    --exclude nonexORexcl2    @{INCL_ALL}    Excl-1
    --exclude excl3ORexcl2    @{INCL_ALL}    Excl-1

Exclude With Patterns
    --exclude exc??        @{INCL_ALL}
    -e *3 -e e*2 -e e*1    Incl-1    Incl-12
    --excl excl?ORnonex    @{INCL_ALL}

Include And Exclude
    [Documentation]    Include and exclude together with and without patterns and ANDing
    -i force --exclude excl2                           @{INCL_ALL}    Excl-1
    --include *cl2 -i nonex -e e???2 -i forceANDi*1    @{INCL_ALL}

Include with NOT
    --include incl1_NOT_incl3              Incl-1    Incl-12
    --include incl1_NOT_incl2_AND_incl3    Incl-1    Incl-12
    --include incl1_NOT_incl2_OR__incl3    Incl-1
    --include incl1_NOT_incl2_NOT_incl3    Incl-1

Exclude with NOT
    --exclude excl1NOTexcl2ANDexcl3    Excl-123    @{INCL_ALL}

Include and Exclude with NOT
    --include incl1NOTincl3 --exclude incl1NOTincl2    Incl-12

Select tests without any tags
    [Setup]    Set Test Variable    ${DATA SOURCES}    tags/no_force_no_default_tags.robot
    --exclude *ORwhatever    No Own Tags No Force Nor Default    Own Tags Empty No Force Nor Default

Select tests with any tag
    [Setup]    Set Test Variable    ${DATA SOURCES}    tags/no_force_no_default_tags.robot
    --include *AND*    Own Tags No Force Nor Default

Non Matching Include
    [Template]    Run And Check Error
    --include nonex               tag 'nonex'
    --include nonex -i nonex2     tags 'nonex' or 'nonex2'
    --include incl1ANDnonex       tag 'incl1ANDnonex'
    --include nonex_OR_nonex_2    tag 'nonex_OR_nonex_2'

Non Matching Exclude
    --exclude nonexisting -e nonex2 -e nonex3    @{ALL}

Non Matching Include And Exclude
    [Template]    Run And Check Error
    -i nonex -e nonex2                            tag 'nonex' and not matching tag 'nonex2'
    --include nonex -i incl? -e *1 -e *2 -e *3    tags 'nonex' or 'incl?' and not matching tags '*1', '*2' or '*3'

Non Matching When Running Multiple Suites
    [Setup]    Set Test Variable    ${DATA SOURCES}    misc/pass_and_fail.robot misc/normal.robot
    [Template]    Run And Check Error
    --include nonex                 tag 'nonex'    Pass And Fail & Normal
    --include nonex --name MyName   tag 'nonex'    MyName

Suite containing tasks is ok if only tests are selected
    --include test    Test    sources=rpa/tasks rpa/tests.robot
    --exclude task    Test    sources=rpa/tasks rpa/tests.robot

Deprecated operator usage
    [Template]    Validate deprecated operator warning
    --include    INCL1AND*    AND
    --exclude    e*ORBAD      OR
    --include    i*NOTBAD     NOT

Deprecated & operator
    [Template]    Validate deprecated operator warning
    --include    INCL1&*    &
    --exclude    e*&*       &

*** Keywords ***
Run And Check Include And Exclude
    [Arguments]    ${params}    @{expected}    ${sources}=${DATA SOURCES}    ${warnings}=False
    Run Tests    ${params}    ${sources}
    IF    not ${warnings}    Stderr Should Be Empty
    Should Contain Tests    ${SUITE}    @{expected}

Validate deprecated operator warning
    [Arguments]    ${option}    ${pattern}    ${operator}
    Run And Check Include And Exclude    ${option} ${pattern}    @{INCL_ALL}    warnings=True
    IF    $operator == '&'
        VAR    ${explanation}
        ...    Boolean operator '&' is deprecated, use 'AND' instead.
    ELSE
        VAR    ${explanation}
        ...    '${operator}' is currently considered to be a Boolean operator, but in the future
        ...    operators must be surrounded with spaces or tag names must be lower case.
    END
    VAR    ${expected}
    ...    Problems when ${{"including" if $option == "--include" else "excluding"}} tests by tags:
    ...    The behavior of tag pattern '${pattern}' will change in Robot Framework 8.0: ${explanation}
    Check Log Message    ${ERRORS}[0]    ${expected}    WARN

Run And Check Error
    [Arguments]    ${params}    ${filter_msg}    ${suite name}=Include And Exclude
    Run Tests Without Processing Output    ${params}    ${DATA SOURCES}
    Stderr Should Be Equal To    SEPARATOR=
    ...    [ ERROR ] Suite '${suite name}' contains no tests matching ${filter_msg}.
    ...    ${USAGE TIP}\n
    File Should Not Exist    ${OUTFILE}
