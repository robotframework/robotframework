*** Settings ***
Documentation   Tests for automatic variables \${OUTPUT_FILE}, \${LOG_FILE} and \${REPORT_FILE}
Resource        atest_resource.robot

*** Test Cases ***
Outputfile Variables Should Contain Absolute Paths To Outputfiles
    Run Tests  --log mylog.html --report myreport.html --debugfile mydebug.txt  variables/outputfile_variables
    ${tc} =  Check Test Case  Log All Output Files In Toplevel
    Outputfile Variables Should Contain Correct Paths  ${tc}  ${OUTFILE}  ${OUTDIR}${/}mylog.html  ${OUTDIR}${/}myreport.html  ${OUTDIR}${/}mydebug.txt  ${OUTDIR}
    ${tc} =  Check Test Case  Log All Output Files In Sublevel
    Outputfile Variables Should Contain Correct Paths  ${tc}  ${OUTFILE}  ${OUTDIR}${/}mylog.html  ${OUTDIR}${/}myreport.html  ${OUTDIR}${/}mydebug.txt  ${OUTDIR}

Default value of outputfile Variables Other than ${OUTPUTDIR} and ${OUTPUTFILE} Is NONE
    Run Tests  --log none --report NONE  variables${/}outputfile_variables
    ${tc} =  Check Test Case  Log All Output Files In Toplevel
    Outputfile Variables Should Contain Correct Paths  ${tc}  ${OUTFILE}  NONE  NONE  NONE  ${OUTDIR}
    ${tc} =  Check Test Case  Log All Output Files In Sublevel
    Outputfile Variables Should Contain Correct Paths  ${tc}  ${OUTFILE}  NONE  NONE  NONE  ${OUTDIR}


*** Keywords ***
Outputfile Variables Should Contain Correct Paths
    [Arguments]    ${test}    @{files}
    FOR    ${index}    ${file}    IN ENUMERATE    @{files}
        Check Log Message    ${test.kws[0].msgs[${index}]}    ${file}
    END

