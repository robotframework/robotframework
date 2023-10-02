*** Settings ***
Resource          resource_2.robot

*** Variables ***
${STRING}         Hello world!
${INTEGER}        ${42}
${FLOAT}          ${-1.2}
${BOOLEAN}        ${True}
${NONE VALUE}     ${None}
${ESCAPES}        one \\ two \\\\ \${non_existing}
${NO VALUE}       ${EMPTY}
@{LIST WITH NON STRINGS}    ${42}    ${-1.2}    ${True}    ${None}
@{ONE ITEM}       Hello again?
@{LIST}           Hello    again    ?
@{LIST WITH ESCAPES}    one \\    two \\\\    three \\\\\\    \${non_existing}
@{LIST CREATED FROM LIST WITH ESCAPES}    @{LIST WITH ESCAPES}
@{EMPTY LIST}
${lowercase}      Variable name in lower case
@{lowercase list}      Variable name in lower case
${S P a c e s }    Variable name with spaces
@{s P a c es li s t}    Variable name with spaces
${UNDER_scores}    Variable name with under scores
@{_u_n_d_e_r___s_c_o_r_e_s__l_i_s_t_}    Variable name with under scores
${ASSIGN MARK} =   This syntax works starting from 1.8
@{ASSIGN MARK LIST} =   This syntax works    starting    from    ${1.8}
${PRIORITIES 1}    Resource File
${PRIORITIES 2}    Resource File
${PRIORITIES 3}    Resource File
${PRIORITIES 4}    Resource File
${DEFINITION IN SAME RESOURCE}    ${PRIORITIES 4}
${DEFINITION IN SECOND RESOURCE}    ${PRIORITIES 5}
