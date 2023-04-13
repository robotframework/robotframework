*** Settings ***
Suite Setup       My Setup
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
    ${total} =    Call Method    ${stats}    find    stat
    Node Should Be Correct    ${total}    All Tests    12    1

Tag statistics should be Correct
    ${stats} =    Get Element    ${OUTFILE}    statistics/tag
    Tag Node Should Be Correct    ${stats[1]}    D1 OR sub3 OR t2 OR or and not
    ...    4    0    info=combined    combined=D1 OR sub3 OR t2 OR or and not
    Tag Node Should Be Correct    ${stats[2]}    f1 AND t1
    ...    5    1    info=combined    combined=f1 AND t1
    Tag Node Should Be Correct    ${stats[3]}    F1 NOT T1
    ...    4    0    info=combined    combined=F1 NOT T1
    Tag Node Should Be Correct    ${stats[4]}    NOT t1
    ...    7    0    info=combined    combined=NOT t1
    Tag Node Should Be Correct    ${stats[5]}    d1
    ...    1    0    links=title:url
    Tag Node Should Be Correct    ${stats[6]}    d2
    ...    1    0
    Tag Node Should Be Correct    ${stats[7]}    f1
    ...    9    1    doc=this is tagdoc    links=title:url
    Tag Node Should Be Correct    ${stats[8]}    sub3
    ...    2    0
    Tag Node Should Be Correct    ${stats[9]}    t1
    ...    5    1    links=my title:http://url.to:::title:url
    Tag Node Should Be Correct    ${stats[10]}    XXX
    ...    12    1

Combined Tag Statistics Name Can Be Given
    ${stats} =    Get Element    ${OUTFILE}    statistics/tag
    Tag Node Should Be Correct    ${stats[0]}    Combined tag with new name AND-OR-NOT
    ...    1    0    info=combined    combined=d1 AND d2

Suite statistics should be correct
    ${stats} =    Get Element    ${OUTFILE}    statistics/suite
    Suite Node Should Be Correct    ${stats[0]}    Suites    12    1
    Suite Node Should Be Correct    ${stats[1]}    Suites.Suite With Prefix    1    0
    Suite Node Should Be Correct    ${stats[2]}    Suites.Fourth    0    1
    Suite Node Should Be Correct    ${stats[3]}    Suites.Subsuites    2    0
    Suite Node Should Be Correct    ${stats[4]}    Suites.Custom name for 📂 'subsuites2'    3    0
    Suite Node Should Be Correct    ${stats[5]}    Suites.Suite With Double Underscore    1    0
    Suite Node Should Be Correct    ${stats[6]}    Suites.Tsuite1    3    0
    Suite Node Should Be Correct    ${stats[7]}    Suites.Tsuite2    1    0
    Suite Node Should Be Correct    ${stats[8]}    Suites.Tsuite3    1    0

*** Keywords ***
My Setup
    ${options} =    Catenate
    ...    --tagdoc "f1:this is tagdoc"
    ...    --tagstatlink "t*:http://url.to:my title"
    ...    --tagstatlink ?1:url:title
    ...    --tagstatcombine f1ANDt1
    ...    --tagstatcombine NOTt1
    ...    --tagstatcombine D1ORsub3ORt2_OR_or_and_not
    ...    --tagstatcombine "d1ANDd2:Combined tag with new name AND-OR-NOT"
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
