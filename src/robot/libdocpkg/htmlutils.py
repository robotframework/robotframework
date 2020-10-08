import re
try:
    from urllib import quote
except ImportError:
    from urllib.parse import quote

from robot.errors import DataError
from robot.utils import html_escape, html_format, NormalizedDict
from robot.utils.htmlformatters import HeaderFormatter


class DocFormatter(object):
    _header_regexp = re.compile(r'<h([234])>(.+?)</h\1>')
    _name_regexp = re.compile('`(.+?)`')

    def __init__(self, keywords, introduction, doc_format='ROBOT'):
        self._doc_to_html = DocToHtml(doc_format)
        self._targets = self._get_targets(keywords, introduction,
                                          robot_format=doc_format == 'ROBOT')

    def _get_targets(self, keywords, introduction, robot_format):
        targets = {
            'introduction': 'Introduction',
            'library introduction': 'Introduction',
            'importing': 'Importing',
            'library importing': 'Importing',
            'keywords': 'Keywords'
        }
        for kw in keywords:
            targets[kw.name] = kw.name
        if robot_format:
            for header in self._yield_header_targets(introduction):
                targets[header] = header
        return self._escape_and_encode_targets(targets)

    def _yield_header_targets(self, introduction):
        headers = HeaderFormatter()
        for line in introduction.splitlines():
            match = headers.match(line.strip())
            if match:
                yield match.group(2)

    def _escape_and_encode_targets(self, targets):
        return NormalizedDict((html_escape(key), self._encode_uri_component(value))
                              for key, value in targets.items())

    def _encode_uri_component(self, value):
        # Emulates encodeURIComponent javascript function
        return quote(value.encode('UTF-8'), safe="-_.!~*'()")

    def html(self, doc, intro=False):
        doc = self._doc_to_html(doc)
        if intro:
            doc = self._header_regexp.sub(r'<h\1 id="\2">\2</h\1>', doc)
        return self._name_regexp.sub(self._link_keywords, doc)

    def _link_keywords(self, match):
        name = match.group(1)
        if name in self._targets:
            return '<a href="#%s" class="name">%s</a>' % (self._targets[name], name)
        return '<span class="name">%s</span>' % name


class DocToHtml(object):

    def __init__(self, doc_format):
        self._formatter = self._get_formatter(doc_format)

    def _get_formatter(self, doc_format):
        try:
            return {'ROBOT': html_format,
                    'TEXT': self._format_text,
                    'HTML': lambda doc: doc,
                    'REST': self._format_rest}[doc_format]
        except KeyError:
            raise DataError("Invalid documentation format '%s'." % doc_format)

    def _format_text(self, doc):
        return '<p style="white-space: pre-wrap">%s</p>' % html_escape(doc)

    def _format_rest(self, doc):
        try:
            from docutils.core import publish_parts
        except ImportError:
            raise DataError("reST format requires 'docutils' module to be installed.")
        parts = publish_parts(doc, writer_name='html',
                              settings_overrides={'syntax_highlight': 'short'})
        return parts['html_body']

    def __call__(self, doc):
        return self._formatter(doc)


class HtmlToText(object):

    html_tags = {
        'b': '*',
        'i': '_',
        'strong': '*',
        'em': '_',
        'code': '``'
    }

    single_chars = {
        '<br>': '\n',
        '<br/>': '\n',
        '&amp;': '&',
        '&lt;': '<',
        '&gt;': '>',
        '&quot;': '"',
        '&apos;': "'"
    }

    def get_shortdoc_from_html(self, doc):
        match = re.search(r'<p.*?>(.*?)</p>', doc, re.DOTALL)
        if match:
            doc = match.group(1)
        doc = self.html_to_plain_text(doc)
        return doc

    def html_to_plain_text(self, doc):
        for tag, repl in self.html_tags.items():
            doc = re.sub('(<%(tag)s>)(.*?)(</%(tag)s>)' % {'tag': tag},
                         lambda m: repl + m.group(2) + repl, doc, flags=re.DOTALL)
        doc = re.sub("|".join(map(re.escape, self.single_chars.keys())),
                     lambda match: self.single_chars[match.group(0)], doc)
        return doc
