*** Settings ***
Force Tags      regression    require-docutils
Resource        formats_resource.robot

*** Test Cases ***
One ReST using code-directive
    Run sample file and check tests  parsing${/}data_formats${/}rest_directives${/}sample.rst
