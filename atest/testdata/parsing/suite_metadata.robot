*** Settings ***
Resource         ../core/resources.robot

Metadata        Name                       Value
Metadata        Multiple columns           Value in    multiple    columns
Metadata        multiple lines             Metadata in multiple lines
...             is parsed using
...             same semantics    as    documentation.
...             | table |
...             |   !   |
MetaData        variables                  Version: ${version}
Metadata        Variable from resource     ${resource_file_var}
Metadata        Value from CLI             ${META_VALUE_FROM_CLI}
Metadata        Escaping                   Three backslashes \\\\\\ & \${version}
Metadata        Overridden                 first value
Metadata        over ridden                This overrides first value

*** Variables ***
${version}      1.2

*** Test Cases ***
Test Case
    No Operation
