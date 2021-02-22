*** Settings ***
Resource          libdoc_resource.robot
Library           ${TESTDATADIR}/default_escaping.py
Resource          ${TESTDATADIR}/default_escaping.resource
Suite Setup       Run Libdoc And Parse Model From JSON    ${TESTDATADIR}/default_escaping.py

*** Comments ***
This test checks if the libdoc.html presented strings are the ones that can be
pasted directly to robot code and reproduce the same default value.
The first line of each test is that value.
The called keyword checks equality.

*** Test Cases ***
Verify All
    Verify All         first \${scalar} \nthen\t \@{list} and \\\\\&{dict.key}[2] so \ \ \\ \ \ \ me env \%{username} and a \\\${backslash} \ \ \
    Check Libdoc Default    0    first \\\${scalar} \\nthen\\t \\\@{list} and \\\\\\\\\\\&{dict.key}[2] so \\ \\ \\\\ \\ \\ \\ me env \\\%{username} and a \\\\\\\${backslash} \\ \\ \\

Verify Backslash
    Verify Backslash    c:\\windows\\system
    Check Libdoc Default    1    c:\\\\windows\\\\system

Verify Internalvariables
    Verify Internalvariables    first \${sca\${lar}} \ \@{list}[\${4}] \ \&{dict.key}[2] some env \%{\${somename}} and a \\\${backslash}[\${key}] \ \ \
    Check Libdoc Default    2    first \\\${sca\\\${lar}} \\ \\\@{list}[\\\${4}] \\ \\\&{dict.key}[2] some env \\\%{\\\${somename}} and a \\\\\\\${backslash}[\\\${key}] \\ \\ \\

Verify Line Break
    Verify Line Break    Hello\n World!\r\n End...\\n
    Check Libdoc Default    3    Hello\\n World!\\r\\n End...\\\\n

Verify Line Tab
    Verify Line Tab    Hello\tWorld!\t\t End\\t...
    Check Libdoc Default    4    Hello\\tWorld!\\t\\t End\\\\t...

Verify Spaces
    Verify Spaces    \ \ \ \ Hello\tW \ \ orld!\t \ \t En d\\t... \
    Check Libdoc Default    5    \\ \\ \\ \\ Hello\\tW \\ \\ orld!\\t \\ \\t En d\\\\t... \\

Verify Variables
    Verify Variables    first \${scalar} then \@{list} and \&{dict.key}[2] some env \%{username} and a \\\${backslash} \ \ \
    Check Libdoc Default    6    first \\\${scalar} then \\\@{list} and \\\&{dict.key}[2] some env \\\%{username} and a \\\\\\\${backslash} \\ \\ \\

Verify No Escaping on Resource Files
    Run Libdoc And Parse Model From JSON    ${TESTDATADIR}/default_escaping.resource
    Check Scalar in Default    some\${text} and ${scalar} \ ${{'Hello'[1:3]}}\ with\n\t ${Say ${World}} Space
    Check Libdoc Default    0    some\\\${text} and \${scalar} \\ \${{'Hello'[1:3]}}\\ with\\n\\t \${Say \${World}} Space

*** Keywords ***
Check Libdoc Default
    [Arguments]    ${keyword_index}    ${expected}
    Should Be Equal    ${expected}
    ...                ${MODEL}[keywords][${keyword_index}][args][0][defaultValue]
    Log    ${MODEL}[keywords][${keyword_index}][args][0][defaultValue]
