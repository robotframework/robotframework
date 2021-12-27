*** Test Cases ***
Log To Console With Formatting
    Log to console    test right align with hash padding    format=#>60
    Log to console    test middle align with star padding    format=*^60
    Log To Console    test-with-spacepad-and-weird-characters+%?,_\>~}./asdf    format=>60
    Log To Console    message starts here,    format=>44    no_newline=true
    Log To Console    this sentence should be on the same sentence as "message starts here"
    Log to console    test log to stderr    format=>44  stream=stdERR