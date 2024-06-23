*** Settings ***
Library               String

*** Variables ***
${NSN}                nokia_siemens_networks
${TEXT IN COLUMNS}    robot\tframework\nis\tgood\tfor\ttesting
${FIRST LINE}         robot\tframework
${SECOND LINE}        is\tgood\tfor\ttesting
&{USER}               name=John Doe    email=john@example.com

*** Test Cases ***
Format String With Positional Argument
    ${result} =    Format String    User {} is not a admin user    non-admin
    Should be equal    ${result}    User non-admin is not a admin user

Format String With Positional Arguments
    ${result} =    Format String    Uploaded file: {} should not be bigger than {}.    photo.jpg    5MB
    Should be equal    ${result}    Uploaded file: photo.jpg should not be bigger than 5MB.

Format String With Named Search Replace Argument
    ${result} =    Format String    My {test} String    test=awesome
    Should be equal    ${result}    My awesome String

Format String With Named Search Replace Arguments
    ${result} =    Format String    Username: {username} - Password: {password}    username=robotframework    password=S3¢r3t
    Should be equal    ${result}    Username: robotframework - Password: S3¢r3t

Format String With Named And Search Replace Arguments
    ${result} =    Format String    Document {} is missing on folder {folder}    tests.robot    folder=/home
    Should be equal    ${result}    Document tests.robot is missing on folder /home

Format String From Non-ASCII Template
    ${result} =    Format String    {} and {} are fruits from Brazil    Açaí    Cupuaçu
    Should be equal    ${result}    Açaí and Cupuaçu are fruits from Brazil

Template can contain '=' without escaping
    ${result} =    Format String    x={}, y={}    1    2
    Should be equal    ${result}    x=1, y=2
    ${result} =    Format String    x={x}, y={y}    y=2    x=1
    Should be equal    ${result}    x=1, y=2
    ${result} =    Format String    template={}    always positional
    Should be equal    ${result}    template=always positional
    ${result} =    Format String    escaping\={}    ok as well
    Should be equal    ${result}    escaping=ok as well

Format String From Template File
    ${result} =    Format String    ${CURDIR}/format_string_template.txt    condition=supports
    Should be equal    ${result}    Format String also supports files templates!

Format String From Template Non-ASCII File
    ${result} =    Format String    ${CURDIR}/format_string_nonasccii_template.txt    city=São Paulo
    Should be equal    ${result}    São Paulo is the eleventh biggest city in the world!

Format String From Trailling Whitespace Template File
    ${result} =    Format String    ${CURDIR}/format_string_trailling_white_space_template.txt    name=Stan Lee
    Should be equal    ${result}    ${SPACE}${SPACE}Stan Lee is the best!!${SPACE}${SPACE}

Attribute access
    ${result} =    Format String    {user.name} <{user.email}>    user=${USER}
    Should Be Equal    ${result}    John Doe <john@example.com>

Item access
    ${result} =    Format String    {user[name]} <{user[email]}>    user=${USER}
    Should Be Equal    ${result}    John Doe <john@example.com>

Format Spec
    ${result} =    Format String    {:*^30}    centered
    Should Be Equal    ${result}    ***********centered***********
    ${result} =    Format String    {0:{width}{base}}    ${42}    base=X    width=10
    Should Be Equal    ${result}    ${SPACE*8}2A
