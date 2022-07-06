from robot.conf import Language


class Cs(Language):
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


class Nl(Language):
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


class Fr(Language):
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
    force_tags = 'Étiquette forcée'
    default_tags = 'Étiquette par défaut'
    tags = 'Étiquette'
    setup = 'Mise en place'
    teardown = 'Démontage'
    template = 'Modèle'
    timeout = 'Délai d'attente'
    arguments = 'Arguments'
    return_ = 'Retour'
    bdd_prefixes = {'Étant donné', 'Lorsque', 'Alors', 'Et', 'Mais'}


class Pt(Language):
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
