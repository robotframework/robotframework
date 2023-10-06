*** Settings ***
Suite Setup    Run tests with options containing </script>
Resource       atest_resource.robot

*** Test Cases ***
Strings like </script> are escaped in JS model
    Check test case    </script>
    Model should contain escaped strings    log
    Model should contain escaped strings    report

Strings like </script> logged as HTML are escaped in JS model
    Strings logged as HTML are escaped    log
    Strings logged as HTML are escaped    report

*** Keywords ***
Run tests with options containing </script>
    ${options} =    Catenate
    ...    --log log.html
    ...    --report report.html
    ...    --name </script>
    ...    --logtitle </script>
    ...    --reporttitle </script>
    ...    --tagdoc *:</script>
    ...    --tagstatlink </script>:</script>:</script>
    ...    --tagstatcombine *:</script>:</script>
    Run tests    ${options}    output/js_model.robot

Model should contain escaped strings
    [Arguments]    ${type}
    ${strings}    ${settings} =   Get JS model    ${type}
    Should not contain    ${strings}    </script>
    Should contain    ${strings}    &lt;/script&gt;
    Should not contain    ${settings}    </script>
    Should contain    ${settings}    &lt;/script&gt;

Strings logged as HTML are escaped
    [Arguments]    ${type}
    ${strings}    ${settings} =   Get JS model    ${type}
    Should not contain    ${strings}    </script>
    Should contain    ${strings}    \\x3c/script>

Get JS model
    [Arguments]    ${type}
    ${file} =    Get File    ${OUTDIR}/${type}.html
    ${strings} =    Get Lines Matching Pattern    ${file}    window.output?"strings"?*
    ${settings} =    Get Lines Matching Pattern    ${file}    window.settings =*
    RETURN    ${strings}    ${settings}
