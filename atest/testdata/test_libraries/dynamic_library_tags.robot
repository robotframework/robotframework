*** Settings ***
Library        DynamicLibraryTags.py
Library        ArgDocDynamicJavaLibrary

*** Test Cases ***
Tags from documentation
    Only tags in documentation
    Tags in addition to normal documentation

Tags from get_keyword_tags
    Tags from get_keyword_tags

Tags both from doc and get_keyword_tags
    Tags both from doc and get_keyword_tags

Tags from Java getKeywordTags
    Java no arg
