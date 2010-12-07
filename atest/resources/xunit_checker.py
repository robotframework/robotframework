from xml.dom.minidom import parse

def parse_xunit(path):
    return parse(path)

def get_root_element_name(dom):
    return dom.documentElement.tagName

def get_element_count_by_name(dom, name):
    return len(get_elements_by_name(dom, name))

def get_elements_by_name(dom, name):
    return dom.getElementsByTagName(name)