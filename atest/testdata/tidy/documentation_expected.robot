*** Settings ***
Documentation     Hello
...               - list
...               - <world>

*** Test Cases ***
Multiline
    [Documentation]    Hillo    # I can has comment!
    ...    | table |
    ...    | world |

Multiple paragraphs
    [Documentation]    Hello
    ...
    ...    Huhuu

Multiline with manual line separators
    [Documentation]    Hillo
    ...    on
    ...    hyvää!

One line
    [Documentation]    One line

Empty

None
    No Operation

Comments
    [Documentation]    First line    # First comment    #Middle comment    ###Last comment###
    ...    Middle line
    ...    Last line

*** Keywords ***
Keyword doc
    [Documentation]    Multi
    ...    line
    ...    stuff
