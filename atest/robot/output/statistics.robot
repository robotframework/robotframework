*** Settings ***
Suite Setup       My Setup
Force Tags        regression
Default Tags      pybot    jybot
Resource          atest_resource.robot

*** Test Cases ***
Statistics Should Be Written to XML
    ${output} =    Get File    ${OUTFILE}
    ${exp} =    Catenate    SEPARATOR=\\r?\\n
    ...    (?s)    <statistics>    <total>    .*    </total>
    ...    <tag>    .*    </tag>    <suite>    .*    </suite>    </statistics>
    Should Match Regexp    ${output}    ${exp}

Total statistics should be Correct
    ${stats} =    Get Element    ${OUTFILE}    statistics/total
    ${crit}    ${total} =    Call Method    ${stats}    findall    stat
    Node Should Be Correct    ${crit}    Critical Tests    5    1
    Node Should Be Correct    ${total}    All Tests    10    1

Tag statistics should be Correct
    ${stats} =    Get Element    ${OUTFILE}    statistics/tag
    Tag Node Should Be Correct    ${stats[0]}    t1
    ...    5    1    info=critical    links=my title:http://url.to:::title:url
    Tag Node Should Be Correct    ${stats[2]}    D1 OR sub3 OR t2 OR or and not
    ...    4    0    info=combined    combined=D1 OR sub3 OR t2 OR or and not
    Tag Node Should Be Correct    ${stats[3]}    f1 AND t1
    ...    5    1    info=combined    combined=f1 AND t1
    Tag Node Should Be Correct    ${stats[4]}    F1 NOT T1
    ...    4    0    info=combined    combined=F1 NOT T1
    Tag Node Should Be Correct    ${stats[5]}    NOT t1
    ...    5    0    info=combined    combined=NOT t1
    Tag Node Should Be Correct    ${stats[6]}    d1
    ...    1    0    links=title:url
    Tag Node Should Be Correct    ${stats[7]}    d2
    ...    1    0
    Tag Node Should Be Correct    ${stats[8]}    f1
    ...    9    1    doc=this is tagdoc    links=title:url
    Tag Node Should Be Correct    ${stats[9]}    sub3
    ...    2    0
    Tag Node Should Be Correct    ${stats[10]}    XXX
    ...    10    1

Combined Tag Statistics Name Can Be Given
    ${stats} =    Get Element    ${OUTFILE}    statistics/tag
    Tag Node Should Be Correct    ${stats[1]}    Combined tag with new name AND-OR-NOT
    ...    1    0    info=combined    combined=d1 AND d2

Suite statistics should be Correct
    ${stats} =    Get Element    ${OUTFILE}    statistics/suite
    Suite Node Should Be Correct    ${stats[0]}    Suites    10    1
    Suite Node Should Be Correct    ${stats[1]}    Suites.Fourth    0    1
    Suite Node Should Be Correct    ${stats[2]}    Suites.Subsuites    2    0
    Suite Node Should Be Correct    ${stats[3]}    Suites.Subsuites2    3    0
    Suite Node Should Be Correct    ${stats[4]}    Suites.Tsuite1    3    0
    Suite Node Should Be Correct    ${stats[5]}    Suites.Tsuite2    1    0
    Suite Node Should Be Correct    ${stats[6]}    Suites.Tsuite3    1    0

*** Keywords ***
My Setup
    ${options} =    Catenate
    ...    --critical t1
    ...    --tagdoc f1:this_is_tagdoc
    ...    --tagstatlink t*:http://url.to:my_title
    ...    --tagstatlink ?1:url:title
    ...    --tagstatcombine f1ANDt1
    ...    --tagstatcombine NOTt1
    ...    --tagstatcombine D1ORsub3ORt2_OR_or_and_not
    ...    --tagstatcombine d1ANDd2:Combined_tag_with_new_name_AND-OR-NOT
    ...    --suitestatlevel 2
    ...    --tagstatexclude t2
    ...    --TagStatComb F1NOT_T1
    ...    --SetTag XXX
    Run Tests    ${options}    misc/suites

Node Should Be Correct
    [Arguments]    ${node}    ${name}    ${pass}    ${fail}
    Should be equal    ${node.text}    ${name}
    Should be equal    ${node.attrib['pass']}    ${pass}
    Should be equal    ${node.attrib['fail']}    ${fail}

Tag Node Should Be Correct
    [Arguments]    ${node}    ${name}    ${pass}    ${fail}    ${info}=    ${doc}=    ${links}=    ${combined}=
    Node Should Be Correct    ${node}    ${name}    ${pass}    ${fail}
    Should be equal    ${node.attrib.get('info', '')}    ${info}
    Should be equal    ${node.attrib.get('doc', '')}     ${doc}
    Should be equal    ${node.attrib.get('links', '')}    ${links}
    Should be equal    ${node.attrib.get('combined', '')}    ${combined}

Suite Node Should Be Correct
    [Arguments]    ${node}    ${name}    ${pass}    ${fail}
    Node Should Be Correct    ${node}    ${name}    ${pass}    ${fail}
