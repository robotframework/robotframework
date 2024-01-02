*** Settings ***
Documentation   Tests for automatic variables related to result files like \${OUTPUT_DIR} and  \${LOG_FILE}.
Resource        atest_resource.robot

*** Test Cases ***
Result file variables as absolute paths
    Run Tests    --log mylog.html --report myreport.html --debugfile %{TEMPDIR}/mydebug.txt    variables/outputfile_variables
    Outputfile Variables Should Contain Correct Paths    Log All Output Files In Toplevel
    ...    ${OUTDIR}    ${OUTFILE}    ${OUTDIR}${/}mylog.html    ${OUTDIR}${/}myreport.html    %{TEMPDIR}${/}mydebug.txt
    Outputfile Variables Should Contain Correct Paths    Log All Output Files In Sublevel
    ...    ${OUTDIR}    ${OUTFILE}    ${OUTDIR}${/}mylog.html    ${OUTDIR}${/}myreport.html    %{TEMPDIR}${/}mydebug.txt
    Check Test Case    Result file variables are strings

Result file variables as NONE string
    Run Tests  --log none --report NONE  variables/outputfile_variables
    Outputfile Variables Should Contain Correct Paths    Log All Output Files In Toplevel
    ...    ${OUTDIR}    ${OUTFILE}    NONE    NONE    NONE
    Outputfile Variables Should Contain Correct Paths    Log All Output Files In Sublevel
    ...    ${OUTDIR}    ${OUTFILE}    NONE    NONE    NONE
    Check Test Case    Result file variables are strings

*** Keywords ***
Outputfile Variables Should Contain Correct Paths
    [Arguments]    ${test name}    @{files}
    ${tc} =    Check Test Case    ${test name}
    FOR    ${index}    ${file}    IN ENUMERATE    @{files}
        Check Log Message    ${tc.body[0].msgs[${index}]}    ${file}
    END

