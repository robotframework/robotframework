from robot.api.deco import library


@library(metadata={"Homepage": "https://example.com", "License": "Apache-2.0"})
class Metadata:
    ROBOT_LIBRARY_METADATA = {"Homepage": "overridden"}

    def keyword(self):
        pass
