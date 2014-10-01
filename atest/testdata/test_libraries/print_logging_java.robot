*** Settings ***
Documentation     Tests for logging using stdout/stderr from Java
Library           ExampleLibrary
Library           ExampleJavaLibrary    WITH NAME    Java
Library           String

*** Test Cases ***
Logging Using Stdout And Stderr
    [Setup]    Java.Print    Hello\nworld\n!!
    Java.Print    Hello from Java library!
    Java.Stderr    Hello Java stderr!!

Logging Non-ASCII
    Java.Print    Hyvää päivää java stdout!
    Java.Stderr    Hyvää päivää java stderr!

Logging with Levels
    Java.Print    This is debug    DEBUG
    Java.Print    First msg\n2nd line of1st msg\n*INFO* 2nd msg *INFO* Still 2nd
    Java.Print    *INFO*1st msg\n2nd line\n*WARN* Second msg\n*INVAL* Still 2nd\n*INFO*Now 3rd msg
    Java.Stderr    Warning to stderr    WARN

Logging HTML
    Java.Print    <b>Hello, stdout!</b>    HTML
    Java.Stderr    <b>Hello, stderr!</b>    HTML

Logging both to Python and Java streams
    Print to Python and Java streams
