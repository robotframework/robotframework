from robot.api.deco import keyword


@keyword("Log ${number} Times")
def log(number):
    for i in range(int(number)):
        print("Log #{}".format(i + 1))
