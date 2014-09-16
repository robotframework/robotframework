*** Variables ***
${STRING}         Hello world!
${INTEGER}        ${42}
${FLOAT}          ${-1.2}
${BOOLEAN}        ${True}
${NONE VALUE}     ${None}
${ESCAPES}        one \\ two \\\\ \${non_existing}
${NO VALUE}       ${EMPTY}
@{ONE ITEM}       Hello again?
@{LIST}           Hello    again    ?
@{LIST WITH ESCAPES}    one \\    two \\\\    three \\\\\\    \${non_existing}
@{LIST CREATED FROM LIST WITH ESCAPES}    @{LIST WITH ESCAPES}
@{EMPTY LIST}
${lowercase}      Variable name in lower case
@{lowercase}      Variable name in lower case
${S P a c e s }    Variable name with spaces
@{s P a c es }    Variable name with spaces
${UNDER_scores}    Variable name with under scores
@{_u_n_d_e_r___s_c_o_r_e_s_}    Variable name with under scores
${ASSING MARK}    This syntax works starting from 1.8
@{ASSIGN MARK}    This syntax works    starting    from    ${1.8}
${THREE DOTS}     ...
@{3DOTS LIST}     ...   ...
${SCALAR LIST}    I    am    a    scalar     list     with    many     items
${NONEX 1}        Creating variable based on ${NON EXISTING} variable fails.
${NONEX 2A}       This ${NON EX} is used for creating another variable.
${NONEX 2B}       ${NONEX 2A}
${NONEX 3}        This ${NON EXISTING VARIABLE} is used in imports.

*** Settings ***
Resource          ${NONEX 3}
Library           ${NONEX 3}
