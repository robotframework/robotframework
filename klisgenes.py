ROBOT_LISTENER_API_VERSION=3

def start_suite(data, result):
    print(repr(data))

def start_keyword(data, result):
    data.name = "Log many"

def end_keyword(data, result):
    print(f"YEAH 2 {data.name}")