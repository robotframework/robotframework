*** Settings ***
Test Template      Should Be Equal

*** Variables ***
${DEFAULT SEP}     Values    catenated    with    space    by    default
${NEWLINE SEP}     SEPARATOR=\n    Newline    used    as    custom separator
${EMPTY SEP}       SEPARATOR=    Empty    string    as separator
${SEPARATOR}       ---
${VARIABLE SEP}    SEPARATOR=${SEPARATOR}    Variable    as    separator
${EXTENDED SEP}    SEPARATOR=${SPACE*3}    Extended variable    as    separator
${NON STRING SEP}  SEPARATOR=${42}    Separator    is    not    string
${NONEX IN SEP}    SEPARATOR=${NON EXISTING}    This fails
${VARIABLE VALUE}  ${EMPTY SEP}    ${SPACE}    ...
${NON STRING 1}    ${0}    1    ${2.0}    ${True}
${NON STRING 2}    SEPARATOR=-    ${0}    1    ${2.0}    ${True}
@{VALUES}          1    2    ${3}    4    5
${@VAR VALUE 1}    @{VALUES}
${@VAR VALUE 2}    SEPARATOR=${EMPTY}    0    @{VALUES}    6    ${7}    8    9
...                ${SPACE}    ${0}    @{VALUES}    6789
${@VAR VALUE 3}    SEPARATOR=@{SEPARATOR.split()}[0]    @{NON STRING 1.split()}
${@VAR VALUE 4}    @{EMPTY}
${NONEX IN VALUE}  Having    ${NON EXISTING}    variable    causes    failure
${ESCAPED}         \SEPARATOR=Default    separator    used
${NON UPPER 1}     separator=not    upper
${NON UPPER 2}     Separator=Not    upper
${NOT FIRST 1}     This    SEPARATOR=is not    used
${NOT FIRST 2}     SEPARATOR==    Only    first    SEPARATOR=    is    used
@{NOT SEPARATOR}   SEPARATOR=This    is    not    separator
${NO SEPARATOR 1}  @{NOT SEPARATOR}
${NO SEPARATOR 2}  @{NOT SEPARATOR}[0]    not    separator    either
${NO SEPARATOR 3}  ${NOT SEPARATOR[0]}    neither
${NO VALUES}

*** Test Cases ***
Default separator is space
    ${DEFAULT SEP}       Values catenated with space by default

Custom separator
    ${NEWLINE SEP}       Newline\nused\nas\ncustom separator
    ${EMPTY SEP}         Emptystringas separator

Custom separator from variable
    ${VARIABLE SEP}      Variable---as---separator
    ${EXTENDED SEP}      Extended variable${SPACE*3}as${SPACE*3}separator

Non-string separator
    ${NON STRING SEP}    Separator42is42not42string

Non-existing variable in separator
    [Template]    Variable should not exist
    ${NONEX IN SEP}

Value containing variables
    ${VARIABLE VALUE}    Emptystringas separator${SPACE*3}...
    ${NON STRING 1}      0 1 2.0 True
    ${NON STRING 2}      0-1-2.0-True
    ${@VAR VALUE 1}      1 2 3 4 5
    ${@VAR VALUE 2}      0123456789 0123456789
    ${@VAR VALUE 3}      0---1---2.0---True
    ${@VAR VALUE 4}      ${EMPTY}

Non-existing variable in value
    [Template]    Variable should not exist
    ${NONEX IN VALUE}

'SEPARATOR=' can be escaped
    ${ESCAPED}           SEPARATOR=Default separator used

'SEPARATOR=' must be upper case
    ${NON UPPER 1}       separator=not upper
    ${NON UPPER 2}       Separator=Not upper

'SEPARATOR=' must be first
    ${NOT FIRST 1}       This SEPARATOR=is not used
    ${NOT FIRST 2}       Only=first=SEPARATOR==is=used

'SEPARATOR=' cannot come from variable
    ${NO SEPARATOR 1}    SEPARATOR=This is not separator
    ${NO SEPARATOR 2}    SEPARATOR=This not separator either
    ${NO SEPARATOR 3}    SEPARATOR=This neither

Having no values creates empty string
    ${NO VALUES}         ${EMPTY}
