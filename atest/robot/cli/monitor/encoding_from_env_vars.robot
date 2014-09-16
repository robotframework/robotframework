*** Settings ***
Force Tags   regression   pybot  jybot
Resource     monitor_resource.robot

*** Variables ***
${TES TFILE}    ${CURDIR}/../../../testdata/misc/pass_and_fail.robot
${STDOUT FILE}  %{TEMPDIR}/redirect_stdout.txt
${STDERR FILE}  %{TEMPDIR}/redirect_stderr.txt

*** Test Cases ***

Invalid Encoding In Environment Variables
    [Tags]  x-exclude-on-windows
    ${stdout}  ${stderr} =  Run Some Tests With Std Streams Redirected
    Should Contain   ${stdout}  Pass And Fail :: Some tests here


*** Keywords ***

Run Some Tests With Std Streams Redirected
  Set Runners
  ${cmd} =  Catenate
  ...  echo "redirect stdin" |
  ...  LANG=invalid LC_TYPE=invalid LANGUAGE=invalid LC_ALL=invalid
  ...  ${ROBOT} --monitorcolors off ${TESTFILE}
  ...  > ${STDOUT FILE} 2> ${STDERR FILE}
  Run  ${cmd}
  ${stdout} =  Log File  ${STDOUT FILE}
  ${stderr} =  Log File  ${STDERR FILE}
  [Return]  ${stdout}  ${stderr}
