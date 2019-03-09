*** Test Cases ***
Test Named Arguments with only one named argument
    Named Arg Test    First arg    Second arg    Maybe a third    named=Actually, correct!

Test Named Arguments with only one named argument but we have a escaped egal
    Named Arg Test    Let's try this again    1    <\=    2    named=Correct again!

Test Named Arguments with only one named argument but we have a no escaped egal
    Named Arg Test    One more time    1    <=    2    named=This part fails

Test Named Arguments with only one named argument but we have two no escaped egal
    Named Arg Test    One more time    a=1    <=    2    named=This part fails

Test Named Arguments with two named argument but with a error
    Named Arg Test    One more time    test=1    2      <=     named=This part fails


*** Keywords ***
Named Arg Test
    [Arguments]    @{list}    ${named}=Wrong!   ${test}=ff
    Log    list: @{list}
    Log    named: ${named}
    Log    named: ${test}
