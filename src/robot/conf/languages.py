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
#  limitations under the License.from robot.conf import Language


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
    keyword_tags = 'Sleutelwoord Labels'
    tags = 'Labels'
    setup = 'Preconditie'
    teardown = 'Postconditie'
    template = 'Sjabloon'
    timeout = 'Time-out'
    arguments = 'Parameters'
    bdd_prefixes = {'Stel', 'Als', 'Dan', 'En', 'Maar'}


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
    keyword_tags = 'Etiquette de mot-clé'
    tags = 'Étiquette'
    setup = 'Mise en place'
    teardown = 'Démontage'
    template = 'Modèle'
    timeout = 'Délai d'attente'
    arguments = 'Arguments'
    bdd_prefixes = {'Étant donné', 'Lorsque', 'Alors', 'Et', 'Mais'}


class Pt-Br(Language):
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
    test_tags = 'Etiquetas de Teste'
    keyword_tags = 'Etiquetas de Palavra-Chave'
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
    keyword_tags = 'Etiquetas de Palavra-Chave'
    tags = 'Etiquetas'
    setup = 'Inicialização'
    teardown = 'Finalização'
    template = 'Modelo'
    timeout = 'Tempo Limite'
    arguments = 'Argumentos'
    bdd_prefixes = {'Dado', 'Quando', 'Então', 'E', 'Mas'}
