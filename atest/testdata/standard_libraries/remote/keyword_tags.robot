*** Settings ***
Library           Remote    http://127.0.0.1:${PORT}
Suite Setup       Set Log Level    DEBUG

*** Variables ***
${PORT}           8270

*** Test Cases ***
No tags
    No tags

Doc contains tags only
    Doc contains tags only

Doc contains tags after doc
    Doc contains tags after doc

Empty 'robot_tags' means no tags
    Empty robot tags means no tags

'robot_tags'
    Robot tags

'robot_tags' and doc tags
    Robot tags and doc tags
