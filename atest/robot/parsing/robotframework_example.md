# Executable Robot Framework Test Documenation

This is an example of executable Robot Framework test data/documentation in a MarkDown (`.md`) file format.  Keep all your test automation assets in one place. This is almost real **SSOF** (_Single Source of Truth_), **SPOT** (_Single Point of Truth_) or call it what you like - it's just cool!

This example demonstrates how your executable RF test documentation looks like in MarkDowns's preview mode. It's pure joy to look at such documentation and - even more joy to **_work_** with it!

Of course you can use links to better navigate across this file (e.g. see [Section III](#section-iii)) or to link to other [documents](https://github.com/Tset-Noitamotua/_learnpython/blob/master/README.md).


## Section I
Let's start with a simple `log` test case.


```robotframework

# This is a Robot Framework specific MarkDown code block.
# Only such code blocks will be executed when running tests with Robot's test runner.
# Of course comments like this lines will be ignored by the runner!
# Same way as they are ignored in .robot files

*** Settings ***
Library    Collections

*** Test Cases ***
001 Simple Log Test Case
    Log    Hello Python!
    Log Many          Robot  Framework  Rules!!!
```

## Section II
Let's organize our tasks, todos and what else ...

### TODOs

* [ ] Task 001
* [x] Task 002 (done)
* [x] ~Task 003 (totally done)~

### Ordered Lists

1. Test Step äää ÄÄÄ üüü ÜÜÜÜ ßßß
   No problems with Umlauten thanks to UTF-8 encoding and Python 3
2. Test Step
3. Test Step

### Unordered Lists

 * `mkdocs new [dir-name]` - Create a new project.
 * `mkdocs serve` - Start the live-reloading docs server.
 * `mkdocs build` - Build the documentation site.
 * `mkdocs help` - Print this help message.


### Images

You can make beautiful documentation with images, screenshots, etc. ...

![Python_Logo](https://raw.githubusercontent.com/Tset-Noitamotua/_learnpython/master/images/python_logo.png)

### (Python) Code Examples

Have you written a custom RF Library? Document code examples here!

```python
def my_function(args):
    print('Damn Sexy Python Code!')
```
And don't be afraid your code examples won't be executed! Only Robot Framework code block will be executed - like the one we have already seen above and the one that follows below:


```robotframework
# Another Robot Framework code block which will be executed by Robot's test runner!
# RF code blocks may be destributed all over the .md file!
# They don't have to be at one peace / in one place!

*** Settings ***
Library    Collections

*** Test Cases ***
002 Easy Robot Test
    Log    Hello Python!
    Log Many          Robot  Framework  Rules!!!
```


## Section III

some text
some more text




```robotframework
*** Settings ***
Library    RequestsLibrary

*** Test Cases ***
003 GET (extern)
    [Documentation]   GET http://httpbin.org/headers
    [Tags]            extern
    Create Session    httpbin  http://httpbin.org
    ${response}=      Get Request   httpbin   /headers
    log              ${response}
```



```robotframework
*** Settings ***
Library   RequestsLibrary
Library   Collections
 
*** Test Cases ***
004 GET (extern)
  [Documentation]   GET http://httpbin.org/headers
  [Tags]            extern
  Create Session    httpbin  http://httpbin.org
  ${response}=      Get Request  httpbin  /headers
  log  ${response}
  log  ${response.raw}
  log  ${response.text}
  log  ${response.content}
  log  ${response.encoding}
  log  ${response.status_code}
  log  ${response.json()}
  log  @{response.json()}
  log  @{response.json()}[0]
  log  &{response.json()}[headers]
  &{headers}=  Set Variable  &{response.json()}[headers]
  log  &{headers}[Host]
  log  @{headers}[0]
  log  @{headers}[1]
  Should Contain    ${response.text}  User-Agent
  Should Contain    &{response.json()}[headers]  Host
  Should Be Equal   &{headers}[Host]  httpbin.org
  Should Be Equal As Strings   &{headers}[Host]  httpbin.org

005 POST (extern)
| | [Documentation] | https://www.hurl.it/
| | ...             | POST https://yourapihere.com/
| | [Tags]          | yourapihere
| | &{headers}=     | Create Dictionary | name=tset_noitamotua | WHO_AM_I=ROBOT
| | &{data}=        | Create Dictionary | mydata=foo | yourdata=bar
| | &{params}=      | Create Dictionary | myparams=yourparams
| | &{args}=        | Create Dictionary | myargs=yourargs
| | Create Session  | yourapihere | https://yourapihere.com/
| | ${response}=    | Post Request | yourapihere | / | headers=${headers}
| |  ...            | data=${data}
| |  ...            | params=${params}
| | log | ${response}
| | log | ${response.raw}
| | log | ${response.text}
| | log | ${response.content}
| | log | ${response.encoding}
| | log | ${response.status_code}
| | log | ${response.json()}
| | log many | @{response.json()}
| | log many | @{response.json()}[0]
| | log | &{response.json()}[headers]
| | &{headers}= | Set Variable | &{response.json()}[headers]
| | log | &{headers}[Host]
| | log | @{headers}[0]
| | log | @{headers}[1]
| | Should Contain  | ${response.text} | User-Agent
| | Should Contain  | &{response.json()}[headers] | Host
| | Should Be Equal | &{headers}[Host] | yourapihere.com
| | Should Contain  | &{response.json()}[headers] | Who-Am-I
| | Should Be Equal | &{headers}[Who-Am-I] | ROBOT
```