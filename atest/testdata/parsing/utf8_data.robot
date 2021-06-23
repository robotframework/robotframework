U T F 8   D A T A

***Setting***
Documentation   Testing that reading and writing of Unicode (äöå §½€ etc.) works properly.
Default Tags    tag-äöå
Force Tags      tag-§
MetaData        Ä         §

|      *Variable*     | *Value* |
| ${UNICODE}          | äöå §½€ |
| ${UTF NAME öäå §½€} | value   |

**Test Cases***
UTF-8   [Documentation]  äöå §½€
        [Setup]          Log  äöå
        [Tags]           tag-€
        Log              §½€
        Log              ${UNICODE}
        Logging Keyword  äöå
        [Teardown]       Logging Keyword  äöå

UTF-8 Name Äöå §½€"
  [Documentation]  Quote is actually plain ASCII but there was
  ...              a bug in processing them also.
  ...              FAIL  Virheessäkin on ääkkösiä: Äöå §½€"
  ${ret} =  äöå §½€
  Log       ${ret}
  Should Be Equal    ${ret}    äöå §½€
  Log       ${UTF NAME öäå §½€}
  Fail      Virheessäkin on ääkkösiä: Äöå §½€"


| * * * * * * * * * Keywords * * * * * * * * |
| Logging Keyword | [Arguments] | ${value}   |
|                 | Log         | ${value}   |
|                 | Log         | ${UNICODE} |
|                 | Log         | §½€        |
| Äöå §½€         | [Return]    | äöå §½€    |
