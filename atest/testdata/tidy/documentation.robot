*** Settings ***
Documentation    Hello
...    - list
...    - <world>

*** Test Cases ***
Multiline
    [ DocuMentation ]    Hillo    # I can has comment!
    ...  | table |
    ...  | world |
Multiple paragraphs
    [Documentation]    Hello
    ...
    ...                Huhuu
Multiline with manual line separators
    [Document]    Hillo\non\n hyvää!
One line
    [Documentation]    One line
Empty
    [Documentation]
None
    No Operation
Comments
    [Documentation]    First line    # First comment
    ...    Middle line               #Middle comment
    ...    Last line    ###Last comment###

*** Keywords ***
Keyword doc
    [Documentation]  Multi
    ...  line\nstuff
