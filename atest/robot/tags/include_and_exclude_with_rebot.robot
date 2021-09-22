*** Settings ***
Documentation     Testing rebot's include/exclude functionality. Tests also include/exclude first during test execution and then with rebot.
Suite Setup       Create Input Files
Suite Teardown    Remove File    ${INPUT FILE}
Test Template     Run And Check Include And Exclude
Resource          rebot_resource.robot

*** Variables ***
${TEST FILE}      tags/include_and_exclude.robot
${TEST FILE2}     tags/no_force_no_default_tags.robot
${INPUT FILE}     %{TEMPDIR}/robot-tags-input.xml
${INPUT FILE 2}    %{TEMPDIR}/robot-tags-input-2.xml
${INPUT FILES}    ${INPUT FILE}
@{INCL_ALL}       Incl-1    Incl-12    Incl-123
@{EXCL_ALL}       excl-1    Excl-12    Excl-123
@{ALL}            @{INCL_ALL}    @{EXCL_ALL}

*** Test Cases ***
No Includes Or Excludes
    ${EMPTY}    @{ALL}

One Include
    --include incl1    @{INCL_ALL}

Matching And Non Matching Includes
    -i INCL3 -i nonexisting    Incl-123

More Includes
    -i incl2 --include incl3 -i _ --include incl2    Incl-12    Incl-123

Includes With AND
    [Documentation]    Testing including like "--include tag1&tag2" both with "&" and "AND"
    --include incl1ANDincl2    Incl-12    Incl-123
    -i incl1&incl2&incl3    Incl-123

Includes With OR
    --include incl3ORnonex    Incl-123
    --include incl3ORincl2    Incl-12    Incl-123
    --include nonexORxxxORincl2    Incl-12    Incl-123

Include With Patterns
    --include incl?    @{INCL_ALL}
    -i *cl3 -i i*2    Incl-12    Incl-123    Excl-123
    -i i?*3ANDFORCE --include inc*    @{INCL_ALL}
    -i incl?*ORnonex    @{INCL_ALL}

One Exclude
    --exclude excl1    @{INCL_ALL}

Matching And Non Matching Excludes
    -e EXCL3 -e nonexisting    @{INCL_ALL}    excl-1    Excl-12

More Excludes
    --exclude excl3 -e excl2    @{INCL_ALL}    excl-1

Exclude With AND
    --exclude excl1&excl2    @{INCL_ALL}    excl-1
    -e excl1&excl2ANDexcl3    @{INCL_ALL}    excl-1    Excl-12

Exclude With OR
    --exclude nonexORexcl2    @{INCL_ALL}    excl-1
    --exclude excl3ORexcl2    @{INCL_ALL}    excl-1

Exclude With Patterns
    --exclude exc??    @{INCL_ALL}
    -e *3 -e e*2 -e e*1    Incl-1    Incl-12
    --excl excl?ORnonex    @{INCL_ALL}

Include And Exclude
    [Documentation]    Include and exclude together with and without patterns and ANDing
    -i force --exclude excl2    @{INCL_ALL}    excl-1
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
    [Setup]    Set Test Variable    ${INPUT FILES}    ${INPUT FILE 2}
    --exclude *ORwhatever    No Own Tags No Force Nor Default    Own Tags Empty No Force Nor Default

Select tests with any tag
    [Setup]    Set Test Variable    ${INPUT FILES}    ${INPUT FILE 2}
    --include *AND*    Own Tags No Force Nor Default

Non Matching Include
    [Template]    Run And Check Error
    --include nonex    tag 'nonex'
    --include nonex -i nonex2    tags 'nonex' or 'nonex2'
    --include incl1&nonex    tag 'incl1 AND nonex'
    --include nonex_OR_nonex_2    tag 'nonex OR nonex 2'

Non Matching Exclude
    --exclude nonexisting -e nonex2 -e nonex3    @{ALL}

Non Matching Include And Exclude
    [Template]    Run And Check Error
    -i nonex -e nonex2                            tag 'nonex' and not matching tag 'nonex2'
    --include nonex -i incl? -e *1 -e *2 -e *3    tags 'nonex' or 'incl?' and not matching tags '*1', '*2' or '*3'

Non Matching When Reboting Multiple Outputs
    [Setup]    Set Test Variable    ${INPUT FILES}    ${INPUT FILE} ${INPUT FILE 2}
    [Template]    Run And Check Error
    --include nonex    tag 'nonex'    Include And Exclude & No Force No Default Tags
    --include nonex --name MyName   tag 'nonex'    MyName

Including With Robot And Including And Excluding With Rebot
    [Setup]    Create Output With Robot    ${INPUT FILE}    --include incl1 --exclude nonexisting    ${TESTFILE}
    -i i*2* -e nonexisting -e incl3    Incl-12

Excluding With Robot And Including And Excluding Without Matching Rebot
    [Setup]    Create Output With Robot    ${INPUT FILE}    -i incl1 --exclude excl*    ${TESTFILE}
    -e nonexisting -e excl3    @{INCL_ALL}

Elapsed Time
    [Documentation]    Test setting start, end and elapsed times correctly when filtering by tags
    [Template]    NONE
    # Rebot hand-edited output with predefined times and check that times are read correctly.
    Run Rebot    ${EMPTY}    rebot/times.xml
    Check Times    ${SUITE.tests[0]}    20061227 12:00:00.000    20061227 12:00:01.000    1000
    Check Times    ${SUITE.tests[1]}    20061227 12:00:01.000    20061227 12:00:03.000    2000
    Check Times    ${SUITE.tests[2]}    20061227 12:00:03.000    20061227 12:00:07.000    4000
    Check Times    ${SUITE.tests[3]}    20061227 12:00:07.000    20061227 12:00:07.001    0001
    Check Times    ${SUITE.tests[4]}    20061227 12:00:07.001    20061227 12:00:07.003    0002
    Check Times    ${SUITE.tests[5]}    20061227 12:00:07.003    20061227 12:00:07.007    0004
    Check Times    ${SUITE}    20061227 11:59:59.000    20061227 12:00:08.999    9999
    Length Should Be    ${SUITE.tests}    6
    # Filter ouput created in earlier step and check that times are set accordingly.
    Copy Previous Outfile
    Run Rebot    --include incl2 --include excl3    ${OUTFILE COPY}
    Check Times    ${SUITE}    ${NONE}    ${NONE}    6004
    Check Times    ${SUITE.tests[0]}    20061227 12:00:01.000    20061227 12:00:03.000    2000
    Check Times    ${SUITE.tests[1]}    20061227 12:00:03.000    20061227 12:00:07.000    4000
    Check Times    ${SUITE.tests[2]}    20061227 12:00:07.003    20061227 12:00:07.007    004
    Length Should Be    ${SUITE.tests}    3

*** Keywords ***
Create Input Files
    Create Output With Robot    ${INPUT FILE 2}    ${EMPTY}    ${TEST FILE 2}
    Create Output With Robot    ${INPUT FILE}    ${EMPTY}    ${TEST FILE}

Run And Check Include And Exclude
    [Arguments]    ${params}    @{tests}
    Run Rebot    ${params}    ${INPUT FILES}
    Stderr Should Be Empty
    Should Contain Tests    ${SUITE}    @{tests}
    Should Be True    $SUITE.statistics.passed == len($tests)
    Should Be True    $SUITE.statistics.failed == 0
    Should Be Equal    ${SUITE.starttime}    ${{None if $params else $ORIG_START}}
    Should Be Equal    ${SUITE.endtime}      ${{None if $params else $ORIG_END}}
    Elapsed Time Should Be Valid    ${SUITE.elapsedtime}
    Should Be True    $SUITE.elapsedtime <= $ORIG_ELAPSED + 1

Run And Check Error
    [Arguments]    ${params}    ${filter msg}    ${suite name}=Include And Exclude
    Run Rebot Without Processing Output    ${params}    ${INPUT FILES}
    Stderr Should Be Equal To    SEPARATOR=
    ...    [ ERROR ] Suite '${suite name}' contains no tests matching ${filter msg}.
    ...    ${USAGE TIP}\n
    File Should Not Exist    ${OUTFILE}
