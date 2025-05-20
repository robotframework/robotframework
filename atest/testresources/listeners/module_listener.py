import os

outpath = os.path.join(os.getenv("TEMPDIR"), "listen_by_module.txt")
OUTFILE = open(outpath, "w", encoding="UTF-8")
ROBOT_LISTENER_API_VERSION = 2


def start_suite(name, attrs):
    meta = " ".join(f"{k}: {v}" for k, v in attrs["metadata"].items())
    OUTFILE.write(f"SUITE START: {name} ({attrs['id']}) '{attrs['doc']}' [{meta}]\n")


def start_test(name, attrs):
    tags = [str(tag) for tag in attrs["tags"]]
    OUTFILE.write(
        f"TEST START: {name} ({attrs['id']}, line {attrs['lineno']}) "
        f"'{attrs['doc']}' {tags}\n"
    )


def start_keyword(name, attrs):
    call = ""
    if attrs["assign"]:
        call += ", ".join(attrs["assign"]) + " = "
    if name:
        call += name + " "
    if attrs["args"]:
        call += str(attrs["args"]) + " "
    OUTFILE.write(f"{attrs['type']} START: {call}(line {attrs['lineno']})\n")


def log_message(message):
    msg, level = message["message"], message["level"]
    if level != "TRACE" and "Traceback" not in msg:
        OUTFILE.write(f"LOG MESSAGE: [{level}] {msg}\n")


def message(message):
    if "Settings" in message["message"]:
        OUTFILE.write(f"Got settings on level: {message['level']}\n")


def end_keyword(name, attrs):
    kw_type = "KW" if attrs["type"] == "Keyword" else attrs["type"].upper()
    OUTFILE.write(f"{kw_type} END: {attrs['status']}\n")


def end_test(name, attrs):
    if attrs["status"] == "PASS":
        OUTFILE.write("TEST END: PASS\n")
    else:
        OUTFILE.write(f"TEST END: {attrs['status']} {attrs['message']}\n")


def end_suite(name, attrs):
    OUTFILE.write(f"SUITE END: {attrs['status']} {attrs['statistics']}\n")


def output_file(path):
    _out_file("Output", path)


def report_file(path):
    _out_file("Report", path)


def log_file(path):
    _out_file("Log", path)


def debug_file(path):
    _out_file("Debug", path)


def _out_file(name, path):
    assert os.path.isabs(path)
    OUTFILE.write(f"{name}: {os.path.basename(path)}\n")


def close():
    OUTFILE.write("Closing...\n")
    OUTFILE.close()
