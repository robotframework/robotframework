*** Settings ***
Library    JavaMultipleListenerLibrary

*** Test Cases ***
Multiple library listeners in java gets events
    Events should be    start test Multiple library listeners in java gets events
        ...             start kw JavaMultipleListenerLibrary.Events Should Be
