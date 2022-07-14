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


class Cs(Language):
    """Czech"""
    setting_headers = {'Nastavení', 'Nastavení', 'Nastavení', 'Nastavení'}
    variable_headers = {'Proměnná', 'Proměnné', 'Proměnné', 'Proměnné'}
    test_case_headers = {'Testovací případ', 'Testovací případy', 'Testovací případy', 'Testovací případy'}
    task_headers = {'Úloha', 'Úlohy', 'Úlohy', 'Úlohy'}
    keyword_headers = {'Klíčové slovo', 'Klíčová slova', 'Klíčová slova', 'Klíčová slova'}
    comment_headers = {'Komentář', 'Komentáře', 'Komentáře', 'Komentáře'}
    library = 'Knihovna'
    resource = 'Zdroj'
    variables = 'Proměnná'
    documentation = 'Dokumentace'
    metadata = 'Metadata'
    suite_setup = 'Příprava sady'
    suite_teardown = 'Ukončení sady'
    test_setup = 'Příprava testu'
    test_teardown = 'Ukončení testu'
    test_template = 'Šablona testu'
    test_timeout = 'Časový limit testu'
    test_tags = 'Štítky testů'
    task_setup = 'Příprava úlohy'
    task_teardown = 'Ukončení úlohy'
    task_template = 'Šablona úlohy'
    task_timeout = 'Časový limit úlohy'
    task_tags = 'Štítky úloh'
    keyword_tags = 'Štítky klíčových slov'
    tags = 'Štítky'
    setup = 'Příprava'
    teardown = 'Ukončení'
    template = 'Šablona'
    timeout = 'Časový limit'
    arguments = 'Argumenty'
    bdd_prefixes = {'Pokud', 'Když', 'Pak', 'A', 'Ale'}


class Nl(Language):
    """Dutch"""
    setting_headers = {'Instelling', 'Instellingen'}
    variable_headers = {'Variabele', 'Variabelen'}
    test_case_headers = {'Testgeval', 'Testgevallen'}
    task_headers = {'Taak', 'Taken'}
    keyword_headers = {'Sleutelwoord', 'Sleutelwoorden'}
    comment_headers = {'Opmerking', 'Opmerkingen'}
    library = 'Bibliotheek'
    resource = 'Resource'
    variables = 'Variabele'
    documentation = 'Documentatie'
    metadata = 'Metadata'
    suite_setup = 'Suite Preconditie'
    suite_teardown = 'Suite Postconditie'
    test_setup = 'Test Preconditie'
    test_teardown = 'Test Postconditie'
    test_template = 'Test Sjabloon'
    test_timeout = 'Test Time-out'
    test_tags = 'Test Labels'
    task_setup = 'Taak Preconditie'
    task_teardown = 'Taak Postconditie'
    task_template = 'Taak Sjabloon'
    task_timeout = 'Taak Time-out'
    task_tags = 'Taak Labels'
    keyword_tags = 'Sleutelwoord Labels'
    tags = 'Labels'
    setup = 'Preconditie'
    teardown = 'Postconditie'
    template = 'Sjabloon'
    timeout = 'Time-out'
    arguments = 'Parameters'
    bdd_prefixes = {'Stel', 'Als', 'Dan', 'En', 'Maar'}


class Fi(Language):
    """Finnish"""
    setting_headers = {'Asetus', 'Asetukset'}
    variable_headers = {'Muuttuja', 'Muuttujat'}
    test_case_headers = {'Testi', 'Testit'}
    task_headers = {'Tehtävä', 'Tehtävät'}
    keyword_headers = {'Avainsana', 'Avainsanat'}
    comment_headers = {'Kommentti', 'Kommentit'}
    library = 'Kirjasto'
    resource = 'Resurssi'
    variables = 'Muuttujat'
    documentation = 'Dokumentaatio'
    metadata = 'Metatiedot'
    suite_setup = 'Setin Alustus'
    suite_teardown = 'Setin Alasajo'
    test_setup = 'Testin Alustus'
    task_setup = 'Tehtävän Alustus'
    test_teardown = 'Testin Alasajo'
    task_teardown = 'Tehtävän Alasajo'
    test_template = 'Testin Malli'
    task_template = 'Tehtävän Malli'
    test_timeout = 'Testin Aikaraja'
    task_timeout = 'Tehtävän Aikaraja'
    test_tags = 'Testin Tagit'
    task_tags = 'Tehtävän Tagit'
    keyword_tags = 'Avainsanan Tagit'
    tags = 'Tagit'
    setup = 'Alustus'
    teardown = 'Alasajo'
    template = 'Malli'
    timeout = 'Aikaraja'
    arguments = 'Argumentit'
    bdd_prefixes = {'Oletetaan', 'Kun', 'Niin', 'Ja', 'Mutta'}


class Fr(Language):
    """French"""
    setting_headers = {'Paramètre', 'Paramètres'}
    variable_headers = {'Variable', 'Variables'}
    test_case_headers = {'Unité de test', 'Unités de test'}
    task_headers = {'Tâche', 'Tâches'}
    keyword_headers = {'Mot-clé', 'Mots-clés'}
    comment_headers = {'Commentaire', 'Commentaires'}
    library = 'Bibliothèque'
    resource = 'Ressource'
    variables = 'Variable'
    documentation = 'Documentation'
    metadata = 'Méta-donnée'
    suite_setup = 'Mise en place de suite'
    suite_teardown = 'Démontage de suite'
    test_setup = 'Mise en place de test'
    test_teardown = 'Démontage de test'
    test_template = 'Modèle de test'
    test_timeout = 'Délai de test'
    test_tags = 'Étiquette de test'
    task_setup = 'Mise en place de tâche'
    task_teardown = 'Démontage de test'
    task_template = 'Modèle de tâche'
    task_timeout = 'Délai de tâche'
    task_tags = 'Étiquette de tâche'
    keyword_tags = 'Etiquette de mot-clé'
    tags = 'Étiquette'
    setup = 'Mise en place'
    teardown = 'Démontage'
    template = 'Modèle'
    timeout = "Délai d'attente"
    arguments = 'Arguments'
    bdd_prefixes = {'Étant donné', 'Lorsque', 'Alors', 'Et', 'Mais'}


class De(Language):
    """German"""
    setting_headers = {'Einstellung', 'Einstellungen'}
    variable_headers = {'Variable', 'Variablen'}
    test_case_headers = {'Testfall', 'Testfälle'}
    task_headers = {'Aufgabe', 'Aufgaben'}
    keyword_headers = {'Schlüsselwort', 'Schlüsselwörter'}
    comment_headers = {'Kommentar', 'Kommentare'}
    library = 'Bibliothek'
    resource = 'Ressource'
    variables = 'Variable'
    documentation = 'Dokumentation'
    metadata = 'Metadaten'
    suite_setup = 'Suitevorbereitung'
    suite_teardown = 'Suitenachbereitung'
    test_setup = 'Testvorbereitung'
    test_teardown = 'Testnachbereitung'
    test_template = 'Testvorlage'
    test_timeout = 'Testzeitlimit'
    test_tags = 'Test Marker'
    task_setup = 'Aufgabenvorbereitung'
    task_teardown = 'Aufgabennachbereitung'
    task_template = 'Aufgabenvorlage'
    task_timeout = 'Aufgabenzeitlimit'
    task_tags = 'Aufgaben Marker'
    keyword_tags = 'Schlüsselwort Marker'
    tags = 'Marker'
    setup = 'Vorbereitung'
    teardown = 'Nachbereitung'
    template = 'Vorlage'
    timeout = 'Zeitlimit'
    arguments = 'Argumente'
    bdd_prefixes = {'Angenommen', 'Wenn', 'Dann', 'Und', 'Aber'}


class PtBr(Language):
    """Portuguese, Brazilian"""
    setting_headers = {'Configuração', 'Configurações'}
    variable_headers = {'Variável', 'Variáveis'}
    test_case_headers = {'Caso de Teste', 'Casos de Teste'}
    task_headers = {'Tarefa', 'Tarefas'}
    keyword_headers = {'Palavra-Chave', 'Palavras-Chave'}
    comment_headers = {'Comentário', 'Comentários'}
    library = 'Biblioteca'
    resource = 'Recurso'
    variables = 'Variável'
    documentation = 'Documentação'
    metadata = 'Metadados'
    suite_setup = 'Configuração da Suíte'
    suite_teardown = 'Finalização de Suíte'
    test_setup = 'Inicialização de Teste'
    test_teardown = 'Finalização de Teste'
    test_template = 'Modelo de Teste'
    test_timeout = 'Tempo Limite de Teste'
    test_tags = 'Test Tags'
    task_setup = 'Inicialização de Tarefa'
    task_teardown = 'Finalização de Tarefa'
    task_template = 'Modelo de Tarefa'
    task_timeout = 'Tempo Limite de Tarefa'
    task_tags = 'Task Tags'
    keyword_tags = 'Keyword Tags'
    tags = 'Etiquetas'
    setup = 'Inicialização'
    teardown = 'Finalização'
    template = 'Modelo'
    timeout = 'Tempo Limite'
    arguments = 'Argumentos'
    bdd_prefixes = {'Dado', 'Quando', 'Então', 'E', 'Mas'}


class Pt(Language):
    """Portuguese"""
    setting_headers = {'Definição', 'Definições'}
    variable_headers = {'Variável', 'Variáveis'}
    test_case_headers = {'Caso de Teste', 'Casos de Teste'}
    task_headers = {'Tarefa', 'Tarefas'}
    keyword_headers = {'Palavra-Chave', 'Palavras-Chave'}
    comment_headers = {'Comentário', 'Comentários'}
    library = 'Biblioteca'
    resource = 'Recurso'
    variables = 'Variável'
    documentation = 'Documentação'
    metadata = 'Metadados'
    suite_setup = 'Inicialização de Suíte'
    suite_teardown = 'Finalização de Suíte'
    test_setup = 'Inicialização de Teste'
    test_teardown = 'Finalização de Teste'
    test_template = 'Modelo de Teste'
    test_timeout = 'Tempo Limite de Teste'
    test_tags = 'Etiquetas de Testes'
    task_setup = 'Inicialização de Tarefa'
    task_teardown = 'Finalização de Tarefa'
    task_template = 'Modelo de Tarefa'
    task_timeout = 'Tempo Limite de Tarefa'
    task_tags = 'Etiquetas de Tarefas'
    keyword_tags = 'Etiquetas de Palavras-Chave'
    tags = 'Etiquetas'
    setup = 'Inicialização'
    teardown = 'Finalização'
    template = 'Modelo'
    timeout = 'Tempo Limite'
    arguments = 'Argumentos'
    bdd_prefixes = {'Dado', 'Quando', 'Então', 'E', 'Mas'}
