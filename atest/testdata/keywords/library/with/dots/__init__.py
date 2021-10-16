from robot.api.deco import keyword


class dots:

    @keyword(name='In.name.conflict')
    def keyword(self):
        print("Executing keyword 'In.name.conflict'.")
