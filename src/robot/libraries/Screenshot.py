#  Copyright 2008-2015 Nokia Networks
#  Copyright 2016-     Robot Framework Foundation
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

from __future__ import print_function

import os
import subprocess
import sys
if sys.platform.startswith('java'):
    from java.awt import Toolkit, Robot, Rectangle
    from javax.imageio import ImageIO
    from java.io import File
elif sys.platform == 'cli':
    import clr
    clr.AddReference('System.Windows.Forms')
    clr.AddReference('System.Drawing')
    from System.Drawing import Bitmap, Graphics, Imaging
    from System.Windows.Forms import Screen
else:
    try:
        import wx
        wx_app = wx.App(False)  # Linux Python 2.7 must exist on global scope
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

from robot.api import logger
from robot.libraries.BuiltIn import BuiltIn
from robot.version import get_version
from robot.utils import abspath, get_error_message, get_link_path, py2to3


class Screenshot(object):
    """Test library for taking screenshots on the machine where tests are run.

    Notice that successfully taking screenshots requires tests to be run with
    a physical or virtual display.

    == Table of contents ==

    %TOC%

    = Using with Python =

    How screenshots are taken when using Python depends on the operating
    system. On OSX screenshots are taken using the built-in ``screencapture``
    utility. On other operating systems you need to have one of the following
    tools or Python modules installed. You can specify the tool/module to use
    when `importing` the library. If no tool or module is specified, the first
    one found will be used.

    - wxPython :: http://wxpython.org :: Required also by RIDE so many Robot
      Framework users already have this module installed.
    - PyGTK :: http://pygtk.org :: This module is available by default on most
      Linux distributions.
    - Pillow :: http://python-pillow.github.io ::
      Only works on Windows. Also the original PIL package is supported.
    - Scrot :: http://en.wikipedia.org/wiki/Scrot :: Not used on Windows.
      Install with ``apt-get install scrot`` or similar.

    Using ``screencapture`` on OSX and specifying explicit screenshot module
    are new in Robot Framework 2.9.2. The support for using ``scrot`` is new
    in Robot Framework 3.0.

    = Using with Jython and IronPython =

    With Jython and IronPython this library uses APIs provided by JVM and .NET
    platforms, respectively. These APIs are always available and thus no
    external modules are needed.

    = Where screenshots are saved =

    By default screenshots are saved into the same directory where the Robot
    Framework log file is written. If no log is created, screenshots are saved
    into the directory where the XML output file is written.

    It is possible to specify a custom location for screenshots using
    ``screenshot_directory`` argument when `importing` the library and
    using `Set Screenshot Directory` keyword during execution. It is also
    possible to save screenshots using an absolute path.

    = ScreenCapLibrary =

    [https://github.com/mihaiparvu/ScreenCapLibrary|ScreenCapLibrary] is an
    external Robot Framework library that can be used as an alternative,
    which additionally provides support for multiple formats, adjusting the
    quality, using GIFs and video capturing.
    """

    ROBOT_LIBRARY_SCOPE = 'TEST SUITE'
    ROBOT_LIBRARY_VERSION = get_version()

    def __init__(self, screenshot_directory=None, screenshot_module=None):
        """Configure where screenshots are saved.

        If ``screenshot_directory`` is not given, screenshots are saved into
        same directory as the log file. The directory can also be set using
        `Set Screenshot Directory` keyword.

        ``screenshot_module`` specifies the module or tool to use when using
        this library on Python outside OSX. Possible values are ``wxPython``,
        ``PyGTK``, ``PIL`` and ``scrot``, case-insensitively. If no value is
        given, the first module/tool found is used in that order. See `Using
        with Python` for more information.

        Examples (use only one of these):
        | =Setting= |  =Value=   |  =Value=   |
        | Library   | Screenshot |            |
        | Library   | Screenshot | ${TEMPDIR} |
        | Library   | Screenshot | screenshot_module=PyGTK |

        Specifying explicit screenshot module is new in Robot Framework 2.9.2.
        """
        self._given_screenshot_dir = self._norm_path(screenshot_directory)
        self._screenshot_taker = ScreenshotTaker(screenshot_module)

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
        return self._norm_path(os.path.join(outdir, log))

    def set_screenshot_directory(self, path):
        """Sets the directory where screenshots are saved.

        It is possible to use ``/`` as a path separator in all operating
        systems. Path to the old directory is returned.

        The directory can also be set in `importing`.
        """
        path = self._norm_path(path)
        if not os.path.isdir(path):
            raise RuntimeError("Directory '%s' does not exist." % path)
        old = self._screenshot_dir
        self._given_screenshot_dir = path
        return old

    def take_screenshot(self, name="screenshot", width="800px"):
        """Takes a screenshot in JPEG format and embeds it into the log file.

        Name of the file where the screenshot is stored is derived from the
        given ``name``. If the ``name`` ends with extension ``.jpg`` or
        ``.jpeg``, the screenshot will be stored with that exact name.
        Otherwise a unique name is created by adding an underscore, a running
        index and an extension to the ``name``.

        The name will be interpreted to be relative to the directory where
        the log file is written. It is also possible to use absolute paths.
        Using ``/`` as a path separator works in all operating systems.

        ``width`` specifies the size of the screenshot in the log file.

        Examples: (LOGDIR is determined automatically by the library)
        | Take Screenshot |                  |     | # LOGDIR/screenshot_1.jpg (index automatically incremented) |
        | Take Screenshot | mypic            |     | # LOGDIR/mypic_1.jpg (index automatically incremented) |
        | Take Screenshot | ${TEMPDIR}/mypic |     | # /tmp/mypic_1.jpg (index automatically incremented) |
        | Take Screenshot | pic.jpg          |     | # LOGDIR/pic.jpg (always uses this file) |
        | Take Screenshot | images/login.jpg | 80% | # Specify both name and width. |
        | Take Screenshot | width=550px      |     | # Specify only width. |

        The path where the screenshot is saved is returned.
        """
        path = self._save_screenshot(name)
        self._embed_screenshot(path, width)
        return path

    def take_screenshot_without_embedding(self, name="screenshot"):
        """Takes a screenshot and links it from the log file.

        This keyword is otherwise identical to `Take Screenshot` but the saved
        screenshot is not embedded into the log file. The screenshot is linked
        so it is nevertheless easily available.
        """
        path = self._save_screenshot(name)
        self._link_screenshot(path)
        return path

    def _save_screenshot(self, basename, directory=None):
        path = self._get_screenshot_path(basename, directory)
        return self._screenshot_to_file(path)

    def _screenshot_to_file(self, path):
        path = self._validate_screenshot_path(path)
        logger.debug('Using %s module/tool for taking screenshot.'
                     % self._screenshot_taker.module)
        try:
            self._screenshot_taker(path)
        except:
            logger.warn('Taking screenshot failed: %s\n'
                        'Make sure tests are run with a physical or virtual '
                        'display.' % get_error_message())
        return path

    def _validate_screenshot_path(self, path):
        path = abspath(self._norm_path(path))
        if not os.path.exists(os.path.dirname(path)):
            raise RuntimeError("Directory '%s' where to save the screenshot "
                               "does not exist" % os.path.dirname(path))
        return path

    def _get_screenshot_path(self, basename, directory):
        directory = self._norm_path(directory) if directory else self._screenshot_dir
        if basename.lower().endswith(('.jpg', '.jpeg')):
            return os.path.join(directory, basename)
        index = 0
        while True:
            index += 1
            path = os.path.join(directory, "%s_%d.jpg" % (basename, index))
            if not os.path.exists(path):
                return path

    def _embed_screenshot(self, path, width):
        link = get_link_path(path, self._log_dir)
        logger.info('<a href="%s"><img src="%s" width="%s"></a>'
                    % (link, link, width), html=True)

    def _link_screenshot(self, path):
        link = get_link_path(path, self._log_dir)
        logger.info("Screenshot saved to '<a href=\"%s\">%s</a>'."
                    % (link, path), html=True)


@py2to3
class ScreenshotTaker(object):

    def __init__(self, module_name=None):
        self._screenshot = self._get_screenshot_taker(module_name)
        self.module = self._screenshot.__name__.split('_')[1]

    def __call__(self, path):
        self._screenshot(path)

    def __nonzero__(self):
        return self.module != 'no'

    def test(self, path=None):
        if not self:
            print("Cannot take screenshots.")
            return False
        print("Using '%s' to take screenshot." % self.module)
        if not path:
            print("Not taking test screenshot.")
            return True
        print("Taking test screenshot to '%s'." % path)
        try:
            self(path)
        except:
            print("Failed: %s" % get_error_message())
            return False
        else:
            print("Success!")
            return True

    def _get_screenshot_taker(self, module_name=None):
        if sys.platform.startswith('java'):
            return self._java_screenshot
        if sys.platform == 'cli':
            return self._cli_screenshot
        if sys.platform == 'darwin':
            return self._osx_screenshot
        if module_name:
            return self._get_named_screenshot_taker(module_name.lower())
        return self._get_default_screenshot_taker()

    def _get_named_screenshot_taker(self, name):
        screenshot_takers = {'wxpython': (wx, self._wx_screenshot),
                             'pygtk': (gdk, self._gtk_screenshot),
                             'pil': (ImageGrab, self._pil_screenshot),
                             'scrot': (self._scrot, self._scrot_screenshot)}
        if name not in screenshot_takers:
            raise RuntimeError("Invalid screenshot module or tool '%s'." % name)
        supported, screenshot_taker = screenshot_takers[name]
        if not supported:
            raise RuntimeError("Screenshot module or tool '%s' not installed."
                               % name)
        return screenshot_taker

    def _get_default_screenshot_taker(self):
        for module, screenshot_taker in [(wx, self._wx_screenshot),
                                         (gdk, self._gtk_screenshot),
                                         (ImageGrab, self._pil_screenshot),
                                         (self._scrot, self._scrot_screenshot),
                                         (True, self._no_screenshot)]:
            if module:
                return screenshot_taker

    def _java_screenshot(self, path):
        size = Toolkit.getDefaultToolkit().getScreenSize()
        rectangle = Rectangle(0, 0, size.width, size.height)
        image = Robot().createScreenCapture(rectangle)
        ImageIO.write(image, 'jpg', File(path))

    def _cli_screenshot(self, path):
        bmp = Bitmap(Screen.PrimaryScreen.Bounds.Width,
                     Screen.PrimaryScreen.Bounds.Height)
        graphics = Graphics.FromImage(bmp)
        try:
            graphics.CopyFromScreen(0, 0, 0, 0, bmp.Size)
        finally:
            graphics.Dispose()
            bmp.Save(path, Imaging.ImageFormat.Jpeg)

    def _osx_screenshot(self, path):
        if self._call('screencapture', '-t', 'jpg', path) != 0:
            raise RuntimeError("Using 'screencapture' failed.")

    def _call(self, *command):
        try:
            return subprocess.call(command, stdout=subprocess.PIPE,
                                   stderr=subprocess.STDOUT)
        except OSError:
            return -1

    @property
    def _scrot(self):
        return os.sep == '/' and self._call('scrot', '--version') == 0

    def _scrot_screenshot(self, path):
        if not path.endswith(('.jpg', '.jpeg')):
            raise RuntimeError("Scrot requires extension to be '.jpg' or "
                               "'.jpeg', got '%s'." % os.path.splitext(path)[1])
        if self._call('scrot', '--silent', path) != 0:
            raise RuntimeError("Using 'scrot' failed.")

    def _wx_screenshot(self, path):
        # depends on wx_app been created
        context = wx.ScreenDC()
        width, height = context.GetSize()
        if wx.__version__ >= '4':
            bitmap = wx.Bitmap(width, height, -1)
        else:
            bitmap = wx.EmptyBitmap(width, height, -1)
        memory = wx.MemoryDC()
        memory.SelectObject(bitmap)
        memory.Blit(0, 0, width, height, context, -1, -1)
        memory.SelectObject(wx.NullBitmap)
        bitmap.SaveFile(path, wx.BITMAP_TYPE_JPEG)

    def _gtk_screenshot(self, path):
        window = gdk.get_default_root_window()
        if not window:
            raise RuntimeError('Taking screenshot failed.')
        width, height = window.get_size()
        pb = gdk.Pixbuf(gdk.COLORSPACE_RGB, False, 8, width, height)
        pb = pb.get_from_drawable(window, window.get_colormap(),
                                  0, 0, 0, 0, width, height)
        if not pb:
            raise RuntimeError('Taking screenshot failed.')
        pb.save(path, 'jpeg')

    def _pil_screenshot(self, path):
        ImageGrab.grab().save(path, 'JPEG')

    def _no_screenshot(self, path):
        raise RuntimeError('Taking screenshots is not supported on this platform '
                           'by default. See library documentation for details.')


if __name__ == "__main__":
    if len(sys.argv) not in [2, 3]:
        sys.exit("Usage: %s <path>|test [wx|pygtk|pil|scrot]"
                 % os.path.basename(sys.argv[0]))
    path = sys.argv[1] if sys.argv[1] != 'test' else None
    module = sys.argv[2] if len(sys.argv) > 2 else None
    ScreenshotTaker(module).test(path)
