*** Settings ***
Suite Setup       My Setup
Resource          atest_resource.robot

*** Test Cases ***
Statistics Should Be Written to XML
    ${output} =    Get File    ${OUTFILE}
    ${exp} =    Catenate    SEPARATOR=\\r?\\n    (?s)    <statistics>    <total>    .*    </total>
    ...    <tag>    .*    </tag>    <suite>    .*    </suite>    </statistics>
    Should Match Regexp    ${output}    ${exp}

Total statistics should be Correct
    ${stats} =    Get Element    ${OUTFILE}    statistics/total
    ${total} =    Call Method    ${stats}    find    stat
    Node Should Be Correct    ${total}    All Tests    12    1

Tag statistics should be Correct
    ${stats} =    Get Element    ${OUTFILE}    statistics/tag
    Tag Node Should Be Correct    ${stats[0]}    Custom title AND-OR-NOT
    ...    1    0    info=combined    combined=d1 AND d2
    Tag Node Should Be Correct    ${stats[1]}    F1 NOT T 1
    ...    4    0    info=combined    combined=F1 NOT T 1
    Tag Node Should Be Correct    ${stats[2]}    d1
    ...    1    0
    Tag Node Should Be Correct    ${stats[3]}    d2
    ...    1    0
    Tag Node Should Be Correct    ${stats[4]}    f1
    ...    9    1
    Tag Node Should Be Correct    ${stats[5]}    sub3
    ...    2    0
    Tag Node Should Be Correct    ${stats[6]}    t1
    ...    5    1
    Tag Node Should Be Correct    ${stats[7]}    XxX
    ...    12    1

Suite statistics should be correct
    ${stats} =    Get Element    ${OUTFILE}    statistics/suite
    Node Should Be Correct    ${stats[0]}    Suites    12    1
    Node Should Be Correct    ${stats[1]}    Suites.Suite With Prefix    1    0
    Node Should Be Correct    ${stats[2]}    Suites.Fourth    0    1
    Node Should Be Correct    ${stats[3]}    Suites.Subsuites    2    0
    Node Should Be Correct    ${stats[4]}    Suites.Custom name for 📂 'subsuites2'    3    0
    Node Should Be Correct    ${stats[5]}    Suites.Suite With Double Underscore    1    0
    Node Should Be Correct    ${stats[6]}    Suites.Tsuite1    3    0
    Node Should Be Correct    ${stats[7]}    Suites.Tsuite2    1    0
    Node Should Be Correct    ${stats[8]}    Suites.Tsuite3    1    0

*** Keywords ***
My Setup
    Run Tests    ${EMPTY}    misc/suites
    Copy Previous Outfile
    ${options} =    Catenate
    ...    --tagstatcombine "d1 AND d2:Custom title AND-OR-NOT"
    ...    --suitestatlevel 2
    ...    --tagstatexclude t2
    ...    --TagStatComb F1NOTT_1
    ...    --SetTag XxX
    Run Rebot    ${options}    ${OUTFILE COPY}

Node Should Be Correct
    [Arguments]    ${node}    ${name}    ${pass}    ${fail}
    Element Text Should Be      ${node}      ${name}
    Element Attribute Should Be      ${node}      pass      ${pass}
    Element Attribute Should Be      ${node}      fail      ${fail}

Tag Node Should Be Correct
    [Arguments]    ${node}    ${name}    ${pass}    ${fail}    ${info}=    ${combined}=
    Node Should Be Correct    ${node}    ${name}    ${pass}    ${fail}
    Should be equal    ${node.attrib.get('info', '')}    ${info}
    Should be equal    ${node.attrib.get('combined', '')}    ${combined}
