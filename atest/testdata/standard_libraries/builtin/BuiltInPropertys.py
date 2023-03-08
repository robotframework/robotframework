from robot.libraries.BuiltIn import BuiltIn


class BuiltInPropertys:

    def __init__(self, dry_run=False):
        assert BuiltIn().robot_running is True
        assert BuiltIn().dry_run_active is dry_run

    def keyword(self):
        assert BuiltIn().robot_running is True
        assert BuiltIn().dry_run_active is False
