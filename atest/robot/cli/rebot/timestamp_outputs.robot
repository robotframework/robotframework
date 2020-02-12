*** Settings ***
Resource          rebot_cli_resource.robot

*** Test Cases ***
Timestamped Outputs
    @{files} =    Run rebot and return outputs    --TimeStampOutputs
    Length Should Be    ${files}    2
    ${timestamp} =    Should Match Regexp    ${files}[0]     20\\d{6}-\\d{6}
    FOR    ${file}    IN    @{files}
        Should Match Regexp    ${file}    ^(log|report)-${timestamp}\\.(html|xml)$
    END

Timestamped Outputs With Custom Names
    @{files} =    Run rebot and return outputs    --timest -l l -r r.html -o o
    Length Should Be    ${files}    3
    ${timestamp} =    Should Match Regexp    ${files}[0]     20\\d{6}-\\d{6}
    FOR    ${file}    IN    @{files}
        Should Match Regexp    ${file}    ^(l|o|r)-${timestamp}\\.(html|xml)$
    END
