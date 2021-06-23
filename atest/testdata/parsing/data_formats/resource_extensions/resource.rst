.. code:: robotframework

    *** Settings ***
    Resource    nested.resource

    *** Variables ***
    ${RST}      resource.rst

    *** Keywords ***
    Keyword in resource.rst
        Keyword in nested.resource
        Should Be Equal    ${NESTED}      nested.resource
        Should Be Equal    ${RST}    resource.rst
