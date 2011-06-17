import os
from robot.result.jsparser import create_datamodel_from

if __name__ == '__main__':
    base = os.path.dirname(__file__)
    model = create_datamodel_from(os.path.join(base, 'output.xml'))
    model.set_settings({'logURL': 'log.html',
                        'reportURL': 'report.html',
                        'background': {'fail': 'DeepPink'}})
    with open(os.path.join(base, 'data.js'), 'w') as output:
        model.write_to(output)

