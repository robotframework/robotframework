# Listener v3 keyword and control structure examples

Files in this directory are used by Robot Framework acceptance tests, but they work also as examples for using listener version 3 with keywords and control structures.

## Contents

- **[`Modifier.py`](Modifier.py)** contains examples how to modify data and results in different ways. It can be used as a listener from the command line directly.
- **[`eventvalidators.py`](eventvalidators.py)** shows all possible keyword and control specific listener v3 methods. It contains several listeners that are registered by [`Library.py`](Library.py).
- **[`tests.robot`](tests.robot)** can be used with the aforementioned listeners to see how they work.
- **[`ArgumentModifier.py`](ArgumentModifier.py)** modifies keyword arguments and can be used with [`keyword_arguments.robot`](keyword_arguments.robot).
- **[`ChangeStatus.py`](ChangeStatus.py)** modifies keyword statuses and can be used with [`change_status.robot`](change_status.robot). Requires Robot Framework 7.1.

## Usage

To execute tests without listeners simply run:

```bash
robot tests.robot
```

To see data and result modifications in action, run the following and compare the results with the earlier results:

```bash
robot --listener Modifier.py tests.robot
```

To validate that all listener methods are executed, use this:

```bash
robot --variable VALIDATE_EVENTS:True tests.robot
```

To see how keyword arguments can be modified:

```bash
robot --listener ArgumentModifier.py keyword_arguments.robot
```

To see how keyword statuses can be modified:

```bash
robot --listener ChangeStatus.py change_status.robot
```
