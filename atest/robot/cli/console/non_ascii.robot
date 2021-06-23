*** Settings ***
Suite Setup       Run Tests    --name "Hyvää Üötä €åppa"    parsing/utf8_data.robot
Test Template     Stdout Should Contain Regexp
Resource          console_resource.robot

*** Test Cases ***
Non-ascii characters in suite name and documentation
    Hyvää Üötä [€?]åppa :: Testing that reading and writing of Unicode \\(äöå .½[€?] et\\.\\.\\.

Non-ascii characters in test name and documentation
    UTF-8 Name Äöå .½[€?]" :: Quote is actually plain ASCII but there was... | FAIL |
    UTF-8 :: äöå .½[€?]

Non-ascii error message
    Virheessäkin on ääkkösiä: Äöå .½[€?]"
