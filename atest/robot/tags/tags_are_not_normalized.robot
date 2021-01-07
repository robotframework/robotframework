*** Settings ***
Suite Setup       Run Tests    --include upper --include onespace --include HYP-HENandD.O.T.S. --include A? --include HeLLo --include TAG --exclude exclude --exclude EXCLUDE2    tags/tags_are_not_normalized.robot
Resource          atest_resource.robot

*** Test Cases ***
Case Is Not Altered
    Check Test Tags    Case Is Not Altered    lower    MiXeD    UPPER

Spaces Are Not Removed
    Check Test Tags    Spaces Are Not Removed    2 \ spaces    One space    Seven${SPACE*7}spaces

Undersscores and similar are not removed
    Check Test Tags    Undersscores and similar are not removed    !"#%&/()=    hyp-HEN and d.o.t.s.    _under_scores_

Sorting Is Normalized
    Check Test Tags    Sorting Is Normalized    A 0    a1    A2

Normalized Duplicates Are Removed
    Check Test Tags    Normalized Duplicates Are Removed    hello

Statistics Are Counted In Normalized Manner
    Should Be Equal    ${STATISTICS.tags.tags['tag'].failed}    ${5}

Including And Excluding Works in Normalized Manner
    [Documentation]    Including is actually tested using --include when running tests. If all previous tests pass then including works.
    Should Not Contain Tests    ${SUITE}    Excluded

Rebot Keeps Tags In Original Format
    Copy Previous Outfile
    Run Rebot    --exclude LOWER --exclude 2spaces --exclude *D?O?T?S* --settag "Added tag"    ${OUTFILE COPY}
    Check Test Tags    Sorting Is Normalized    A 0    a1    A2    Added tag
    Check Test Tags    Normalized Duplicates Are Removed    Added tag    hello
    Should Be Equal    ${STATISTICS.tags.tags['tag'].failed}    ${5}
