def importing_robot_module_directly_fails():
    try:
        import running
    except ImportError:
        pass
    else:
        raise AssertionError("Importing 'running' succeeded!")


def importing_robot_module_through_robot_succeeds():
    import robot.running
