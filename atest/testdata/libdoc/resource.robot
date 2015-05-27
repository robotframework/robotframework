*** Settings ***
Documentation   This resource file has documentation.
...
...  And it is even set in multiple cells with _formatting_.
...  This should be in the same paragraph as the sentence above.
...
...  Here is a literal\nnewline\n
...
...  -------------
...
...  | *TABLE* |
...  | ${NONEX} | ${CURDIR} | ${TEMPDIR} |
...
...  tabs \t\t\t here


*** Keywords ***
kw  [Documentation]  foo bar `kw 2`.
    No Operation

Keyword with some "stuff" to <escape>
    [Documentation]   foo bar `kw` & some "stuff" to <escape> .\n\n baa `${a1}`
    [Arguments]  ${a1}   ${a2}
    No Operation

kw 3
    [Documentation]   literal\nnewline
    [Arguments]  ${a1}   @{a2}

kw 4  [Arguments]  ${positional}=default  @{varargs}  &{kwargs}
      [Tags]    kw4    Has    tags    ?!?!??

kw 5  [Documentation]   foo bar `kw`.
      ...
      ...  baa `${a1}` alskdj alskdjlajd
      ...  askf laskdjf asldkfj alsdkfj alsdkfjasldkfj
      ...  askf laskdjf _asldkfj_ alsdkfj alsdkfjasldkfj
      ...  askf *laskdjf* asldkfj `introduction` alsdkfj
      ...  http://foo.bar
      ...  - aaa
      ...  - bbb
      ...
      ...  -------------
      ...
      ...  | *1* | *2* |
      ...  | foo | bar |
      ...
      ...  tags: a, b, ${3}

kw 6
    [Documentation]    Summary line
    ...
    ...                 Another line.
    ...                 Tags: foo, bar
    [Tags]              foo    dar

Embedded ${arguments}

curdir  [Documentation]  ${CURDIR}

non ascii doc
    [Documentation]    Hyvää yötä.\n\nСпасибо!
