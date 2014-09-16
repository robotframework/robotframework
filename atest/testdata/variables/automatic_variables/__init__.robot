*** Settings ***
Documentation     The doc.
Metadata          Name    Value
Suite Setup       Check Variables In Suite Setup    Automatic Variables
...               The doc.    {'Name': 'Value'}
Resource          resource.robot
