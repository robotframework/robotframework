*** Test Cases ***    header1            header2
My Test Case          [Documentation]    This is a long comment that spans several columns
                      My TC Step 1       my step arg                                          # step 1 comment
                      My TC Step 2       my step \ 2 arg                                      second arg          # step 2 comment
                      [Teardown]         1 minute

A very long named test case
                      My step 1          This is arg
                      My step 2          This also is arg

Test with for         FOR                ${i}                                                 IN RANGE            100
                                         Log                                                  ${i}
                      END
