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

import inspect
import os.path

from robot.utils import is_string, Importer


class Languages:

    def __init__(self, languages):
        self.languages = self._get_languages(languages)
        self.setting_headers = set()
        self.variable_headers = set()
        self.test_case_headers = set()
        self.task_headers = set()
        self.keyword_headers = set()
        self.comment_headers = set()
        self.settings = {}
        self.bdd_prefixes = set()
        for lang in self.languages:
            self.setting_headers |= lang.setting_headers
            self.variable_headers |= lang.variable_headers
            self.test_case_headers |= lang.test_case_headers
            self.task_headers |= lang.task_headers
            self.keyword_headers |= lang.keyword_headers
            self.comment_headers |= lang.comment_headers
            self.settings.update(lang.settings)
            self.bdd_prefixes |= lang.bdd_prefixes

    def _get_languages(self, languages):
        languages = self._resolve_languages(languages)
        available = {c.__name__.lower(): c for c in Language.__subclasses__()}
        returned = []
        for lang in languages:
            if lang.lower() in available:
                returned.append(available[lang.lower()])
            else:
                returned.extend(self._import_languages(lang))
        return [subclass() for subclass in returned]

    def _resolve_languages(self, languages):
        if not languages:
            languages = []
        if is_string(languages):
            languages = [languages]
        if 'en' not in languages:
            languages.append('en')
        return languages

    def _import_languages(self, lang):
        def is_language(member):
            return (inspect.isclass(member)
                    and issubclass(member, Language)
                    and member is not Language)
        if os.path.exists(lang):
            lang = os.path.abspath(lang)
        module = Importer('language file').import_module(lang)
        return [value for _, value in inspect.getmembers(module, is_language)]

    def translate_setting(self, name):
        return self.settings.get(name, name)

    def __iter__(self):
        return iter(self.languages)


class Language:
    setting_headers = set()
    variable_headers = set()
    test_case_headers = set()
    task_headers = set()
    keyword_headers = set()
    comment_headers = set()
    library = None
    resource = None
    variables = None
    documentation = None
    metadata = None
    suite_setup = None
    suite_teardown = None
    test_setup = None
    task_setup = None
    test_teardown = None
    task_teardown = None
    test_template = None
    task_template = None
    test_timeout = None
    task_timeout = None
    test_tags = None
    task_tags = None
    keyword_tags = None
    tags = None
    setup = None
    teardown = None
    template = None
    timeout = None
    arguments = None
    bdd_prefixes = set()

    @property
    def settings(self):
        settings = {
            self.library: En.library,
            self.resource: En.resource,
            self.variables: En.variables,
            self.documentation: En.documentation,
            self.metadata: En.metadata,
            self.suite_setup: En.suite_setup,
            self.suite_teardown: En.suite_teardown,
            self.test_setup: En.test_setup,
            self.task_setup: En.task_setup,
            self.test_teardown: En.test_teardown,
            self.task_teardown: En.task_teardown,
            self.test_template: En.test_template,
            self.task_template: En.task_template,
            self.test_timeout: En.test_timeout,
            self.task_timeout: En.task_timeout,
            self.test_tags: En.test_tags,
            self.task_tags: En.task_tags,
            self.keyword_tags: En.keyword_tags,
            self.tags: En.tags,
            self.setup: En.setup,
            self.teardown: En.teardown,
            self.template: En.template,
            self.timeout: En.timeout,
            self.arguments: En.arguments,
        }
        return {name.title(): settings[name] for name in settings if name}


class En(Language):
    setting_headers = {'Settings', 'Setting'}
    variable_headers = {'Variables', 'Variable'}
    test_case_headers = {'Test Cases', 'Test Case'}
    task_headers = {'Tasks', 'Task'}
    keyword_headers = {'Keywords', 'Keyword'}
    comment_headers = {'Comments', 'Comment'}
    library = 'Library'
    resource = 'Resource'
    variables = 'Variables'
    documentation = 'Documentation'
    metadata = 'Metadata'
    suite_setup = 'Suite Setup'
    suite_teardown = 'Suite Teardown'
    test_setup = 'Test Setup'
    task_setup = 'Task Setup'
    test_teardown = 'Test Teardown'
    task_teardown = 'Task Teardown'
    test_template = 'Test Template'
    task_template = 'Task Template'
    test_timeout = 'Test Timeout'
    task_timeout = 'Task Timeout'
    test_tags = 'Test Tags'
    task_tags = 'Task Tags'
    keyword_tags = 'Keyword Tags'
    setup = 'Setup'
    teardown = 'Teardown'
    template = 'Template'
    tags = 'Tags'
    timeout = 'Timeout'
    arguments = 'Arguments'
    bdd_prefixes = {'Given', 'When', 'Then', 'And', 'But'}


class Fi(Language):
    # FIXME: Update based on terms agreed at
    # https://robotframework.crowdin.com/robot-framework
    setting_headers = {'Asetukset', 'Asetus'}
    variable_headers = {'Muuttujat', 'Muuttuja'}
    test_case_headers = {'Testit', 'Testi'}
    task_headers = {'Tehtävät', 'Tehtävä'}
    keyword_headers = {'Avainsanat', 'Avainsana'}
    comment_headers = {'Kommentit', 'Kommentti'}
    library = 'Kirjasto'
    resource = 'Resurssi'
    variables = 'Muuttujat'
    documentation = 'Dokumentaatio'
    metadata = 'Metadata'
    suite_setup = 'Setin Alustus'
    suite_teardown = 'Setin Purku'
    test_setup = 'Testin Alustus'
    task_setup = 'Tehtävän Alustus'
    test_teardown = 'Testin Purku'
    task_teardown = 'Tehtävän Purku'
    test_template = 'Testin Malli'
    task_template = 'Tehtävän Malli'
    test_timeout = 'Testin Aikaraja'
    task_timeout = 'Tehtävän Aikaraja'
    test_tags = 'Testin Tagit'
    task_tags = 'Tehtävän Tagit'
    keyword_tags = 'Avainsanan Tagit'
    setup = 'Alustus'
    teardown = 'Purku'
    template = 'Malli'
    tags = 'Tagit'
    timeout = 'Aikaraja'
    arguments = 'Argumentit'
    bdd_prefixes = {'Oletetaan', 'Kun', 'Niin', 'Ja', 'Mutta'}
