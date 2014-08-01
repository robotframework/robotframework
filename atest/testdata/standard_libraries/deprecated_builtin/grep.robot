*** Variables ***
${TEXT}  foo\nbar\nfoo bar\nFoo

*** Test Cases ***
Grep Literal
    :FOR  ${pattern}  ${type}  ${exp}  IN  foo  ${EMPTY}  foo\nfoo bar
    ...  o b  ${EMPTY}  foo bar  Foo  not matching any predefined type  Foo  ${EMPTY}
    ...  ${EMPTY}  ${TEXT}  Should Match  ${EMPTY}  ${EMPTY}
    \  Verify grep  ${pattern}  ${type}  ${exp}

Grep Case Insensitive
    :FOR  ${pattern}  ${type}  ${exp}  IN  foo  case insensitive  foo\nfoo bar\nFoo
    ...  BAR  this is CASE InsensitivE  bar\nfoo bar  ${EMPTY}  case insensitive  ${TEXT}  Should Match
    ...  case insensitive  ${EMPTY}
    \  Verify grep  ${pattern}  ${type}  ${exp}

Grep Simple Pattern
    :FOR  ${pattern}  ${type}  ${exp}  IN  foo*  Simple Pattern  foo\nfoo bar
    ...  *  glob  ${TEXT}  ${EMPTY}  glob  ${TEXT}  Should Match
    ...  glob  ${EMPTY}
    \  Verify grep  ${pattern}  ${type}  ${exp}

Grep Regexp
    :FOR  ${pattern}  ${type}  ${exp}  IN  foo|bar  regexp  foo\nbar\nfoo bar
    ...  (?i)foo|bar  regexp  foo\nbar\nfoo bar\nFoo  [a-f]o*|b[a-r]*  regular expression  foo\nbar\nfoo bar  ${EMPTY}
    ...  regexp  ${TEXT}  Should Match  regular expression  ${EMPTY}
    \  Verify grep  ${pattern}  ${type}  ${exp}

Regexp Escape
    ${escaped} =  Regexp Escape  f$o^o$b[a]r()?\\
    Should Be Equal  ${escaped}  f\\$o\\^o\\$b\\[a\\]r\\(\\)\\?\\\\
    Should Match Regexp  f$o^o$b[a]r()?\\  ${escaped}
    @{patterns} =  Create List  $  ^  $  [  ]  so%me&te[]?*x*t
    @{escaped} =  Regexp Escape  @{patterns}
    Should Be True  @{escaped} == ['\\$', '\\^', '\\$', '\\[', '\\]', 'so\\%me\\&te\\[\\]\\?\\*x\\*t']


*** Keywords ***
Verify Grep
    [Arguments]  ${pattern}  ${pattern_type}  ${exp_result}  ${grep_text}=${TEXT}
    ${res} =  Grep  ${grep_text}  ${pattern}  ${pattern_type}
    Should Be Equal  ${res}  ${exp_result}

