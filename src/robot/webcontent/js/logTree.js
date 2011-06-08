function openSuite(suiteId) {
    function populator(suite, childElement){
        addElements(suite.keyword, window.templates.keyword, childElement);
        addElements(suite.suite, window.templates.suite, childElement);
        addElements(suite.test, window.templates.test, childElement);
    }
    openElement(suiteId, populator);
}

function openTest(testId) {
    function populator(test, childElement){
        addElements(test.keyword, window.templates.keyword, childElement);
    }
    openElement(testId, populator);
}

function openKeyword(kwId) {
    function populator(keyword, childElement){
        addElements(keyword.keyword, window.templates.keyword, childElement);
        addElements(keyword.message, window.templates.message, childElement);
    }
    openElement(kwId, populator);
}

function addElements(elems, template, target){
    for (var i = 0; elems(i); i++) {
        $.tmpl(template, elems(i)).appendTo(target);
    }
}

function openElement(elementId, populator){
    var childElement = $("#"+elementId+"_children");
    childElement.show();
    if (!childElement.hasClass("populated")) {
        element = window.testdata.find(elementId);
        populator(element, childElement);
        childElement.addClass("populated");
    }
    $('#'+elementId+'_foldlink').show();
    $('#'+elementId+'_unfoldlink').hide();
}

function closeElement(elementId) {
    $("#"+elementId+"_children").hide();
    $('#'+elementId+'_foldlink').hide();
    $('#'+elementId+'_unfoldlink').show();
}

function iterateTasks(){
    if (!window.tasks.length)
        return;
    var element = window.tasks.pop();
    if (element == undefined || elementHiddenByUser(element.id)) {
        window.tasks = []
        return;
    }
    $("#"+element.id+"_unfoldlink").click();
    var children = element.children()
    for (var i = children.length-1; i >= 0; i--) {
        if (window.tasksMatcher(children[i]))
            window.tasks.push(children[i]);
    }
    if (window.tasks.length)
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
    if (element.status == "fail") {
        window.tasks = [element];
        window.tasksMatcher = function(e) {return e.status == "fail"};
        iterateTasks();
    }
}
