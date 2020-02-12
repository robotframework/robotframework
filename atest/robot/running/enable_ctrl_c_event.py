try:
    from ctypes import windll

    windll.kernel32.SetConsoleCtrlHandler(None, False)

except ImportError:
    pass
