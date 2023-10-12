.. code:: robotframework

    *** Settings ***
    Resource                rest_directive_resource2.rest
    Invalid Resource        Setting

    *** Variables ***
    ${rest_resource_var}    ReST Resource Variable


.. table:: Tables are ignored if reST files has Robot-directives.

   ==========================  ============
         Test Cases
   ==========================  ============
   I'm not really a test
   ==========================  ============


.. code-block:: robotframework

    *** Keywords ***
    Keyword from REST resource
        No Operation
