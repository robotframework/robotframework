#!/usr/bin/env python

from os.path import abspath, dirname, join

from setuptools import find_packages, setup

# Version number typically updated by running `invoke set-version <version>`.
# Run `invoke --help set-version` or see tasks.py for details.
VERSION = "7.3rc3"
with open(join(dirname(abspath(__file__)), "README.rst")) as f:
    LONG_DESCRIPTION = f.read()
    base_url = "https://github.com/robotframework/robotframework/blob/master"
    for text in ("INSTALL", "CONTRIBUTING"):
        search = f"`<{text}.rst>`__"
        replace = f"`{text}.rst <{base_url}/{text}.rst>`__"
        if search not in LONG_DESCRIPTION:
            raise RuntimeError(f"{search} not found from README.rst")
        LONG_DESCRIPTION = LONG_DESCRIPTION.replace(search, replace)
CLASSIFIERS = """
Development Status :: 5 - Production/Stable
License :: OSI Approved :: Apache Software License
Operating System :: OS Independent
Programming Language :: Python :: 3
Programming Language :: Python :: 3 :: Only
Programming Language :: Python :: 3.8
Programming Language :: Python :: 3.9
Programming Language :: Python :: 3.10
Programming Language :: Python :: 3.11
Programming Language :: Python :: 3.12
Programming Language :: Python :: 3.13
Programming Language :: Python :: 3.14
Programming Language :: Python :: Implementation :: CPython
Programming Language :: Python :: Implementation :: PyPy
Topic :: Software Development :: Testing
Topic :: Software Development :: Testing :: Acceptance
Topic :: Software Development :: Testing :: BDD
Framework :: Robot Framework
""".strip().splitlines()
DESCRIPTION = (
    "Generic automation framework for acceptance testing "
    "and robotic process automation (RPA)"
)
KEYWORDS = (
    "robotframework automation testautomation rpa testing acceptancetesting atdd bdd"
)
PACKAGE_DATA = [
    join("htmldata", directory, pattern)
    for directory in ("rebot", "libdoc", "testdoc", "lib", "common")
    for pattern in ("*.html", "*.css", "*.js")
] + ["api/py.typed", "logo.png"]


setup(
    name="robotframework",
    version=VERSION,
    author="Pekka Klärck",
    author_email="peke@eliga.fi",
    url="https://robotframework.org",
    project_urls={
        "Source": "https://github.com/robotframework/robotframework",
        "Issue Tracker": "https://github.com/robotframework/robotframework/issues",
        "Documentation": "https://robotframework.org/robotframework",
        "Release Notes": f"https://github.com/robotframework/robotframework/blob/master/doc/releasenotes/rf-{VERSION}.rst",
        "Slack": "http://slack.robotframework.org",
    },
    download_url="https://pypi.org/project/robotframework",
    license="Apache License 2.0",
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/x-rst",
    keywords=KEYWORDS,
    platforms="any",
    python_requires=">=3.8",
    classifiers=CLASSIFIERS,
    package_dir={"": "src"},
    package_data={"robot": PACKAGE_DATA},
    packages=find_packages("src"),
    entry_points={
        "console_scripts": [
            "robot = robot:run_cli",
            "rebot = robot:rebot_cli",
            "libdoc = robot.libdoc:libdoc_cli",
        ]
    },
)
