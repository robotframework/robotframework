def importing_robot_module_directly_fails():
    try:
        import running  # noqa: F401
    except ImportError:
        pass
    else:
        raise AssertionError("Importing 'running' directly succeeded!")


def importing_robot_module_through_robot_succeeds():
    from robot import running  # noqa: F401


def importing_standard_library_directly_fails():
    try:
        import BuiltIn  # noqa: F401
    except ImportError:
        pass
    else:
        raise AssertionError("Importing 'BuiltIn' directly succeeded!")


def importing_standard_library_through_robot_libraries_succeeds():
    from robot.libraries import BuiltIn

    BuiltIn.BuiltIn().set_test_variable("${SET BY LIBRARY}", 42)
