*** Test Cases ***
Test With Metadata
    [Metadata]    Owner     Team Robot
    [Metadata]    Ticket    RF-4409
    [Metadata]    Escape    not <b>bold</b> & <extra>
    [Metadata]    Format    *bold* & <extra>
    No Operation

Test Without Metadata
    No Operation
