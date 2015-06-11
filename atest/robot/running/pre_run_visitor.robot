*** Settings ***
Force Tags     pybot    jybot    regression
Resource       atest_resource.robot

*** Test Cases ***
Visitor as path
    Run Tests    --prerunvisitor ${CURDIR}/PreRunVisitor.py    misc/pass_and_fail.robot
    Check Test Tags    Pass    force    pass    visited
    Length Should Be    ${SUITE.tests}    1

Visitor as name
    Run Tests    --prerunvisitor PreRunVisitor --pythonpath ${CURDIR}    misc/pass_and_fail.robot
    Check Test Tags    Pass    force    pass    visited
    Length Should Be    ${SUITE.tests}    1

Visitor with arguments separated with ':'
    Run Tests    --PreRunVisitor ${CURDIR}/PreRunVisitor.py:new:tags    misc/pass_and_fail.robot
    Check Test Tags    Pass    force    new    pass    tags
    Length Should Be    ${SUITE.tests}    1

Visitor with arguments separated with ';'
    Run Tests    --prerun "PreRunVisitor;1;2;3" -P ${CURDIR}    misc/pass_and_fail.robot
    Check Test Tags    Pass    1    2    3    force    pass
    Length Should Be    ${SUITE.tests}    1

Non-existing visitor
    Run Tests    --prerunvisitor NobodyHere    misc/pass_and_fail.robot
    Stderr Should Match
    ...    [ ERROR ] Importing pre-run visitor 'NobodyHere' failed: ImportError:
    ...    No module named NobodyHere\nTraceback (most recent call last):\n*
    Check Test Case    Pass
    Check Test Case    Fail

Invalid visitor
    Run Tests    --prerunvisitor ${CURDIR}/PreRunVisitor.py:FAIL:Message    misc/pass_and_fail.robot
    Stderr Should Match
    ...    [ ERROR ] Executing pre-run visitor 'PreRunVisitor' failed:
    ...    Message\nTraceback (most recent call last):\n*
    Check Test Case    Pass
    Check Test Case    Fail
