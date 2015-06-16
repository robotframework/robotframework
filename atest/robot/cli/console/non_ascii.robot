*** Settings ***
Suite Setup  Run Tests  --name Hyvää_Üötä_€åppa  parsing/utf8_data.robot
Force Tags   regression   pybot  jybot
Resource     console_resource.robot


*** Test Cases ***

Non-ascii characters in suite name and documentation
    Check stdout contains regexp  
    ...  Hyvää Üötä [€?]åppa :: Testing that reading and writing of Unicode \\(äöå .½[€?] et\\.\\.\\.

Non-ascii characters in test name and documentation
    Check stdout contains regexp
    ...  UTF-8 Name Äöå .½[€?]" :: Quote is actually plain ASCII but there was... | FAIL |
    Check stdout contains regexp
    ...  UTF-8 :: äöå .½[€?]

Non-ascii error message
    Check stdout contains regexp
    ...  Virheessäkin on ääkkösiä: Äöå .½[€?]"
