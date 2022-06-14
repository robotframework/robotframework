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
    test_teardown = None
    test_template = None
    test_timeout = None
    force_tags = None
    default_tags = None
    tags = None
    setup = None
    teardown = None
    template = None
    timeout = None
    arguments = None
    return_ = None
    bdd_prefixes = set()  # These are not used yet

    @classmethod
    def get_languages(cls, languages):
        languages = cls._resolve_languages(languages)
        available = {c.__name__.lower(): c for c in cls.__subclasses__()}
        returned = []
        for lang in languages:
            if lang.lower() in available:
                returned.append(available[lang.lower()])
            else:
                returned.extend(cls._import_languages(lang))
        return [subclass() for subclass in returned]

    @classmethod
    def _resolve_languages(cls, languages):
        if not languages:
            languages = []
        if is_string(languages):
            languages = [languages]
        if 'en' not in languages:
            languages.append('en')
        return languages

    @classmethod
    def _import_languages(cls, lang):
        def find_subclass(member):
            return (inspect.isclass(member)
                    and issubclass(member, Language)
                    and member is not Language)
        # FIXME: error handling
        if os.path.exists(lang):
            lang = os.path.abspath(lang)
        module = Importer().import_module(lang)
        return [value for _, value in inspect.getmembers(module, find_subclass)]

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
            self.test_teardown: En.test_teardown,
            self.test_template: En.test_template,
            self.test_timeout: En.test_timeout,
            self.force_tags: En.force_tags,
            self.default_tags: En.default_tags,
            self.tags: En.tags,
            self.setup: En.setup,
            self.teardown: En.teardown,
            self.template: En.template,
            self.timeout: En.timeout,
            self.arguments: En.arguments,
            self.return_: En.return_
        }
        settings.pop(None, None)
        return settings


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
    test_teardown = 'Test Teardown'
    test_template = 'Test Template'
    force_tags = 'Force Tags'
    default_tags = 'Default Tags'
    test_timeout = 'Test Timeout'
    setup = 'Setup'
    teardown = 'Teardown'
    template = 'Template'
    tags = 'Tags'
    timeout = 'Timeout'
    arguments = 'Arguments'
    return_ = 'Return'
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
    test_teardown = 'Testin Purku'
    test_template = 'Testin Malli'
    force_tags = 'Testin Tagit'
    default_tags = 'Oletus Tagit'
    test_timeout = 'Testin Aikaraja'
    setup = 'Alustus'
    teardown = 'Purku'
    template = 'Malli'
    tags = 'Tagit'
    timeout = 'Aikaraja'
    arguments = 'Argumentit'
    return_ = 'Paluuarvo'
    bdd_prefixes = {}
