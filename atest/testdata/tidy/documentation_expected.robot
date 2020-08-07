When editing this file, make sure your editor doesn't remove trailing spaces!

*** Settings ***
Documentation     Hello
...
...               No extra spaces should be added to the above line.
# Trailing spaces everywhere!!
...
...               Trailing spaces should be removed from this line and 2 lines above.
...
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
    ...
    ...    Also trailing spaces.

Multiline with manual line separators
    [Documentation]    Hillo\non\n hyvää!

One line
    [Documentation]    One line

Empty

None
    No Operation

Comments
    [Documentation]    First line    # First comment
    ...    Middle line    #Middle comment
    ...    Last line    ###Last comment###

*** Keywords ***
Keyword doc
    [Documentation]    Multi
    ...    line\nstuff
