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

    def __init__(self):
        self.settings = {n: None for n in self.names}

    def lex(self, statement):
        setting = statement[0]
        name = self._format_name(setting.value)
        normalized = self._normalize_name(name)
        try:
            self._validate(name, normalized, statement)
        except ValueError as err:
            self._lex_error(setting, statement[1:], err.args[0])
        else:
            self._lex_setting(setting, statement[1:], normalized)

    def _format_name(self, name):
        return name

    def _normalize_name(self, name):
        name = normalize_whitespace(name).title()
        if name in self.aliases:
            return self.aliases[name]
        return name

    def _validate(self, name, normalized, statement):
        if normalized not in self.settings:
            message = self._get_non_existing_setting_message(name, normalized)
            raise ValueError(message)
        if self.settings[normalized] is not None and normalized not in self.multi_use:
            raise ValueError("Setting '%s' is allowed only once. "
                             "Only the first value is used." % name)
        if normalized in self.single_value and len(statement) > 2:
            raise ValueError("Setting '%s' accepts only one value, got %s."
                             % (name, len(statement) - 1))

    def _get_non_existing_setting_message(self, name, normalized):
        if normalized in TestCaseFileSettings.names:
            is_resource = isinstance(self, ResourceFileSettings)
            return "Setting '%s' is not allowed in %s file." % (
                name, 'resource' if is_resource else 'suite initialization'
            )
        return RecommendationFinder(normalize).find_and_format(
            name=normalized,
            candidates=tuple(self.settings) + tuple(self.aliases),
            message="Non-existing setting '%s'." % name
        )

    def _lex_error(self, setting, values, error):
        setting.set_error(error)
        for token in values:
            token.type = Token.COMMENT

    def _lex_setting(self, setting, values, name):
        self.settings[name] = values
        setting.type = name.upper()
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
                normalize_whitespace(tokens[-2].value) == 'WITH NAME':
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
        'Force Tags',
        'Default Tags',
        'Library',
        'Resource',
        'Variables'
    )
    aliases = {
        'Task Setup': 'Test Setup',
        'Task Teardown': 'Test Teardown',
        'Task Template': 'Test Template',
        'Task Timeout': 'Test Timeout',
    }


class InitFileSettings(Settings):
    names = (
        'Documentation',
        'Metadata',
        'Suite Setup',
        'Suite Teardown',
        'Test Setup',
        'Test Teardown',
        'Test Timeout',
        'Force Tags',
        'Library',
        'Resource',
        'Variables'
    )


class ResourceFileSettings(Settings):
    names = (
        'Documentation',
        'Library',
        'Resource',
        'Variables'
    )


class TestCaseSettings(Settings):
    names = (
        'Documentation',
        'Tags',
        'Setup',
        'Teardown',
        'Template',
        'Timeout'
    )

    def __init__(self, parent):
        Settings.__init__(self)
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
