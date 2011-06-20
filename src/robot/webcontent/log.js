function openSuite(suiteId) {
    openElement(suiteId, ['keyword', 'suite', 'test']);
}

function openTest(testId) {
    openElement(testId, ['keyword']);
}

function openKeyword(kwId) {
    openElement(kwId, ['keyword', 'message']);
}

function addElements(elems, templateName, target){
    for (var i = 0; elems(i); i++) {
        $.tmpl(templateName, elems(i)).appendTo(target);
    }
}

function openElement(elementId, childrenNames){
    var childElement = $("#"+elementId+"_children");
    childElement.show();
    if (!childElement.hasClass("populated")) {
        var element = window.testdata.find(elementId);
        $.map(childrenNames, function (childName) {
            addElements(element[childName], childName + 'Template', childElement);
        });
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
