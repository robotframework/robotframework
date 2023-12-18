*** Settings ***
Test Template               Should be equal

*** Variables ***
${X}                        X
@{LIST}                     a      b      c
&{DICT}                     a=A    b=B    c=C

${PYTHON ONLY}              ${{1 + 2 - 3}}
${VARIABLES}                ${{"${SUITE NAME}"}}
${A START}                  ${{1}}     # These variables are internally resolved in
${Z END}                    ${{11}}    # alphabetical order. Test that it is OK.
${INLINE VARIABLES}         ${{ ', '.join(str(i) for i in range($A_START, $Z_END)) }}
${MODULE IMPORTS}           ${{os.path.join('foo', re.escape('bar'))}}

${NON EXISTING VARIABLE}    ${{$i_do_not_exist}}
${NON EXISTING MODULE}      ${{i_do_not_exist}}
${INVALID EXPRESSION}       ${{ 1/0 }}
${INVALID SYNTAX}           ${{ 1/1 }
${RECURSION}                ${{ $RECURSION }}
${RECURSION INDIRECT}       ${{ $INDIRECT_RECURSION }}
${INDIRECT RECURSION}       ${{ $RECURSION_INDIRECT }}

*** Test Cases ***
Python only
    ${{'Hello, world!'}}                        Hello, world!
    ${{''}}                                     ${EMPTY}
    ${{ " " }}                                  ${SPACE}
    ${{42}}                                     ${42}
    ${{ 1 + 2 }}                                ${3}
    ${{['a', 'b', 'c']}}                        ${LIST}
    ${{[i for i in ('a', 'b', 'c')]}}           ${LIST}
    ${{{'a': 'A', 'b': 'B', 'c': 'C'}}}         ${DICT}
    ${{ {k: k.upper() for k in 'abc'} }}        ${DICT}

Variable replacement
    ${{"${TEST NAME}"}}                         Variable replacement
    ${{ '${:}' }}                               ${:}
    ${{${4}${2}}}                               ${42}
    ${{${LIST}}}                                ${LIST}
    ${{ ${DICT} }}                              ${DICT}
    ${{'${LIST}[0]'}}                           a
    ${{'${DICT}[${LIST}[${1}]]'}}               B

Inline variables
    ${{$X}}                                     X
    ${{$x}}                                     X
    ${{ '-'.join([$X, $x, "$X", "${X}"]) }}     X-X-$X-X
    ${{ $A_START + $zend }}                     ${12}
    ${{$LIST[0]}}                               a
    ${{$DICT[$LIST[1]]}}                        B
    ${{ ', '.join('%s: %s' % item for item in $d_i_c_t.items()) }}
    ...                                         a: A, b: B, c: C

Automatic module import
    ${{os.sep}}                                 ${/}
    ${{round(math.pi, 2)}}                      ${3.14}
    ${{json.dumps([1, None, 'kolme'])}}         [1, null, "kolme"]
    ${{robot.__version__.split('.')[0] in ('6', '7', '8', '9')}}
    ...                                         ${True}

Module imports are case-sensitive
    [Documentation]    FAIL
    ...    Several failures occurred:
    ...
    ...    1) Resolving variable '\${{OS.sep}}' failed: \
    ...    Evaluating expression 'OS.sep' failed: \
    ...    NameError: name 'OS' is not defined nor importable as module
    ...
    ...    2) Resolving variable '\${{os.sep + OS.sep}}' failed: \
    ...    Evaluating expression 'os.sep + OS.sep' failed: \
    ...    NameError: name 'OS' is not defined nor importable as module
    ${{OS.sep}}                                 Module import is case-sensitive
    ${{os.sep + OS.sep}}                        Also re-import is case-sensitive

Nested usage
    ${{ ${{ 42 }} }}                            ${42}
    ${{'${{'nested'}}'}}${{${{${{2}}}}}}        nested2
    ${{$${{$x}}}}                               X

Variable section
    ${PYTHON ONLY}                              ${0}
    ${VARIABLES}                                Python Evaluation
    ${INLINE VARIABLES}                         1, 2, 3, 4, 5, 6, 7, 8, 9, 10
    ${MODULE IMPORTS}                           foo${/}bar

Escape characters and curly braces
    [Documentation]    Escape characters in the variable body are left alone
    ...                and thus can be used in evaluated expression without
    ...                additional escaping. Exceptions to this rule are escapes
    ...                before curly braces as well as before literal strings
    ...                looking like variables. These escapes are needed to
    ...                make the whole variable valid and are removed. Matching
    ...                curly braces don't need to be escaped.
    ${{ '\n' }}                                 \n
    ${{ u'\xe4' }}                              ä
    ${{ '\${X}' }}                              \${X}
    ${{ '\\${X}' }}                             \\X
    ${{ '$\{X\}' }}                             \${X}
    ${{ '\\$\{X\}' }}                           \\\${X}
    ${{ '\\' }}                                 \\
    ${{ '\}' }}                                 }
    ${{ '\{' }}                                 {
    ${{ '{}' }}                                 {}
    ${{ __import__('${{'re'}}').match(r'(\d{2})${X}\s{2}', '1${2}X\t\r\${FOO}').group(${1}) }}
    ...                                         12

Invalid
    [Documentation]    FAIL GLOB:
    ...    Several failures occurred:
    ...
    ...    1) Resolving variable '\${{$i_do_not_exist}}' failed: \
    ...    Evaluating expression '$i_do_not_exist' failed: \
    ...    Variable '$i_do_not_exist' not found.
    ...
    ...    2) Resolving variable '\${{i_do_not_exist}}' failed: \
    ...    Evaluating expression 'i_do_not_exist' failed: \
    ...    NameError: name 'i_do_not_exist' is not defined nor importable as module
    ...
    ...    3) Resolving variable '\${{ 1/0 }}' failed: \
    ...    Evaluating expression '1/0' failed: \
    ...    ZeroDivisionError: *
    ...
    ...    4) Variable '\${{ 1/1 }' was not closed properly.
    ...
    ...    5) Resolving variable '\${{}}' failed: \
    ...    Evaluating expression '' failed: \
    ...    ValueError: Expression cannot be empty.
    ${{$i_do_not_exist}}                        Non-existing variable
    ${{i_do_not_exist}}                         Non-existing module
    ${{ 1/0 }}                                  Invalid expression
    ${{ 1/1 }                                   Invalid syntax
    ${{}}                                       Empty
