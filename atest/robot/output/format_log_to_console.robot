*** Settings ***
Library    Process
Library    OperatingSystem
*** Test Cases *** 
No formatting
    Log To Console  no format
Center align log to console with star padding
    Log to console  hello console  format=*^78
Right align log to console with hastag padding
    Log to console  test123$#@!$  format=#>32
Right align log to console with space padding
    Log To Console  +000000120\./asdf  format=>30
Test if formatting works with no_newline argument
    Log To Console  message starts here,  format=>44  no_newline=true
    Log To Console  this sentence should be on the same sentence as "message starts here"
Test if formatting works with stderr argument
    Log to console  log to stderr  format=>44  stream=STDERR