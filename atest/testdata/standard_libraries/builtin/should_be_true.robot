*** Settings ***
Variables         variables_to_verify.py

*** Test Cases ***
Should Be True
    [Documentation]    FAIL '1 != 1 and True or False' should be true.
    Should Be True    -1 <= 1 <= 1
    Should Be True    ${TRUE}
    Should Be True    ${LIST 1}
    Should Be True    ${DICT 1}
    Should Be True    1 != 1 and True or False

Should Be True with message
    [Documentation]    FAIL My error message
    Should Be True    False    My error message

Should Be True with invalid expression
    [Documentation]    FAIL STARTS: Evaluating expression '"quotes" != "quote missing' failed: SyntaxError:
    Should Be True    "quotes" != "quote missing

Should Not Be True
    [Documentation]    FAIL '0 < 1' should not be true.
    Should Not Be True    0 > 1
    Should Not Be True    ${FALSE}
    Should Not Be True    ${LIST 0}
    Should Not Be True    ${DICT 0}
    Should Not Be True    0 < 1

Should Not Be True with message
    [Documentation]    FAIL My message
    Should Not Be True    True    My message

Should Not Be True with invalid expression
    [Documentation]    FAIL STARTS: Evaluating expression 'this is invalid' failed: NameError:
    Should Not Be True    this is invalid

Should (Not) Be True automatically imports modules
    Should Be True    os.pathsep == '${:}'
    Should Be True    math.pi > 3.14
    Should Be True    robot.__version__[0] in ('6', '7', '8', '9')
    Should Not Be True    os.sep == 'os.sep'
    Should Not Be True    sys.platform == 'hurd'    # let's see when this starts failing

Should (Not) Be True is evaluated with robot's variables
    Should Be True    $list2
    Should Be True    $list0 == []
    Should Be True   len($list2) == 2
    Should Not Be True   $list0
    Should Not Be True   $list0 == $dict0
