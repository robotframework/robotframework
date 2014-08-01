*** Settings ***
Library    AbstractJavaLibrary.java
Library    JavaLibraryWithoutPublicConstructor.java
Library    JavaLibraryWithoutPublicConstructor.java    no    args    accepted
Library    java.lang.Enum    # Both abstract and doesn't have public constructor
Library    java.lang.Enum    name    ${42}

*** Test Case ***
Invalid Java Libraries Do Not Cause Fatal Errors
    Log    This test should pass
