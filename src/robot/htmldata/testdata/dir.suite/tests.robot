*** Settings ***
Documentation     Some suite _docs_ with links: http://robotframework.org
Suite Setup       Log    Suite setup
Suite Teardown    Fail
Test Setup        Log    Test Setup
Test Teardown     Log    Test Teardown
Metadata          home *page*    http://robotframework.org
Metadata          < &lt; ä       < &lt; ä
Force Tags        force    with space    < &lt; ä
Default Tags      default with percent %
Library           pölkü/myLib.py

*** Variables ***
@{list}           1    2    3    4

*** Test Cases ***
Simple
    Log  do nothing

Long
    [Tags]    long1    long2    long3
    Sleep    0.5 seconds

Longer
    [Tags]    long2    long3
    Sleep    0.7 second

Longest
    [Tags]    long3    *kek*kone*
    Sleep    2 seconds

Log HTML
    [Documentation]    This test uses _*formatted*_ HTML.
    ...  | Isn't | that | _cool?_ |
    [Tags]   !"#%&/()=
    Log   <blink><b><font face="comic sans ms" size="42" color="red">CAN HAZ HMTL & NO CSS?!?!??!!?</font></b></blink>  HTML
    Log   <table><tr><td>This table<td>should have<tr><td>no special<td>formatting</table>  HTML
    Log   escape < &lt; <b>no bold</b>
    Fail  escape < &lt; <b>no bold</b>

Long doc with formatting
    [Documentation]    This test has a pretty long documentation.
    ...
    ...    It contains multiple rows in source and
    ...    multiple paragraphs in HTML.
    ...
    ...    It has URLs like http://robotframework.org and
    ...    [http://robotframework.org|custom links].
    ...
    ...    - lists
    ...    - tooooo
    ...
    ...    | as wel | as |
    ...    | tables | !! |
    No Operation

Non-ASCII 官话
    [Documentation]   with nön-äscii 官话
    [Tags]   with nön-äscii 官话  \u2603  \U0001F435
    Log  hyvää joulua \u2603 \U0001F435
    ${long enough to be zipped} =    Evaluate    u'\\u2603 \\U0001F435 ' * 1000
    Log    ${long enough to be zipped}

Complex
    [Setup]   Log   in own setup
    [Teardown]    Log   in own teardown
    [Documentation]    Test doc
    [Tags]    t1  owner-kekkonen
    Log   in test
    User Kw
    ::FOR  ${i}  IN  @{list}
    \    Log   Got ${i}

Log levels
    Log     This is a WARNING!\n\nWith multiple lines.      WARN
    Log     This is info            INFO
    Log     This is debug           DEBUG

Multi-line failure
    [Template]    Fail
    First failure
    Second failure\nhas multiple\nlines

Escape JS </script> " http://url.com
    [Documentation]    </script>
    [Tags]    </script>
    Log    </script>
    kw http://url.com
    </script>

Escape stuff logged as HTML
    Log    <b id='dynamic'></b><script>document.getElementById('dynamic').innerHTML = 'dynamic'</script>    HTML
    Fail    *HTML* <b>HTML</b></script>

Long messages
    ${msg1} =    Evaluate    'HelloWorld' * 100
    ${msg2} =    Evaluate    (('Hello, world! ' * 100) + '\\n\\n') * 5
    Log    ${msg1}    WARN
    Log    ${msg2}    WARN
    Run Keyword And Continue on Failure    Fail    ${msg1}
    Fail    ${msg2}

Tags
    [Tags]    test    haz    own    tagz
    Keyword with tags

*** Keywords ***
User Kw
    Log   in User Kw

</script>
    Fail    </script>

kw http://url.com
    No Operation

Keyword with tags
    [Tags]    i    can    haz    tägs    ?!?!?!    <&§¢'"</script>
    No Operation
