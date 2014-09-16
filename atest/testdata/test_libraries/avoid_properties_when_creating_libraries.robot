*** Setting ***
Library           ExampleJavaLibrary
Library           extendingjava.ExtendJavaLib
Library           newstyleclasses.NewStyleClassLibrary

*** Test Case ***
Java Bean Property
    ${count} =    ExampleJavaLibrary.Get Count
    Should Be Equal As Integers    ${count}    1

Java Bean Property In Class Extended In Python
    ${count} =    extendingjava.ExtendJavaLib.Get Count
    Should Be Equal As Integers    ${count}    1

Python Property
    mirror    whatever
