*** Settings ***
Resource      libdoc_resource.robot
Test Setup    Remove Output Files
Force Tags    require-docutils    require-pygments

*** Test Cases ***
Native links, shared targets and headerless examples
    Run Libdoc And Parse Model From HTML    ${TESTDATADIR}/DocFormatRest.py
    Should Contain    ${MODEL}[doc]    href="#My%20Keyword"
    Should Contain    ${MODEL}[keywords][1][doc]    href="#examples"
    Should Contain    ${MODEL}[keywords][1][doc]    href="https://example.com/robot"
    Should Contain    ${MODEL}[keywords][1][doc]    href="#Introduction"
    Should Contain    ${MODEL}[keywords][1][doc]    class="nf"
    Should Contain    ${MODEL}[keywords][1][doc]    class="nv"
    Should Not Contain    ${MODEL}[keywords][1][doc]    *** Keywords ***
    Should Contain    ${MODEL}[keywords][0][doc]    href="https://example.com/local"
    Should Contain    ${MODEL}[keywords][0][doc]    href="#My%20Keyword"

Parameter fields in HTML documentation
    Run Libdoc And Parse Model From HTML    ${TESTDATADIR}/DocFormatRest.py
    Should Contain    ${MODEL}[keywords][1][doc]    Parameters
    Should Contain    ${MODEL}[keywords][1][doc]    (str)
    Should Contain    ${MODEL}[keywords][1][doc]    (int)
    Should Contain    ${MODEL}[keywords][1][doc]    <strong>user</strong>
    Should Contain    ${MODEL}[keywords][1][doc]    This field is preserved.

Raw JSON preserves reStructuredText source
    [Tags]    require-jsonschema
    Run Libdoc And Parse Model From JSON    --specdocformat RAW ${TESTDATADIR}/DocFormatRest.py
    Should Be Equal    ${MODEL}[docFormat]    REST
    Should Contain    ${MODEL}[keywords][1][doc]    :param str name:
    Should Contain    ${MODEL}[keywords][1][doc]    examples_
