*** Test Cases ***
Log To Console With Formatting
    Stdout Should Contain    ************test middle align with star padding*************
    Stdout Should Contain    ####################test right align with hash padding
    Stdout Should Contain    ${SPACE * 6}test-with-spacepad-and-weird-characters+%?,_\>~}./asdf
    Stdout Should Contain    ${SPACE * 24}message starts here,this sentence should be on the same sentence as "message starts here"
    Stderr Should Contain    ${SPACE * 26}test log to stderr