*** Settings ***
Suite Setup     Run Tests  \  core/list_and_scalar_variables.robot
Force Tags      regression  jybot  pybot
Resource        atest_resource.txt

*** Test Cases ***

List variable as a scalar variable
  Check testcase  status=PASS

Scalar variable as a list variable
  Check testcase  status=PASS

Scalar variable that can not be a list variable
  Check testcase  status=FAIL  message=Non-existing variable '\@{scalar}'.

