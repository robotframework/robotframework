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


class EN(Language):
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


class FI(Language):
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

class CS(Language):
    setting_headers = {'Nastavení', 'Nastavení', 'Nastavení', 'Nastavení'}
    variable_headers = {'Proměnná', 'Proměnné', 'Proměnné', 'Proměnné'}
    test_case_headers = {'Testovací případ', 'Testovací případy', 'Testovací případy', 'Testovací případy'}
    task_headers = {'Úloha', 'Úlohy', 'Úlohy', 'Úlohy'}
    keyword_headers = {'Klíčové slovo', 'Klíčová slova', 'Klíčová slova', 'Klíčová slova'}
    comment_headers = {'Comment', 'Comments', 'Comments', 'Comments'}
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
    force_tags = 'Vynucené štítky'
    default_tags = 'Výchozí štítky'
    tags = 'Štítky'
    setup = 'Příprava'
    teardown = 'Ukončení'
    template = 'Šablona'
    timeout = 'Časový limit'
    arguments = 'Argumenty'
    return_ = 'Vrací'
    bdd_prefixes = {'Pokud', 'Když', 'Pak', 'A', 'Ale'}

class DE(Language):
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
    force_tags = 'Pflichtmarker'
    default_tags = 'Standard Marker'
    tags = 'Marker'
    setup = 'Vorbereitung'
    teardown = 'Nachbereitung'
    template = 'Vorlage'
    timeout = 'Zeitlimit'
    arguments = 'Argumente'
    return_ = 'Rückgabe'
    bdd_prefixes = {'Angenommen', 'Wenn', 'Dann', 'Und', 'Aber'}

class NL(Language):
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
    force_tags = 'Forceer Labels'
    default_tags = 'Standaard Labels'
    tags = 'Labels'
    setup = 'Preconditie'
    teardown = 'Postconditie'
    template = 'Sjabloon'
    timeout = 'Time-out'
    arguments = 'Parameters'
    return_ = 'Return'
    bdd_prefixes = {'Stel', 'Als', 'Dan', 'En', 'Maar'}

class PL(Language):
    setting_headers = {'Ustawienia', 'Ustawienia', 'Ustawienia', 'Ustawienia'}
    variable_headers = {'Zmienna', 'Zmienne', 'Zmienne', 'Zmienne'}
    test_case_headers = {'Test Case', 'Test Cases', 'Test Cases', 'Test Cases'}
    task_headers = {'Zadanie', 'Zadania', 'Zadania', 'Zadania'}
    keyword_headers = {'Keyword', 'Keywords', 'Keywords', 'Keywords'}
    comment_headers = {'Comment', 'Comments', 'Comments', 'Comments'}
    library = 'Biblioteka'
    resource = 'Zasób'
    variables = 'Zmienna'
    documentation = 'Dokumentacja'
    metadata = 'Metadane'
    suite_setup = 'Suite Setup'
    suite_teardown = 'Suite Teardown'
    test_setup = 'Test Setup'
    test_teardown = 'Test Teardown'
    test_template = 'Test Template'
    test_timeout = 'Limit Czasu Testu'
    force_tags = 'Wymuś Znaczniki'
    default_tags = 'Domyślne Znaczniki'
    tags = 'Znaczniki'
    setup = 'Ustawienia'
    teardown = 'Teardown'
    template = 'Szablon'
    timeout = 'Limit Czasu'
    arguments = 'Argumenty'
    return_ = 'Return'
    bdd_prefixes = {'Given', 'Kiedy', 'Wtedy', 'Oraz', 'Ale'}

class PT(Language):
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
    force_tags = 'Forçar Etiquetas'
    default_tags = 'Etiquetas por Defeito'
    tags = 'Etiquetas'
    setup = 'Inicialização'
    teardown = 'Finalização'
    template = 'Modelo'
    timeout = 'Tempo Limite'
    arguments = 'Argumentos'
    return_ = 'Retornar'
    bdd_prefixes = {'Dado', 'Quando', 'Então', 'E', 'Mas'}

from robot.conf import Language
class PT-br(Language):
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
    force_tags = 'Forçar Etiquetas'
    default_tags = 'Etiquetas Padrão'
    tags = 'Etiquetas'
    setup = 'Inicialização'
    teardown = 'Finalização'
    template = 'Modelo'
    timeout = 'Tempo Limite'
    arguments = 'Argumentos'
    return_ = 'Retornar'
    bdd_prefixes = {'Dado', 'Quando', 'Então', 'E', 'Mas'}

class TR(Language):
    setting_headers = {'Setting', 'Ayarlar'}
    variable_headers = {'Variable', 'Değişkenler'}
    test_case_headers = {'Test Case', 'Test Cases'}
    task_headers = {'Task', 'Görevler'}
    keyword_headers = {'Keyword', 'Keywords'}
    comment_headers = {'Comment', 'Comments'}
    library = 'Kütüphane'
    resource = 'Kaynak'
    variables = 'Değişken'
    documentation = 'Dokümentasyon'
    metadata = 'Metadata'
    suite_setup = 'Suite Setup'
    suite_teardown = 'Suite Teardown'
    test_setup = 'Test Setup'
    test_teardown = 'Test Teardown'
    test_template = 'Test Şablonu'
    test_timeout = 'Test Zaman Aşımı'
    force_tags = 'Force Tags'
    default_tags = 'Default Tags'
    tags = 'Etiketler'
    setup = 'Kurulum'
    teardown = 'Teardown'
    template = 'Şablon'
    timeout = 'Zaman Aşımı'
    arguments = 'Argümanlar'
    return_ = 'Return'
    bdd_prefixes = {'Diyelim ki', 'Eğer ki', 'O zaman', 'Ve', 'Ancak'}

class UK(Language):
    setting_headers = {'Setting', 'Settings', 'Settings', 'Settings'}
    variable_headers = {'Змінна', 'Змінні', 'Змінних', 'Змінних'}
    test_case_headers = {'Тест-кейс', 'Тест-кейси', 'Тест-кейсів', 'Тест-кейси'}
    task_headers = {'Завдання', 'Завадання', 'Завдань', 'Завдань'}
    keyword_headers = {'Ключове слово', 'Ключових слова', 'Ключових слів', 'Ключових слова'}
    comment_headers = {'Comment', 'Comments', 'Comments', 'Comments'}
    library = 'Бібліотека'
    resource = 'Resource'
    variables = 'Variable'
    documentation = 'Документація'
    metadata = 'Метадані'
    suite_setup = 'Suite Setup'
    suite_teardown = 'Suite Teardown'
    test_setup = 'Test Setup'
    test_teardown = 'Test Teardown'
    test_template = 'Test Template'
    test_timeout = 'Test Timeout'
    force_tags = 'Force Tags'
    default_tags = 'Default Tags'
    tags = 'Tags'
    setup = 'Setup'
    teardown = 'Teardown'
    template = 'Template'
    timeout = 'Timeout'
    arguments = 'Arguments'
    return_ = 'Return'
    bdd_prefixes = {'Given', 'When', 'Then', 'And', 'But'}

class ZH-CN(Language):
    setting_headers = {'设置'}
    variable_headers = {'变量'}
    test_case_headers = {'用例'}
    task_headers = {'任务'}
    keyword_headers = {'关键字'}
    comment_headers = {'备注'}
    library = '程序库'
    resource = '资源文件'
    variables = '变量文件'
    documentation = '说明'
    metadata = '元数据'
    suite_setup = '用例集启程'
    suite_teardown = '用例集终程'
    test_setup = '测试启程'
    test_teardown = '测试终程'
    test_template = '测试模板'
    test_timeout = '测试超时'
    force_tags = '强制标签'
    default_tags = '默认标签'
    tags = '标签'
    setup = '启程'
    teardown = '终程'
    template = '模板'
    timeout = '超时'
    arguments = '入参'
    return_ = '回参'
    bdd_prefixes = {'假定', '当', '那么', '并且', '但是'}
