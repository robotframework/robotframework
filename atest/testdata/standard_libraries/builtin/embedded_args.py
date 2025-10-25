from robot.api.deco import keyword


@keyword('Embedded "${argument}" in library')
def embedded(arg):
    print(arg)


@keyword('Embedded object "${obj}" in library')
def embedded_object(obj):
    print(obj)
    if obj.name != "Robot":
        raise AssertionError(f"'{obj.name}' != 'Robot'")


@keyword('Embedded "not" in library')
def embedded_not():
    print("Nothing embedded in this library keyword!")
