*** Settings ***
Test Setup      Create Output Directory
Resource        cli_resource.robot

*** Test Cases ***
Timestamped Outputs
    Run Some Tests  --timestampoutputs
    @{files} =  List Directory  ${CLI OUTDIR}
    Length Should Be  ${files}  3
    :FOR  ${file}  IN  @{files}
    \  Should Match Regexp  ${file}  (log|output|report)-20\\d{6}-\\d{6}\\.(html|xml)

Timestamped Outputs With Names And Split Log
    Run Tests Without Processing Output  -d ${CLI OUTDIR} -T -l l -r r -o o --split  ${TESTFILE}
    @{files} =  List Directory  ${CLI OUTDIR}
    Length Should Be  ${files}  5
    :FOR  ${file}  IN  @{files}
    \  Should Match Regexp  ${file}  (l|o|r)-20\\d{6}-\\d{6}(\\.(html|xml)|-(1|2)\\.js)

Override with --NoTimeStampOutputs
    Run Some Tests  --TimeStampOutputs -T --timestamp --NoTimeStampOutputs
    @{files} =  List Directory  ${CLI OUTDIR}
    Length Should Be  ${files}  3
    :FOR  ${file}  IN  @{files}
    \  Should Match Regexp  ${file}  (log|output|report).(html|xml)
