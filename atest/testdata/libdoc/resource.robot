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
...  | foo      |    bar    |
...  tabs \t\t\t here


*** Keywords ***
kw  [Documentation]  foo bar `kw 2`.
    No Operation

Keyword with some "stuff" to <escape>
    [Documentation]   foo bar `kw` & some "stuff" to <escape> .\n\nbaa `${a1}`
    [Arguments]  ${a1}   ${a2}
    No Operation

kw 3
    [Documentation]   literal\nnewline
    [Arguments]  ${a1}   @{a2}
    No Operation

kw 4  [Arguments]  ${positional}=default  @{varargs}  &{kwargs}
      [Tags]    kw4    Has    tags    ?!?!??
      No Operation

kw 5  [DocumeNtation]   foo bar `kw`.
      ...
      ...  FIRST `${a1}` alskdj alskdjlajd
      ...  askf laskdjf asldkfj alsdkfj alsdkfjasldkfj END
      ...
      ...  SECOND askf laskdjf _asldkfj_ alsdkfj alsdkfjasldkfj
      ...  askf *laskdjf* END
      ...
      ...  THIRD asldkfj `introduction` alsdkfj http://foo.bar END
      ...  - aaa
      ...  - bbb
      ...
      ...  -------------
      ...
      ...  | = first = | = second = |
      ...  | foo       |    bar     |
      ...
      ...  tags: a, b, ${3}
  No Operation

kw 6
    [Documentation]    Summary line
    ...
    ...                Another line.
    ...                Tags: foo, bar
    [Tags]             foo    dar
    No Operation

Different argument types
    [Arguments]    ${mandatory}    ${optional}=default    @{varargs}
    ...            ${kwo}=default    ${another}    &{kwargs}
    No Operation

Embedded ${arguments}
    No Operation

curdir  [Documentation]  ${CURDIR}
    No Operation

non ascii doc
    [Documentation]    Hyvää yötä.\n\nСпасибо!
    No Operation

Deprecation
    [Documentation]    *DEPRECATED* for some reason.
    No Operation

Private
    [Tags]    robot:private
    No Operation
