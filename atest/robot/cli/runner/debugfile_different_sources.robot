*** Settings ***
Resource           atest_resource.robot

*** Variables ***
${CLI OUTDIR}      %{TEMPDIR}${/}cli
${TEST FILE}        cli${/}runner${/}debugfile_different_sources.robot

*** test cases ***
all
    Run Tests         --debugfile=${CLI OUTDIR}${/}debug.log --variable=DEBUGFILE:${CLI OUTDIR}${/}debug.log  ${TEST FILE}  
    Should Contain Tests    ${SUITE}    log from thread process and async
