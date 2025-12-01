*** Settings ***
Library           String

*** Test Cases ***
Remove String
    ${result} =    Remove String    RobotFramework    o
    Should Be Equal    ${result}    RbtFramewrk
    ${result} =    Remove String    RobotFramework    no match
    Should Be Equal    ${result}    RobotFramework

Remove String Multiple Removables
    ${result} =    Remove String    RobotFramework    o    wrk
    Should Be Equal    ${result}    RbtFrame

Remove String Non-ASCII characters
    ${result} =    Remove String    Robot\u2603Framew\u2603ork    \u2603
    Should Be Equal    ${result}    RobotFramework
    ${result} =    Remove String    R\x00obotFramework    \x00
    Should Be Equal    ${result}    RobotFramework

Remove String with bytes
    ${result} =    Remove String    ${{b"RobotFramework"}}    ${{b"o"}}    ${{b"ame"}}    rk
    Should Be Equal    ${result}    RbtFrw    type=bytes

Remove String Using Regexp
    ${result} =    Remove String Using Regexp    RobotFramework    F.*k
    Should Be Equal    ${result}    Robot
    ${result} =    Remove String Using Regexp    RobotFramework    f.*k    flags=I
    Should Be Equal    ${result}    Robot
    ${result} =    Remove String Using Regexp    RobotFrame\nwork    f.*k    flags=IGNORECASE|DOTALL
    Should Be Equal    ${result}    Robot
    ${result} =    Remove String Using Regexp    RobotFramework    no match
    Should be equal    ${result}    RobotFramework

Remove String Using Regexp Multiple Patterns
    ${result} =    Remove String Using Regexp    RobotFramework    o.o    r.*w
    Should Be Equal    ${result}    RtFork
    ${result} =    Remove String Using Regexp    RobotFrame\nwork    o.o    f.*w    flags=IGNORECASE|DOTALL
    Should Be Equal    ${result}    Rtork

Remove String Using Regexp with bytes
    ${result} =    Remove String Using Regexp   ${{b"RobotFramework"}}    ${{b"o"}}    ${{b"a.."}}    [kr]{2}
    Should Be Equal    ${result}    RbtFrw    type=bytes
