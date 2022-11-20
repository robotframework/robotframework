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

from robot.utils import normalize, normalize_whitespace, RecommendationFinder

from .tokens import Token


class Settings:
    names = ()
    aliases = {}
    multi_use = (
        'Metadata',
        'Library',
        'Resource',
        'Variables'
    )
    single_value = (
        'Resource',
        'Test Timeout',
        'Test Template',
        'Timeout',
        'Template'
    )
    name_and_arguments = (
        'Metadata',
        'Suite Setup',
        'Suite Teardown',
        'Test Setup',
        'Test Teardown',
        'Test Template',
        'Setup',
        'Teardown',
        'Template',
        'Resource',
        'Variables'
    )
    name_arguments_and_with_name = (
        'Library',
    )

    def __init__(self, languages):
        self.settings = {n: None for n in self.names}
        self.languages = languages

    def lex(self, statement):
        setting = statement[0]
        orig = self._format_name(setting.value)
        name = normalize_whitespace(orig).title()
        name = self.languages.settings.get(name, name)
        if name in self.aliases:
            name = self.aliases[name]
        try:
            self._validate(orig, name, statement)
        except ValueError as err:
            self._lex_error(setting, statement[1:], err.args[0])
        else:
            self._lex_setting(setting, statement[1:], name)

    def _format_name(self, name):
        return name

    def _validate(self, orig, name, statement):
        if name not in self.settings:
            message = self._get_non_existing_setting_message(orig, name)
            raise ValueError(message)
        if self.settings[name] is not None and name not in self.multi_use:
            raise ValueError(f"Setting '{orig}' is allowed only once. "
                             f"Only the first value is used.")
        if name in self.single_value and len(statement) > 2:
            raise ValueError(f"Setting '{orig}' accepts only one value, "
                             f"got {len(statement)-1}.")

    def _get_non_existing_setting_message(self, name, normalized):
        if self._is_valid_somewhere(normalized):
            return self._not_valid_here(name)
        return RecommendationFinder(normalize).find_and_format(
            name=normalized,
            candidates=tuple(self.settings) + tuple(self.aliases),
            message=f"Non-existing setting '{name}'."
        )

    def _is_valid_somewhere(self, normalized):
        for cls in Settings.__subclasses__():
            if normalized in cls.names or normalized in cls.aliases:
                return True
        return False

    def _not_valid_here(self, name):
        raise NotImplementedError

    def _lex_error(self, setting, values, error):
        setting.set_error(error)
        for token in values:
            token.type = Token.COMMENT

    def _lex_setting(self, setting, values, name):
        self.settings[name] = values
        # TODO: Change token type from 'FORCE TAGS' to 'TEST TAGS' in RF 7.0.
        setting.type = name.upper() if name != 'Test Tags' else 'FORCE TAGS'
        if name in self.name_and_arguments:
            self._lex_name_and_arguments(values)
        elif name in self.name_arguments_and_with_name:
            self._lex_name_arguments_and_with_name(values)
        else:
            self._lex_arguments(values)

    def _lex_name_and_arguments(self, tokens):
        if tokens:
            tokens[0].type = Token.NAME
        self._lex_arguments(tokens[1:])

    def _lex_name_arguments_and_with_name(self, tokens):
        self._lex_name_and_arguments(tokens)
        if len(tokens) > 1 and \
                normalize_whitespace(tokens[-2].value) in ('WITH NAME', 'AS'):
            tokens[-2].type = Token.WITH_NAME
            tokens[-1].type = Token.NAME

    def _lex_arguments(self, tokens):
        for token in tokens:
            token.type = Token.ARGUMENT


class TestCaseFileSettings(Settings):
    names = (
        'Documentation',
        'Metadata',
        'Suite Setup',
        'Suite Teardown',
        'Test Setup',
        'Test Teardown',
        'Test Template',
        'Test Timeout',
        'Test Tags',
        'Default Tags',
        'Keyword Tags',
        'Library',
        'Resource',
        'Variables'
    )
    aliases = {
        'Force Tags': 'Test Tags',
        'Task Tags': 'Test Tags',
        'Task Setup': 'Test Setup',
        'Task Teardown': 'Test Teardown',
        'Task Template': 'Test Template',
        'Task Timeout': 'Test Timeout',
    }

    def _not_valid_here(self, name):
        return f"Setting '{name}' is not allowed in suite file."


class InitFileSettings(Settings):
    names = (
        'Documentation',
        'Metadata',
        'Suite Setup',
        'Suite Teardown',
        'Test Setup',
        'Test Teardown',
        'Test Timeout',
        'Test Tags',
        'Keyword Tags',
        'Library',
        'Resource',
        'Variables'
    )
    aliases = {
        'Force Tags': 'Test Tags',
        'Task Tags': 'Test Tags',
        'Task Setup': 'Test Setup',
        'Task Teardown': 'Test Teardown',
        'Task Timeout': 'Test Timeout',
    }

    def _not_valid_here(self, name):
        return f"Setting '{name}' is not allowed in suite initialization file."


class ResourceFileSettings(Settings):
    names = (
        'Documentation',
        'Keyword Tags',
        'Library',
        'Resource',
        'Variables'
    )

    def _not_valid_here(self, name):
        return f"Setting '{name}' is not allowed in resource file."


class TestCaseSettings(Settings):
    names = (
        'Documentation',
        'Tags',
        'Setup',
        'Teardown',
        'Template',
        'Timeout'
    )

    def __init__(self, parent, languages):
        super().__init__(languages)
        self.parent = parent

    def _format_name(self, name):
        return name[1:-1].strip()

    @property
    def template_set(self):
        template = self.settings['Template']
        if self._has_disabling_value(template):
            return False
        parent_template = self.parent.settings['Test Template']
        return self._has_value(template) or self._has_value(parent_template)

    def _has_disabling_value(self, setting):
        if setting is None:
            return False
        return setting == [] or setting[0].value.upper() == 'NONE'

    def _has_value(self, setting):
        return setting and setting[0].value

    def _not_valid_here(self, name):
        return f"Setting '{name}' is not allowed with tests or tasks."


class KeywordSettings(Settings):
    names = (
        'Documentation',
        'Arguments',
        'Teardown',
        'Timeout',
        'Tags',
        'Return'
    )

    def _format_name(self, name):
        return name[1:-1].strip()

    def _not_valid_here(self, name):
        return f"Setting '{name}' is not allowed with user keywords."
