*** Settings ***
Library           String

*** Variables ***
${NSN}            nokia_siemens_networks
${TEXT IN COLUMNS}    robot\tframework\nis\tgood\tfor\ttesting
${FIRST LINE}     robot\tframework
${SECOND LINE}    is\tgood\tfor\ttesting

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

Format String From Template File
    ${result} =    Format String    atest/testdata/standard_libraries/string/format_string_template.txt    condition=supports
    Should be equal    ${result}    Format String also supports files templates!
