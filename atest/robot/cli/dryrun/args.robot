*** Settings ***
Suite Setup      Run Tests    --dryrun    cli/dryrun/args.robot
Force Tags       regression    pybot    jybot
Resource         atest_resource.robot

*** Test Cases ***
Valid positional args
    Check Test Case    ${TESTNAME}

Too few arguments
    Check Test Case    ${TESTNAME}

Too few arguments for UK
    Check Test Case    ${TESTNAME}

Too many arguments
    Check Test Case    ${TESTNAME}

Valid named args
    Check Test Case    ${TESTNAME}

Invalid named args
    Check Test Case    ${TESTNAME}
