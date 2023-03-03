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

import json
import re
from itertools import chain

from robot.model import Tags
from robot.running import ArgInfo, ArgumentSpec, TypeInfo
from robot.utils import getshortdoc, Sortable, setter

from .htmlutils import DocFormatter, DocToHtml, HtmlToText
from .writer import LibdocWriter
from .output import LibdocOutput, get_generation_time


class LibraryDoc:
    """Documentation for a library, a resource file or a suite file."""

    def __init__(self, name='', doc='', version='', type='LIBRARY', scope='TEST',
                 doc_format='ROBOT', source=None, lineno=-1):
        self.name = name
        self._doc = doc
        self.version = version
        self.type = type
        self.scope = scope
        self.doc_format = doc_format
        self.source = source
        self.lineno = lineno
        self.inits = ()
        self.keywords = ()
        self.type_docs = ()

    @property
    def doc(self):
        if self.doc_format == 'ROBOT' and '%TOC%' in self._doc:
            return self._add_toc(self._doc)
        return self._doc

    def _add_toc(self, doc):
        toc = self._create_toc(doc)
        return '\n'.join(line if line.strip() != '%TOC%' else toc
                         for line in doc.splitlines())

    def _create_toc(self, doc):
        entries = re.findall(r'^\s*=\s+(.+?)\s+=\s*$', doc, flags=re.MULTILINE)
        if self.inits:
            entries.append('Importing')
        if self.keywords:
            entries.append('Keywords')
        return '\n'.join('- `%s`' % entry for entry in entries)

    @setter
    def doc_format(self, format):
        return format or 'ROBOT'

    @setter
    def inits(self, inits):
        """Initializer docs as :class:`~KeywordDoc` instances."""
        return self._process_keywords(inits)

    @setter
    def keywords(self, kws):
        """Keyword docs as :class:`~KeywordDoc` instances."""
        return self._process_keywords(kws)

    @setter
    def type_docs(self, type_docs):
        return set(type_docs)

    def _process_keywords(self, kws):
        for keyword in kws:
            keyword.parent = self
        return sorted(kws)

    @property
    def all_tags(self):
        return Tags(chain.from_iterable(kw.tags for kw in self.keywords))

    def save(self, output=None, format='HTML', theme=None):
        with LibdocOutput(output, format) as outfile:
            LibdocWriter(format, theme).write(self, outfile)

    def convert_docs_to_html(self):
        formatter = DocFormatter(self.keywords, self.type_docs, self.doc, self.doc_format)
        self._doc = formatter.html(self.doc, intro=True)
        for item in self.inits + self.keywords:
            # If 'shortdoc' is not set, it is generated automatically based on 'doc'
            # when accessed. Generate and set it to avoid HTML format affecting it.
            item.shortdoc = item.shortdoc
            item.doc = formatter.html(item.doc)
        for type_doc in self.type_docs:
            # Standard docs are always in ROBOT format ...
            if type_doc.type == type_doc.STANDARD:
                # ... unless they have been converted to HTML already.
                if not type_doc.doc.startswith('<p>'):
                    type_doc.doc = DocToHtml('ROBOT')(type_doc.doc)
            else:
                type_doc.doc = formatter.html(type_doc.doc)
        self.doc_format = 'HTML'

    def to_dictionary(self, include_private=False, theme=None):
        data = {
            'specversion': 2,
            'name': self.name,
            'doc': self.doc,
            'version': self.version,
            'generated': get_generation_time(),
            'type': self.type,
            'scope': self.scope,
            'docFormat': self.doc_format,
            'source': str(self.source) if self.source else None,
            'lineno': self.lineno,
            'tags': list(self.all_tags),
            'inits': [init.to_dictionary() for init in self.inits],
            'keywords': [kw.to_dictionary() for kw in self.keywords
                         if include_private or not kw.private],
            # 'dataTypes' was deprecated in RF 5, 'typedoc' should be used instead.
            'dataTypes': self._get_data_types(self.type_docs),
            'typedocs': [t.to_dictionary() for t in sorted(self.type_docs)]
        }
        if theme:
            data['theme'] = theme.lower()
        return data

    def _get_data_types(self, types):
        enums = sorted(t for t in types if t.type == 'Enum')
        typed_dicts = sorted(t for t in types if t.type == 'TypedDict')
        return {
            'enums': [t.to_dictionary(legacy=True) for t in enums],
            'typedDicts': [t.to_dictionary(legacy=True) for t in typed_dicts]
        }

    def to_json(self, indent=None, include_private=True, theme=None):
        data = self.to_dictionary(include_private, theme)
        return json.dumps(data, indent=indent)


class KeywordDoc(Sortable):
    """Documentation for a single keyword or an initializer."""

    def __init__(self, name='', args=None, doc='', shortdoc='', tags=(), private=False,
                 deprecated=False, source=None, lineno=-1, parent=None):
        self.name = name
        self.args = args or ArgumentSpec()
        self.doc = doc
        self._shortdoc = shortdoc
        self.tags = Tags(tags)
        self.private = private
        self.deprecated = deprecated
        self.source = source
        self.lineno = lineno
        self.parent = parent
        # Map argument types to type documentations.
        self.type_docs = {arg.name: {} for arg in self.args}

    @property
    def shortdoc(self):
        return self._shortdoc or self._doc_to_shortdoc()

    def _doc_to_shortdoc(self):
        if self.parent and self.parent.doc_format == 'HTML':
            doc = HtmlToText().get_shortdoc_from_html(self.doc)
        else:
            doc = self.doc
        return ' '.join(getshortdoc(doc).splitlines())

    @shortdoc.setter
    def shortdoc(self, shortdoc):
        self._shortdoc = shortdoc

    @property
    def _sort_key(self):
        return self.name.lower()

    def to_dictionary(self):
        data = {
            'name': self.name,
            'args': [self._arg_to_dict(arg) for arg in self.args],
            'doc': self.doc,
            'shortdoc': self.shortdoc,
            'tags': list(self.tags),
            'source': str(self.source) if self.source else None,
            'lineno': self.lineno
        }
        if self.private:
            data['private'] = True
        if self.deprecated:
            data['deprecated'] = True
        return data

    def _arg_to_dict(self, arg: ArgInfo):
        type_docs = self.type_docs.get(arg.name, {})
        return {
            'name': arg.name,
            'type': self._type_to_dict(arg.type, type_docs),
            'types': arg.types_reprs,
            'typedocs': type_docs,
            'defaultValue': arg.default_repr,
            'kind': arg.kind,
            'required': arg.required,
            'repr': str(arg)
        }

    def _type_to_dict(self, type: TypeInfo, type_docs: dict):
        if not type:
            return None
        return {'name': type.name,
                'typedoc': type_docs.get(type.name),
                'nested': [self._type_to_dict(t, type_docs) for t in type.nested],
                'union': type.is_union}
