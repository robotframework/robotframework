import re


def mask_changing_parts(path):
    with open(path) as file:
        content = file.read()
    for pattern, replace in [
        (r'"20\d{6} \d{2}:\d{2}:\d{2}\.\d{3}"', '"[timestamp]"'),
        (r'generator=".*?"', 'generator="[generator]"'),
        (r'source=".*?"', 'source="[source]"')
    ]:
        content = re.sub(pattern, replace, content)
    return content
