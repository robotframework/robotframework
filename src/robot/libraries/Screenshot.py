#  Copyright 2008-2010 Nokia Siemens Networks Oyj
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.


import sys
import os
import tempfile

from java.awt import Toolkit, Robot, Rectangle
from javax.imageio import ImageIO
from java.io import File

from robot.version import get_version
from robot import utils


class Screenshot:

    """A test library for taking full-screen screenshots of the desktop.

    `Screenshot` is Robot Framework's standard library that provides
    keywords to capture and store screenshots of the whole desktop.
    This library is implemented with Java AWT APIs, so it can be used
    only when running Robot Framework on Jython.
    """

    ROBOT_LIBRARY_SCOPE = 'TEST SUITE'
    ROBOT_LIBRARY_VERSION = get_version()

    def __init__(self, default_directory=None, log_file_directory=None):
        """Screenshot library can be imported with optional arguments.

        If the `default_directory` is provided, all the screenshots are saved
        into that directory by default. Otherwise the default location is the
        system temporary directory.

        `log_file_directory` is used to create relative paths when screenshots
        are logged. By default the paths to images in the log file are absolute.

        Examples (use only one of these):

        | *Setting* | *Value*  | *Value* | *Value* |
        | Library | Screenshot |         |         |
        | Library | Screenshot | ${CURDIR}/images | |
        | Library | Screenshot | ${OUTPUTDIR} | ${OUTPUTDIR} |

        It is also possible to set these directories using `Set Screenshot
        Directories` keyword.
        """
        self.set_screenshot_directories(default_directory, log_file_directory)

    def set_screenshot_directories(self, default_directory=None,
                                   log_file_directory=None):
        """Used to set `default_directory` and `log_file_directory`.

        See the `library importing` for details.
        """
        if not default_directory:
            self._default_dir = tempfile.gettempdir()
        else:
            self._default_dir = os.path.normpath(default_directory.replace('/', os.sep))
        if not log_file_directory:
            self._log_file_dir = None
        else:
            self._log_file_dir = os.path.normpath(log_file_directory.replace('/', os.sep))

    def save_screenshot_to(self, path):
        """Saves a screenshot to the specified file.

        The directory holding the file must exist or an exception is raised.
        """
        path = os.path.abspath(path.replace('/', os.sep))
        if not os.path.exists(os.path.dirname(path)):
            raise RuntimeError("Directory '%s' where to save the screenshot does "
                            "not exist" % os.path.dirname(path))
        screensize = Toolkit.getDefaultToolkit().getScreenSize()
        rectangle = Rectangle(0, 0, screensize.width, screensize.height)
        image = Robot().createScreenCapture(rectangle)
        ImageIO.write(image, "jpg", File(path))
        print "Screenshot saved to '%s'" % path
        return path

    def save_screenshot(self, basename="screenshot", directory=None):
        """Saves a screenshot with a generated unique name.

        The unique name is derived based on the provided `basename` and
        `directory` passed in as optional arguments. If a `directory`
        is provided, the screenshot is saved under that directory.
        Otherwise, the `default_directory` set during the library
        import or by the keyword `Set Screenshot Directories` is used.
        If a `basename` for the screenshot file is provided, a unique
        filename is determined by appending an underscore and a running
        counter. Otherwise, the `basename` defaults to 'screenshot'.

        The path where the screenshot is saved is returned.

        Examples:
        | Save Screenshot | mypic | /home/user | # (1) |
        | Save Screenshot | mypic |            | # (2) |
        | Save Screenshot |       |            | # (3) |
        =>
        1. /home/user/mypic_1.jpg, /home/user/mypic_2.jpg, ...
        2. /tmp/mypic_1.jpg, /tmp/mypic_2.jpg, ...
        3. /tmp/screenshot_1.jpg, /tmp/screenshot_2.jpg, ...
        """
        if directory is None:
            directory = self._default_dir
        else:
            directory = directory.replace('/', os.sep)
        index = 0
        while True:
            index += 1
            path = os.path.join(directory, "%s_%d.jpg" % (basename, index))
            if not os.path.exists(path):
                break
        return self.save_screenshot_to(path)

    def log_screenshot(self, basename="screenshot", directory=None,
                       log_file_directory=None, width="100%"):
        """Takes a screenshot and logs it to Robot Framework's log file.

        Saves the files as defined in the keyword `Save Screenshot` and creates
        a picture to Robot Framework's log. `directory` defines the directory
        where the screenshots are saved. By default, its value is
        `default_directory`, which is set at the library import or with the
        keyword `Set Screenshot Directories`. `log_file_directory` is used to
        create relative paths to the pictures. This allows moving the log and
        pictures to different machines and having still working pictures. If
        `log_file_directory` is not given or set (in the same way as
        `default_directory` is set), the paths are absolute.

        The path where the screenshot is saved is returned.
        """
        path = self.save_screenshot(basename, directory)
        if log_file_directory is None:
            log_file_directory = self._log_file_dir
        if log_file_directory is not None:
            link = utils.get_link_path(path, log_file_directory)
        else:
            link = 'file:///' + path.replace('\\', '/')
        print '*HTML* <a href="%s"><img src="%s" width="%s" /></a>' \
              % (link, link, width)
        return path


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print "Usage: %s path" % os.path.basename(sys.argv[0])
    else:
        Screenshot().save_screenshot_to(sys.argv[1])
