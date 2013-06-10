#!/usr/bin/env python

#  Copyright 2008-2013 Nokia Siemens Networks Oyj
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

"""risto.py -- Robot Framework's Historical Reporting Tool

Version: <VERSION>

Usage:  risto.py options input_files
  or:   risto.py options1 --- options2 --- optionsN --- input files
  or:   risto.py --argumentfile path

risto.py plots graphs about test execution history based on statistics
read from Robot Framework output files. Actual drawing is handled by
Matplotlib tool, which must be installed separately.  More information
about it, including installation instructions, can be found from
http://matplotlib.sourceforge.net.

By default risto.py draws total, passed and failed graphs for critical
tests and all tests, but it is possible to omit some of these graphs
and also to add graphs by tags. Names of test rounds that are shown on
the x-axis are, by default, got from the paths to input files.
Alternatively, names can be got from the metadata of the top level
test suite (see Robot Framework's '--metadata' option for more details).

The graph is saved into a file specified with '--output' option, and the
output format is got from the file extension. Supported formats depend on the
installed Matplotlib back-ends, but at least PNG ought to be always available.
If the output file is omitted, the graph is opened into Matplotlib's image
viewer (which requires Matplotlib to be installed with some graphical
front-end).

It is possible to draw multiple graphs with different options at once. This
is done by separating different option groups with three or more hyphens
('---'). Note that in this case also paths to input files need to be
separated from last options similarly.

Instead of giving all options from the command line, it is possible to read
them from a file specified with '--argument' option. In an argument file
options and their possible argument are listed one per line, and option
groups are separated with lines of three or more hyphens. Empty lines and
lines starting with a hash mark ('#') are ignored.

Options:
  -C --nocritical     Do not plot graphs for critical tests.
  -A --noall          Do not plot graphs for all tests.
  -T --nototals       Do not plot total graphs.
  -P --nopassed       Do not plot passed graphs.
  -F --nofailed       Do not plot failed graphs.
  -t --tag name *     Add graphs for these tags. Name can contain '*' and
                      '?' as wildcards.
  -o --output path    Path to the image file to create. If not given, the
                      image is opened into Matplotlib's image viewer.
  -i --title title    Title of the graph. Underscores in the given title
                      are converted to spaces. By default there is no
                      title.
  -w --width inches   Width of the image. Default is 800.
  -h --height inches  Height of the image. Default is 400.
  -f --font size      Font size used for legends and labels. Default is 8.
  -m --marker size    Size of marked used with tag graphs. Default is 5.
  -x --xticks num     Maximum number of ticks in x-axis. Default is 15.
  -n --namemeta name  Name of the metadata of the top level test suite
                      where to get name of the test round. By default names
                      are got from paths to input files.
  ---                 Used to group options when creating multiple images
                      at once.
  --argumentfile path  Read arguments from the specified file.
  --verbose           Verbose output.
  --help              Print this help.
  --version           Print version information.

Examples:
  risto.py --output history.png output1.xml output2.xml output3.xml
  risto.py --title My_Report --noall --namemeta Date --output out.png *.xml
  risto.py --nopassed --tag smoke --tag iter-* results/*/output.xml
  risto.py -CAP -t tag1 --- -CAP -t tag2 --- -CAP -t tag3 --- outputs/*.xml
  risto.py --argumentfile arguments.txt

     ====[arguments.txt]===================
     --title Overview
     --output overview.png
     ----------------------
     --nocritical
     --noall
     --nopassed
     --tag smoke1
     --title Smoke Tests
     --output smoke.png
     ----------------------
     path/to/*.xml
     ======================================
"""

from __future__ import with_statement
import os.path
import sys
import glob

try:
    from matplotlib import pylab
    from matplotlib.lines import Line2D
    from matplotlib.font_manager import FontProperties
    from matplotlib.pyplot import get_current_fig_manager
except ImportError:
    raise ImportError('Could not import Matplotlib modules. Install it form '
                      'http://matplotlib.sourceforge.net/')

try:
    from robot import utils
    from robot.errors import DataError, Information
except ImportError:
    raise ImportError('Could not import Robot Framework modules. '
                      'Make sure you have Robot Framework installed.')


__version__ = '1.0.2'


class AllStatistics(object):

    def __init__(self, paths, namemeta=None, verbose=False):
        self._stats = self._get_stats(paths, namemeta, verbose)
        self._tags = self._get_tags()

    def _get_stats(self, paths, namemeta, verbose):
        paths = self._glob_paths(paths)
        if namemeta:
            return [Statistics(path, namemeta=namemeta, verbose=verbose)
                    for path in paths]
        return [Statistics(path, name, verbose=verbose)
                for path, name in zip(paths, self._get_names(paths))]

    def _glob_paths(self, orig):
        paths = []
        for path in orig:
            paths.extend(glob.glob(path))
        if not paths:
            raise DataError("No valid paths given.")
        return paths

    def _get_names(self, paths):
        paths = [os.path.splitext(os.path.abspath(p))[0] for p in paths]
        path_tokens = [p.replace('\\', '/').split('/') for p in paths]
        min_tokens = min(len(t) for t in path_tokens)
        index = -1
        while self._tokens_are_same_at_index(path_tokens, index):
            index -= 1
            if abs(index) > min_tokens:
                index = -1
                break
        names = [tokens[index] for tokens in path_tokens]
        return [utils.printable_name(n, code_style=True) for n in names]

    def _tokens_are_same_at_index(self, token_list, index):
        first = token_list[0][index]
        for tokens in token_list[1:]:
            if first != tokens[index]:
                return False
        return len(token_list) > 1

    def _get_tags(self):
        stats = {}
        for statistics in self._stats:
            stats.update(statistics.tags)
        return [stat.name for stat in sorted(stats.values())]

    def plot(self, plotter):
        plotter.set_axis(self._stats)
        plotter.critical_tests([s.critical_tests for s in self._stats])
        plotter.all_tests([s.all_tests for s in self._stats])
        for tag in self._tags:
            plotter.tag([s[tag] for s in self._stats])


class Statistics(object):

    def __init__(self, path, name=None, namemeta=None, verbose=False):
        if verbose:
            print path
        root = utils.ET.ElementTree(file=path).getroot()
        self.name = self._get_name(name, namemeta, root)
        stats = root.find('statistics')
        crit_node, all_node = list(stats.find('total'))
        self.critical_tests = Stat(crit_node)
        self.all_tests = Stat(all_node)
        self.tags = dict((n.text, Stat(n)) for n in stats.find('tag'))

    def _get_name(self, name, namemeta, root):
        if namemeta is None:
            if name is None:
                raise TypeError("Either 'name' or 'namemeta' must be given")
            return name
        metadata = root.find('suite').find('metadata')
        if metadata:
            for item in metadata:
                if item.get('name','').lower() == namemeta.lower():
                    return item.text
        raise DataError("No metadata matching '%s' found" % namemeta)

    def __getitem__(self, name):
        try:
            return self.tags[name]
        except KeyError:
            return EmptyStat(name)


class Stat(object):

    def __init__(self, node):
        self.name = node.text
        self.passed = int(node.get('pass'))
        self.failed = int(node.get('fail'))
        self.total = self.passed + self.failed
        self.doc = node.get('doc', '')
        info = node.get('info', '')
        self.critical = info == 'critical'
        self.non_critical = info == 'non-critical'
        self.combined = info == 'combined'

    def __cmp__(self, other):
        if self.critical != other.critical:
            return self.critical is True and -1 or 1
        if self.non_critical != other.non_critical:
            return self.non_critical is True and -1 or 1
        if self.combined != other.combined:
            return self.combined is True and -1 or 1
        return cmp(self.name, other.name)


class EmptyStat(Stat):

    def __init__(self, name):
        self.name = name
        self.passed = self.failed = self.total = 0
        self.doc = ''
        self.critical = self.non_critical = self.combined = False


class Legend(Line2D):

    def __init__(self, **attrs):
        styles = {'color': '0.5', 'linestyle': '-', 'linewidth': 1}
        styles.update(attrs)
        Line2D.__init__(self, [], [], **styles)


class Plotter(object):
    _total_color = 'blue'
    _pass_color = 'green'
    _fail_color = 'red'
    _background_color = '0.8'
    _xtick_rotation = 20
    _default_width = 800
    _default_height = 400
    _default_font = 8
    _default_marker = 5
    _default_xticks = 15
    _dpi = 100
    _marker_symbols = 'o s D ^ v < > d p | + x 1 2 3 4 . ,'.split()

    def __init__(self, tags=None, critical=True, all=True, totals=True,
                 passed=True, failed=True, width=None, height=None, font=None,
                 marker=None, xticks=None):
        self._xtick_limit, self._font_size, self._marker_size, width, height  \
               = self._get_sizes(xticks, font, marker, width, height)
        self._figure = pylab.figure(figsize=(width, height))
        self._axes = self._figure.add_axes([0.05, 0.15, 0.65, 0.70])
        # axes2 is used only for getting ytick labels also on right side
        self._axes2 = self._axes.twinx()
        self._axes2.set_xticklabels([], visible=False)
        self._tags = tags or []
        self._critical = critical
        self._all = all
        self._totals = totals
        self._passed = passed
        self._failed = failed
        self._legends = []
        self._markers = iter(self._marker_symbols)

    def _get_sizes(self, xticks, font, marker, width, height):
        xticks = xticks or self._default_xticks
        font   = font   or self._default_font
        marker = marker or self._default_marker
        width  = width  or self._default_width
        height = height or self._default_height
        try:
            return (int(xticks), int(font), int(marker),
                    float(width)/self._dpi, float(height)/self._dpi)
        except ValueError:
            raise DataError('Width, height, font and xticks must be numbers.')

    def set_axis(self, stats):
        slen = len(stats)
        self._indexes = range(slen)
        self._xticks = self._get_xticks(slen, self._xtick_limit)
        self._axes.set_xticks(self._xticks)
        self._axes.set_xticklabels([stats[i].name for i in self._xticks],
                                   rotation=self._xtick_rotation,
                                   size=self._font_size)
        self._scale = (slen-1, max(s.all_tests.total for s in stats))

    def _get_xticks(self, slen, limit):
        if slen <= limit:
            return range(slen)
        interval, extra = divmod(slen-1, limit-1)  # 1 interval less than ticks
        if interval < 2:
            interval = 2
            limit, extra = divmod(slen-1, interval)
            limit += 1
        return [ self._get_index(i, interval, extra) for i in range(limit) ]

    def _get_index(self, count, interval, extra):
        if count < extra:
            extra = count
        return count * interval + extra

    def critical_tests(self, stats):
        if self._critical:
            line = {'linestyle': '--', 'linewidth': 1}
            self._plot(self._indexes, stats, **line)
            self._legends.append(Legend(label='critical tests', **line))

    def all_tests(self, stats):
        if self._all:
            line = {'linestyle': ':', 'linewidth': 1}
            self._plot(self._indexes, stats, **line)
            self._legends.append(Legend(label='all tests', **line))

    def tag(self, stats):
        if utils.MultiMatcher(self._tags).match(stats[0].name):
            line = {'linestyle': '-', 'linewidth': 0.3}
            mark = {'marker': self._get_marker(),
                    'markersize': self._marker_size}
            self._plot(self._indexes, stats, **line)
            markers = [stats[index] for index in self._xticks]
            self._plot(self._xticks, markers, linestyle='', **mark)
            line.update(mark)
            label = self._get_tag_label(stats)
            self._legends.append(Legend(label=label, **line))

    def _get_tag_label(self, stats):
        label = stats[0].name
        # need to go through all stats because first can be EmptyStat
        for stat in stats:
            if stat.critical:
                return label + ' (critical)'
            if stat.non_critical:
                return label + ' (non-critical)'
        return label

    def _get_marker(self):
        try:
            return self._markers.next()
        except StopIteration:
            return ''

    def _plot(self, xaxis, stats, **attrs):
        total, passed, failed \
               = zip(*[(s.total, s.passed, s.failed) for s in stats])
        if self._totals:
            self._axes.plot(xaxis, total, color=self._total_color, **attrs)
        if self._passed:
            self._axes.plot(xaxis, passed, color=self._pass_color, **attrs)
        if self._failed:
            self._axes.plot(xaxis, failed, color=self._fail_color, **attrs)

    def draw(self, output=None, title=None):
        self._set_scale(self._axes)
        self._set_scale(self._axes2)
        self._set_legends(self._legends[:])
        if title:
            title = title.replace('_', ' ')
            self._axes.set_title(title, fontsize=self._font_size*1.8)
        if output:
            self._figure.savefig(output, facecolor=self._background_color,
                                 dpi=self._dpi)
        else:
            if not hasattr(self._figure, 'show'):
                raise DataError('Could not find a graphical front-end for '
                                'Matplotlib.')
            self._figure.show()
            if title:
                figman = get_current_fig_manager()
                figman.set_window_title(title)

    def _set_scale(self, axes):
        width, height = self._scale
        axes.axis([-width*0.01, width*1.01, -height*0.04, height*1.04])

    def _set_legends(self, legends):
        legends.insert(0, Legend(label='Styles:', linestyle=''))
        legends.append(Legend(label='', linestyle=''))
        legends.append(Legend(label='Colors:', linestyle=''))
        if self._totals:
            legends.append(Legend(label='total', color=self._total_color))
        if self._passed:
            legends.append(Legend(label='passed', color=self._pass_color))
        if self._failed:
            legends.append(Legend(label='failed', color=self._fail_color))
        labels = [l.get_label() for l in legends]
        self._figure.legend(legends, labels, loc='center right',
                            numpoints=3, borderpad=0.1,
                            prop=FontProperties(size=self._font_size))


class Ristopy(object):

    def __init__(self):
        self._arg_parser = utils.ArgumentParser(__doc__, version=__version__)

    def main(self, args):
        args = self._process_possible_argument_file(args)
        try:
            opt_groups, paths = self._split_to_option_groups_and_paths(args)
        except ValueError:
            viewer_open = self._plot_one_graph(args)
        else:
            viewer_open = self._plot_multiple_graphs(opt_groups, paths)

        if viewer_open:
            try:
                raw_input('Press enter to exit.\n')
            except (EOFError, KeyboardInterrupt):
                pass
            pylab.close('all')

    def _plot_one_graph(self, args):
        opts, paths = self._arg_parser.parse_args(args)
        stats = AllStatistics(paths, opts['namemeta'], opts['verbose'])
        output = self._plot(stats, opts)
        return output is None

    def _plot_multiple_graphs(self, opt_groups, paths):
        viewer_open = False
        stats = AllStatistics(paths, opt_groups[0]['namemeta'],
                              opt_groups[0]['verbose'])
        for opts in opt_groups:
            output = self._plot(stats, opts)
            viewer_open = output is None or viewer_open
        return viewer_open

    def _plot(self, stats, opts):
        plotter = Plotter(opts['tag'],  not opts['nocritical'],
                          not opts['noall'], not opts['nototals'],
                          not opts['nopassed'], not opts['nofailed'],
                          opts['width'], opts['height'], opts['font'],
                          opts['marker'], opts['xticks'])
        stats.plot(plotter)
        plotter.draw(opts['output'], opts['title'])
        if opts['output']:
            print os.path.abspath(opts['output'])
        return opts['output']

    def _process_possible_argument_file(self, args):
        try:
            index = args.index('--argumentfile')
        except ValueError:
            return args
        path = args[index+1]
        try:
            lines = open(path).readlines()
        except IOError:
            raise DataError("Invalid argument file '%s'" % path)
        fargs = []
        for line in lines:
            line = line.strip()
            if line == '' or line.startswith('#'):
                continue
            elif line.startswith('-'):
                fargs.extend(line.split(' ', 1))
            else:
                fargs.append(line)
        args[index:index+2] = fargs
        return args

    def _split_to_option_groups_and_paths(self, args):
        opt_groups = []
        current = []
        for arg in args:
            if arg.replace('-', '') == '' and len(arg) >= 3:
                opts = self._arg_parser.parse_args(current)[0]
                opt_groups.append(opts)
                current = []
            else:
                current.append(arg)
        if opt_groups:
            return opt_groups, current
        raise ValueError("Nothing to split")


if __name__ == '__main__':
    try:
        Ristopy().main(sys.argv[1:])
    except Information, msg:
        print str(msg)
    except DataError, err:
        print '%s\n\nTry --help for usage information.' % err
