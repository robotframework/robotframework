*** Settings ***
Test Metadata     Owner       QA Team
Test Metadata     Priority    Normal
Task Metadata     Alias       Task Metadata is an alias
Test Metadata     Multi       Value in
...                           multiple rows
Test Metadata     Variable    ${VALUE}
Test Metadata     Removed     Removed later in this file
Test Metadata     -Removed

*** Variables ***
${VALUE}          resolved
${HYPHEN}         -Owner

*** Test Cases ***
Use defaults
    No Operation

Override default
    [Metadata]    Priority    Critical
    No Operation

Add new
    [Metadata]    Issue    4409
    No Operation

Remove default
    [Metadata]    -Owner
    No Operation

Remove is normalized
    [Metadata]    -o_w n e r
    No Operation

Remove non-existing
    [Metadata]    -Nonex
    No Operation

Remove does not support patterns
    [Metadata]    -Priorit*
    No Operation

Escaped hyphen is literal
    [Metadata]    \-Literal    value
    No Operation

Name from variable is not removal
    [Metadata]    ${HYPHEN}    value
    No Operation
