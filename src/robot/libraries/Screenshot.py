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
if sys.platform.startswith('java'):
    from java.awt import Toolkit, Robot, Rectangle
    from javax.imageio import ImageIO
    from java.io import File
else:
    try:
        import wx
        _wx_app_reference = wx.PySimpleApp()
    except ImportError:
        wx = None
    try:
        from gtk import gdk
    except ImportError:
        gdk = None
    try:
        from PIL import ImageGrab  # apparently available only on Windows
    except ImportError:
        ImageGrab = None

from robot.version import get_version
from robot import utils
from robot.libraries.BuiltIn import BuiltIn


class Screenshot:

    """A test library for taking screenshots and embedding them into log files.

    *Using with Jython*

    On Jython this library uses Java AWT APIs. They are always available
    and thus no external modules are needed.

    *Using with Python*

    On Python you need to have one of the following modules installed to be
    able to use this library. The first module that is found will be used.

    - wxPython :: http://wxpython.org :: Required also by RIDE so many Robot
      Framework users already have this module installed.
    - PyGTK :: http://pygtk.org :: This module is available by default on most
      Linux distributions.
    - Python Imaging Library (PIL) :: http://www.pythonware.com/products/pil ::
      This module can take screenshots only on Windows.

    *Where screenshots are saved*

    By default screenshots are saved into the same directory where the Robot
    Framework log file is written. If no log is created, screenshots are saved
    into the directory where the XML output file is written.

    It is possible to specify a custom location for screenshots using
   `screenshot_directory` argument in `importing` and `Set Screenshot Directory`
    keyword during execution. It is also possible to save screenshots using
    an absolute path.

    Note that prior to Robot Framework 2.5.5 the default screenshot location
    was system's temporary directory.

    *Changes in Robot Framework 2.5.5*

    This library was enhanced heavily in Robot Framework 2.5.5 release. The
    changes are listed below and explained more thoroughly in affected places.

    - The support for using this library on Python (see above) was added.
    - The default location where screenshots are saved was changed (see above).
    - New `Take Screenshot` and `Take Screenshot Without Embedding` keywords
      were added. These keywords should be used for taking screenshots in
      the future. Other screenshot taking keywords will be deprecated and
      removed later.
    - `log_file_directory` argument was deprecated everywhere it was used..
    """

    ROBOT_LIBRARY_SCOPE = 'TEST SUITE'
    ROBOT_LIBRARY_VERSION = get_version()

    def __init__(self, screenshot_directory=None, log_file_directory='DEPRECATED'):
        """Optionally save screenshots into a custom directory.

        Examples (use only one of these):

        | *Setting* | *Value*  | *Value*    | *Value* |
        | Library | Screenshot |            | # Default location |
        | Library | Screenshot | ${TEMPDIR} | # System temp (this was default prior to 2.5.5) |

        `log_file_directory` has been deprecated in 2.5.5 release and has no
        effect. The information provided with it earlier is nowadays got
        automatically. This argument will be removed in the 2.6 release.
        """
        if log_file_directory != 'DEPRECATED':
            print '*WARN* TODO'
        self._given_screenshot_dir = self._norm_path(screenshot_directory)
        self._screenshot_taker = ScreenshotTaker()

    def _norm_path(self, path):
        if not path:
            return path
        return os.path.normpath(path.replace('/', os.sep))

    @property
    def _screenshot_dir(self):
        return self._given_screenshot_dir or self._log_dir

    @property
    def _log_dir(self):
        variables = BuiltIn().get_variables()
        outdir = variables['${OUTPUTDIR}']
        log = variables['${LOGFILE}']
        log = os.path.dirname(log) if log != 'NONE' else '.'
        return os.path.join(outdir, log)

    def set_screenshot_directory(self, path):
        """Sets the directory where screenshots are saved.

        The old value is returned.
        """
        path = self._norm_path(path)
        if not os.path.isdir(path):
            raise RuntimeError("Directory '%s' does not exist." % path)
        old = self._given_screenshot_dir
        self._given_screenshot_dir = path
        return old

    def set_screenshot_directories(self, default_directory=None,
                                   log_file_directory='DEPRECATED'):
        """*DEPRECATED* Use `Set Screenshot Directory` keyword instead."""
        self.set_screenshot_directory(default_directory)

    def save_screenshot_to(self, path):
        """Saves a screenshot to the specified file.

        *This keyword is obsolete.* Use `Take Screenshot` or `Take Screenshot
        Without Embedding` instead. This keyword will be deprecated in Robot
        Framework 2.6 and removed later.
        """
        return self._screenshot_to_file(path)

    def _screenshot_to_file(self, path, loglevel='INFO'):
        path = os.path.abspath(path.replace('/', os.sep))
        self._validate_screenshot_path(path)
        print '*DEBUG* Using %s modules for taking screenshot.' \
            % self._screenshot_taker.module
        self._screenshot_taker(path)
        print "*%s* Screenshot saved to '%s'" % (loglevel, path)
        return path

    def _validate_screenshot_path(self, path):
        if not os.path.exists(os.path.dirname(path)):
            raise RuntimeError("Directory '%s' where to save the screenshot does "
                               "not exist" % os.path.dirname(path))

    def save_screenshot(self, basename="screenshot", directory=None):
        """Saves a screenshot with a generated unique name.

        *This keyword is obsolete.* Use `Take Screenshot` or `Take Screenshot
        Without Embedding` instead. This keyword will be deprecated in Robot
        Framework 2.6 and removed later.

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
        return self._save_screenshot(basename, directory)

    def _save_screenshot(self, basename, directory=None):
        path = self._get_screenshot_path(basename, directory)
        return self._screenshot_to_file(path)

    def _get_screenshot_path(self, basename, directory):
        directory = self._norm_path(directory) if directory else self._screenshot_dir
        if basename.endswith('.jpg'):
            return os.path.join(directory, basename)
        index = 0
        while True:
            index += 1
            path = os.path.join(directory, "%s_%d.jpg" % (basename, index))
            if not os.path.exists(path):
                return path

    def log_screenshot(self, basename='screenshot', directory=None,
                       log_file_directory='DEPRECATED', width='100%'):
        """Takes a screenshot and logs it to Robot Framework's log file.

        *This keyword is obsolete.* Use `Take Screenshot` or `Take Screenshot
        Without Embedding` instead. This keyword will be deprecated in Robot
        Framework 2.6 and removed later.

        Saves the files as defined in the keyword `Save Screenshot` and creates
        a picture to Robot Framework's log. `directory` defines the directory
        where the screenshots are saved. By default, its value is
        `screenshot_directory`, which is set at the library import or with the
        keyword `Set Screenshot Directory`.

        `log_file_directory` has been deprecated in 2.5.5 release and has no
        effect. The information provided with it earlier is nowadays got
        automatically. This argument will be removed in the 2.6 release.
        """
        if log_file_directory != 'DEPRECATED':
            print '*WARN* TODO'
        return self._log_screenshot_as_html(basename, width, directory)

    def _log_screenshot_as_html(self, basename, width, directory=None):
        path = self._save_screenshot(basename, directory)
        link = utils.get_link_path(path, self._log_dir)
        print '*HTML* <a href="%s"><img src="%s" width="%s" /></a>' \
              % (link, link, width)
        return path

    def take_screenshot(self, basename="screenshot", width="800px"):
        return self._log_screenshot_as_html(basename, width=width)


class ScreenshotTaker(object):

    def __init__(self, module_name=None):
        self._screenshot = self._get_screenshot_taker(module_name)
        self.module = self._screenshot.__name__.split('_')[1]

    def __call__(self, path):
        self._screenshot(path)

    def _get_screenshot_taker(self, module_name):
        if sys.platform.startswith('java'):
            return self._java_screenshot
        if module_name:
            method_name = '_%s_screenshot' % module_name.lower()
            if hasattr(self, method_name):
                return getattr(self, method_name)
        return self._get_default_screenshot_taker()

    def _get_default_screenshot_taker(self):
        for module, screenshot_taker in [(wx, self._wx_screenshot),
                                         (gdk, self._gtk_screenshot),
                                         (ImageGrab, self._pil_screenshot),
                                         (True, self._no_screenshot)]:
            if module:
                return screenshot_taker

    def _java_screenshot(self, path):
        size = Toolkit.getDefaultToolkit().getScreenSize()
        rectangle = Rectangle(0, 0, size.width, size.height)
        image = Robot().createScreenCapture(rectangle)
        ImageIO.write(image, 'jpg', File(path))

    def _wx_screenshot(self, path):
        context = wx.ScreenDC()
        width, height = context.GetSize()
        bitmap = wx.EmptyBitmap(width, height, -1)
        memory = wx.MemoryDC()
        memory.SelectObject(bitmap)
        memory.Blit(0, 0, width, height, context, -1, -1)
        memory.SelectObject(wx.NullBitmap)
        bitmap.SaveFile(path, wx.BITMAP_TYPE_JPEG)

    def _gtk_screenshot(self, path):
        window = gdk.get_default_root_window()
        if not window:
            raise RuntimeError('Taking screenshot failed')
        width, height = window.get_size()
        pb = gdk.Pixbuf(gdk.COLORSPACE_RGB, False, 8, width, height)
        pb = pb.get_from_drawable(window, window.get_colormap(),
                                  0, 0, 0, 0, width, height)
        if not pb:
            raise RuntimeError('Taking screenshot failed')
        pb.save(path, 'jpeg')

    def _pil_screenshot(self, path):
        ImageGrab.grab().save(path, 'JPEG')

    def _no_screenshot(self, path):
        raise RuntimeError('Taking screenshots is not supported on this platform '
                           'by default. See library documentation for details.')


if __name__ == "__main__":
    if len(sys.argv) not in [2, 3]:
        print "Usage: %s path [wx|gtk|pil]" % os.path.basename(sys.argv[0])
        sys.exit(1)
    path = os.path.abspath(sys.argv[1])
    module = sys.argv[2] if len(sys.argv) == 3 else None
    shooter = ScreenshotTaker(module)
    print 'Using %s modules' % shooter.module
    shooter(path)
    print path
