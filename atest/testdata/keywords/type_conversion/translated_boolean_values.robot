*** Settings ***
Library                  Annotations.py
Library                  OperatingSystem

*** Test cases ***
Boolean
    Boolean              Tosi                      True
    Boolean              Kyllä                     True
    Boolean              Päällä                    True
    Boolean              EpäTOSI                   False
    Boolean              EI                        False
    Boolean              Pois                      False

Via Run Keyword
    Run Keyword    Boolean    Kyllä    True
    Run Keyword    Boolean    EI       False
