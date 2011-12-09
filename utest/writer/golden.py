_txt_template = '''*** Settings ***
Library           MyLibrary    argument    WITH NAME    My Alias    # My library comment
Variables         MyVariables    args    args 2    args 3    args 4    args 5    args 6
...               args 7    args 8    args 9    args 10    args 11    args 12
Resource          MyResource args that are part of the name

*** Variables ***
MyVar    val1    val2    val3    val4    val5    val6    val6
...    val7    val8    val9    # var comment
%s
*** Keywords ***
My Keyword
    [Documentation]    Documentation    # Comment for doc
    # Comment row
    # Comment row 2
    My Step 1    args    args 2    args 3    args 4    args 5    args 6
    ...    args 7    args 8    args 9    # step 1 comment
    : FOR    ${param1}    ${param2}    IN    ${data 1}    ${data 2}    ${data 3}
    ...    ${data 4}    ${data 5}    ${data 6}
    \    Loop Step    args    args 2    args 3    args 4    args 5
    \    ...    args 6    args 7    args 8    args 9    # loop step comment
    \    Loop Step 2
    My Step 2    my step 2 arg    second arg    # step 2 comment
    [Return]    args 1    args 2

'''

GOLDEN_TXT_RESOURCE = _txt_template % ''
GOLDEN_TXT_TESTCASE_FILE = _txt_template % '''
*** Test Cases ***
My Test Case
    [Documentation]    This is a long comment that spans several columns
    My TC Step 1    my step arg    # step 1 comment
    My TC Step 2    my step 2 arg    second \ arg    # step 2 comment
    [Teardown]    1 minute    args
'''
GOLDEN_ALIGNED_TXT_TESTCASE_FILE = _txt_template % '''
*** Test Cases ***    header1            header2
My Test Case          [Documentation]    This is a long comment that spans several columns
                      My TC Step 1       my step arg                                          # step 1 comment
                      My TC Step 2       my step \ 2 arg                                      second arg          # step 2 comment
                      [Teardown]         1 minute
'''


_txt_pipe_template = '''| *** Settings *** |
| Library        | MyLibrary | argument | WITH NAME | My Alias | # My library comment |
| Variables      | MyVariables | args | args 2 | args 3 | args 4 | args 5 | args 6 |
| ...            | args 7 | args 8 | args 9 | args 10 | args 11 | args 12 |
| Resource       | MyResource args that are part of the name |

| *** Variables *** |
| MyVar | val1 | val2 | val3 | val4 | val5 | val6 | val6 |
| ... | val7 | val8 | val9 | # var comment |
%s
| *** Keywords *** |
| My Keyword |
|    | [Documentation] | Documentation | # Comment for doc |
|    | # Comment row |
|    | # Comment row 2 |
|    | My Step 1 | args | args 2 | args 3 | args 4 | args 5 | args 6 |
|    | ... | args 7 | args 8 | args 9 | # step 1 comment |
|    | : FOR | ${param1} | ${param2} | IN | ${data 1} | ${data 2} | ${data 3} |
|    | ... | ${data 4} | ${data 5} | ${data 6} |
|    |    | Loop Step | args | args 2 | args 3 | args 4 | args 5 |
|    |    | ... | args 6 | args 7 | args 8 | args 9 | # loop step comment |
|    |    | Loop Step 2 |
|    | My Step 2 | my step 2 arg | second arg | # step 2 comment |
|    | [Return] | args 1 | args 2 |

'''

GOLDEN_TXT_PIPE_RESOURCE = _txt_pipe_template % ''
GOLDEN_TXT_PIPE_TESTCASE_FILE = _txt_pipe_template % '''
| *** Test Cases *** |
| My Test Case |
|    | [Documentation] | This is a long comment that spans several columns |
|    | My TC Step 1 | my step arg | # step 1 comment |
|    | My TC Step 2 | my step 2 arg | second \ arg | # step 2 comment |
|    | [Teardown] | 1 minute | args |
'''

_tsv_template = '''*Settings*
Library\tMyLibrary\targument\tWITH NAME\tMy Alias\t# My library comment\t\t
Variables\tMyVariables\targs\targs 2\targs 3\targs 4\targs 5\targs 6
...\targs 7\targs 8\targs 9\targs 10\targs 11\targs 12\t
Resource\tMyResource args that are part of the name\t\t\t\t\t\t
\t\t\t\t\t\t\t
*Variables*
MyVar\tval1\tval2\tval3\tval4\tval5\tval6\tval6
...\tval7\tval8\tval9\t# var comment\t\t\t
\t\t\t\t\t\t\t%s
*Keywords*
My Keyword\t\t\t\t\t\t\t
\t[Documentation]\tDocumentation\t# Comment for doc\t\t\t\t
\t# Comment row\t\t\t\t\t\t
\t# Comment row 2\t\t\t\t\t\t
\tMy Step 1\targs\targs 2\targs 3\targs 4\targs 5\targs 6
\t...\targs 7\targs 8\targs 9\t# step 1 comment\t\t
\t: FOR\t${param1}\t${param2}\tIN\t${data 1}\t${data 2}\t${data 3}
\t...\t${data 4}\t${data 5}\t${data 6}\t\t\t
\t\tLoop Step\targs\targs 2\targs 3\targs 4\targs 5
\t\t...\targs 6\targs 7\targs 8\targs 9\t# loop step comment
\t\tLoop Step 2\t\t\t\t\t
\tMy Step 2\tmy step 2 arg\tsecond arg\t# step 2 comment\t\t\t
\t[Return]\targs 1\targs 2\t\t\t\t
\t\t\t\t\t\t\t
'''

GOLDEN_TSV_RESOURCE = _tsv_template % ''
GOLDEN_TSV_TESTCASE_FILE = _tsv_template % '''
*Test Cases*
My Test Case\t\t\t\t\t\t\t
\t[Documentation]\tThis is a long comment that spans several columns\t\t\t\t\t
\tMy TC Step 1\tmy step arg\t# step 1 comment\t\t\t\t
\tMy TC Step 2\tmy step 2 arg\tsecond \ arg\t# step 2 comment\t\t\t
\t[Teardown]\t1 minute\targs\t\t\t\t
\t\t\t\t\t\t\t'''

GOLDEN_HTML_TESTCASE_FILE = '''
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">
<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
<style type="text/css">
html {
  font-family: Arial,Helvetica,sans-serif;
  background-color: white;
  color: black;
}
table {
  border-collapse: collapse;
  empty-cells: show;
  margin: 1em 0em;
  border: 1px solid black;
}
th, td {
  border: 1px solid black;
  padding: 0.1em 0.2em;
  height: 1.5em;
  width: 12em;
}
td.colspan4, th.colspan4 {
    width: 48em;
}
td.colspan3, th.colspan3 {
    width: 36em;
}
td.colspan2, th.colspan2 {
    width: 24em;
}
th {
  background-color: rgb(192, 192, 192);
  color: black;
  height: 1.7em;
  font-weight: bold;
  text-align: center;
  letter-spacing: 0.1em;
}
td.name {
  background-color: rgb(240, 240, 240);
  letter-spacing: 0.1em;
}
td.name, th.name {
  width: 10em;
}
</style>
<title>Here</title>
</head>
<body>
<h1>Here</h1>
<table id="settings" border="1">
<tr>
<th class="name" colspan="5">Settings</th>
</tr>
<tr>
<td class="name">Library</td>
<td>MyLibrary</td>
<td>argument</td>
<td>WITH NAME</td>
<td>My Alias</td>
</tr>
<tr>
<td class="name">...</td>
<td># My library comment</td>
<td></td>
<td></td>
<td></td>
</tr>
<tr>
<td class="name">Variables</td>
<td>MyVariables</td>
<td>args</td>
<td>args 2</td>
<td>args 3</td>
</tr>
<tr>
<td class="name">...</td>
<td>args 4</td>
<td>args 5</td>
<td>args 6</td>
<td>args 7</td>
</tr>
<tr>
<td class="name">...</td>
<td>args 8</td>
<td>args 9</td>
<td>args 10</td>
<td>args 11</td>
</tr>
<tr>
<td class="name">...</td>
<td>args 12</td>
<td></td>
<td></td>
<td></td>
</tr>
<tr>
<td class="name">Resource</td>
<td>MyResource args that are part of the name</td>
<td></td>
<td></td>
<td></td>
</tr>
<tr>
<td class="name"></td>
<td></td>
<td></td>
<td></td>
<td></td>
</tr>
</table>
<table id="variables" border="1">
<tr>
<th class="name" colspan="5">Variables</th>
</tr>
<tr>
<td class="name">MyVar</td>
<td>val1</td>
<td>val2</td>
<td>val3</td>
<td>val4</td>
</tr>
<tr>
<td class="name">...</td>
<td>val5</td>
<td>val6</td>
<td>val6</td>
<td>val7</td>
</tr>
<tr>
<td class="name">...</td>
<td>val8</td>
<td>val9</td>
<td># var comment</td>
<td></td>
</tr>
<tr>
<td class="name"></td>
<td></td>
<td></td>
<td></td>
<td></td>
</tr>
</table>
<table id="testcases" border="1">
<tr>
<th class="name" colspan="5">Test Cases</th>
</tr>
<tr>
<td class="name"><a name="test_My Test Case">My Test Case</a></td>
<td>[Documentation]</td>
<td class="colspan3" colspan="3">This is a long comment that spans several columns</td>
</tr>
<tr>
<td class="name"></td>
<td>My TC Step 1</td>
<td>my step arg</td>
<td># step 1 comment</td>
<td></td>
</tr>
<tr>
<td class="name"></td>
<td>My TC Step 2</td>
<td>my step 2 arg</td>
<td>second \ arg</td>
<td># step 2 comment</td>
</tr>
<tr>
<td class="name"></td>
<td>[Teardown]</td>
<td>1 minute</td>
<td>args</td>
<td></td>
</tr>
<tr>
<td class="name"></td>
<td></td>
<td></td>
<td></td>
<td></td>
</tr>
</table>
<table id="keywords" border="1">
<tr>
<th class="name" colspan="5">Keywords</th>
</tr>
<tr>
<td class="name"><a name="keyword_My Keyword">My Keyword</a></td>
<td>[Documentation]</td>
<td>Documentation</td>
<td># Comment for doc</td>
<td></td>
</tr>
<tr>
<td class="name"></td>
<td># Comment row</td>
<td></td>
<td></td>
<td></td>
</tr>
<tr>
<td class="name"></td>
<td># Comment row 2</td>
<td></td>
<td></td>
<td></td>
</tr>
<tr>
<td class="name"></td>
<td>My Step 1</td>
<td>args</td>
<td>args 2</td>
<td>args 3</td>
</tr>
<tr>
<td class="name"></td>
<td>...</td>
<td>args 4</td>
<td>args 5</td>
<td>args 6</td>
</tr>
<tr>
<td class="name"></td>
<td>...</td>
<td>args 7</td>
<td>args 8</td>
<td>args 9</td>
</tr>
<tr>
<td class="name"></td>
<td>...</td>
<td># step 1 comment</td>
<td></td>
<td></td>
</tr>
<tr>
<td class="name"></td>
<td>: FOR</td>
<td>${param1}</td>
<td>${param2}</td>
<td>IN</td>
</tr>
<tr>
<td class="name"></td>
<td>...</td>
<td>${data 1}</td>
<td>${data 2}</td>
<td>${data 3}</td>
</tr>
<tr>
<td class="name"></td>
<td>...</td>
<td>${data 4}</td>
<td>${data 5}</td>
<td>${data 6}</td>
</tr>
<tr>
<td class="name"></td>
<td></td>
<td>Loop Step</td>
<td>args</td>
<td>args 2</td>
</tr>
<tr>
<td class="name"></td>
<td></td>
<td>...</td>
<td>args 3</td>
<td>args 4</td>
</tr>
<tr>
<td class="name"></td>
<td></td>
<td>...</td>
<td>args 5</td>
<td>args 6</td>
</tr>
<tr>
<td class="name"></td>
<td></td>
<td>...</td>
<td>args 7</td>
<td>args 8</td>
</tr>
<tr>
<td class="name"></td>
<td></td>
<td>...</td>
<td>args 9</td>
<td># loop step comment</td>
</tr>
<tr>
<td class="name"></td>
<td></td>
<td>Loop Step 2</td>
<td></td>
<td></td>
</tr>
<tr>
<td class="name"></td>
<td>My Step 2</td>
<td>my step 2 arg</td>
<td>second arg</td>
<td># step 2 comment</td>
</tr>
<tr>
<td class="name"></td>
<td>[Return]</td>
<td>args 1</td>
<td>args 2</td>
<td></td>
</tr>
<tr>
<td class="name"></td>
<td></td>
<td></td>
<td></td>
<td></td>
</tr>
</table>
</body>
</html>
'''
