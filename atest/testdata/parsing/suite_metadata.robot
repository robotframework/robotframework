*** Settings ***
Resource  ../core/resources.robot

Metadata  Name  Value
MetadatA  Multiple columns  Value in  multiple  columns
Meta data  multiple lines  Value in  multiple lines  '\n\n'   and with
...  real newlines
MetaData  variables  Version: ${version}
Metadata  Variable from resource  ${resource_file_var}
Metadata  Value from CLI  ${META_VALUE_FROM_CLI}
Metadata  Escaping   Three backslashes \\\\\\
Metadata  Overridden  first value
Metadata  over ridden  This overrides first value
Meta: old style meta  some value

*** Variables ***
${version}  1.2

*** Test Cases ***
Test Case
    No Operation
