
function openSuite(suiteId) {
    function populator(suite, childrenElement){
        populateMetadata(suite, childrenElement);
        addElements(suite.keyword, window.templates.keyword, childrenElement);
        addElements(suite.suite, window.templates.suite, childrenElement);
        addElements(suite.test, window.templates.test, childrenElement);
    }
    openElement(suiteId, populator);
}

function populateMetadata(element, childrenElement) {
    var metadata = $.tmpl(window.templates.metadata, element);
    metadata.appendTo(childrenElement);
    meta = $('#'+element.id+'_metadata');
    addMetadata(meta, 'Full Name', element.fullname, window.templates.metadataElement);
    addMetadata(meta, 'Documentation', element.documentation, window.templates.documentationElement);
    addMetadata(meta, 'Timeout', element.timeout, window.templates.metadataElement);
    if (element.tags)
        addMetadata(meta, 'Tags', element.tags.join(', '), window.templates.metadataElement);
    for(var key in element.metadata){
        addMetadata(meta, key, element.metadata[key], window.templates.metadataElement);
    }
    addMetadata(meta, 'Source', element.source, window.templates.sourceElement);
    addMetadata(meta, 'Start / End',
                [element.times.startTime(), element.times.endTime()].join('  /  '),
                window.templates.metadataElement);
    addMetadata(meta, 'Elapsed',
            element.times.elapsedTime(),
            window.templates.metadataElement);
    if (element.statusText) {
        var status = $.tmpl(window.templates.statusElement, element);
        status.appendTo(meta);
    }
    addMessage(meta, element);
}

function addMessage(parent, element){
    var failureMessage = element.getFailureMessage();
    if(element.total == undefined){
        addMetadata(meta, 'Message', failureMessage, window.templates.metadataElement);
        return;
    }
    var template = (failureMessage !== undefined ? window.templates.failureAndStatsMessageElement : window.templates.statsMessageElement);
    var elem = $.tmpl(template, element);
    elem.appendTo(parent);
}

function addMetadata(parent, key, value, template) {
    if (value === undefined || value === "") return;
    var data = {key:key, value:value};
    var metadataElement = $.tmpl(template, data);
    metadataElement.appendTo(parent);
}

function addElements(elems, template, target){
    for(var i = 0;elems(i); i++){
        $.tmpl(template, elems(i)).appendTo(target);
    }
}

function openElement(elementId, populator){
    var childrenElement = $("#"+elementId+"_children");
    childrenElement.show();
    $('#'+elementId+'_foldlink').show();
    $('#'+elementId+'_unfoldlink').hide();
    if(childrenElement.hasClass("populated"))
        return;
    childrenElement.addClass("populated");
    element = window.testdata.find(elementId);
    populator(element, childrenElement);
}

function closeElement(elementId) {
    var childrenElement = $("#"+elementId+"_children")
    childrenElement.hide();
    $('#'+elementId+'_foldlink').hide();
    $('#'+elementId+'_unfoldlink').show();
}

function openTest(testId) {
    function populator(test, childrenElement){
        populateMetadata(test, childrenElement);
        addElements(test.keyword, window.templates.keyword, childrenElement);
    }
    openElement(testId, populator);
}

function openKeyword(kwId) {
    function populator(keyword, childrenElement){
        populateMetadata(keyword, childrenElement);
        addElements(keyword.keyword, window.templates.keyword, childrenElement);
        addElements(keyword.message, window.templates.message, childrenElement);
    }
    openElement(kwId, populator);
}

function iterateTasks(){
    if (window.tasks.length == 0)
        return;
    var element = window.tasks.pop();
    var unfoldLink = $("#"+element.id+"_unfoldlink");
    if(element == undefined || elementHiddenByUser(element.id)){
        window.tasks = []
        return;
    }
    $("#"+element.id+"_unfoldlink").click();
    var children = element.children()
    for(var i = children.length-1; i >= 0; i--){
        if(window.tasksMatcher(children[i]))
            window.tasks.push(children[i]);
    }
    if(window.tasks.length > 0)
        setTimeout("iterateTasks()", 0);
}

function elementHiddenByUser(elementId) {
    var domElement = $("#"+elementId);
    return !domElement.is(":visible");
}

function expandAllChildren(elementId) {
    window.tasks = [window.testdata.find(elementId)];
    window.tasksMatcher = function() {return true;}
    iterateTasks();
}

function expandFailed(element) {
    if(element.status == "fail"){
        window.tasks = [element];
        window.tasksMatcher = function(e) {return e.status == "fail"};
        iterateTasks();
    }
}