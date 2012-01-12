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
    for (var i in elems) {
        $.tmpl(templateName, elems[i]).appendTo(target);
    }
}

function openElement(elementId, childrenNames) {
    $('#'+elementId+'_unfoldlink').css("background", "yellow");
    var childElement = $("#"+elementId+"_children");
    childElement.show();
    if (!childElement.hasClass("populated")) {
        var element = window.testdata.find(elementId);
        element.callWhenChildrenReady(drawCallback(element, childElement, childrenNames));
        childElement.addClass("populated");
    }
    $('#'+elementId+'_foldlink').show();
    $('#'+elementId+'_unfoldlink').hide();
    $('#'+elementId+'_unfoldlink').css("background", "white");
}

function drawCallback(element, childElement, childrenNames) {
    return function () {
        $.map(childrenNames, function (childName) {
            addElements(element[childName + 's'](), childName + 'Template', childElement);
        });
    }
}

function closeElement(elementId) {
    $("#"+elementId+"_children").hide();
    $('#'+elementId+'_foldlink').hide();
    $('#'+elementId+'_unfoldlink').show();
}

function expandRecursively(){
    if (!window.elementsToExpand.length)
        return;
    var element = window.elementsToExpand.pop();
    if (element == undefined || elementHiddenByUser(element.id)) {
        window.elementsToExpand = [];
        return;
    }
    expandElement(element);
    element.callWhenChildrenReady( function () {
        var children = element.children();
        for (var i = children.length-1; i >= 0; i--) {
            if (window.expandDecider(children[i]))
                window.elementsToExpand.push(children[i]);
        }
        if (window.elementsToExpand.length)
            setTimeout(expandRecursively, 0);
    });
}

function expandElement(element) {
    $("#" + element.id + "_unfoldlink").click();
}

function elementHiddenByUser(elementId) {
    var domElement = $("#"+elementId);
    return !domElement.is(":visible");
}

function expandAllChildren(elementId) {
    window.elementsToExpand = [window.testdata.find(elementId)];
    window.expandDecider = function() {return true;};
    expandRecursively();
}

function expandCriticalFailed(element) {
    if (element.status == "FAIL") {
        window.elementsToExpand = [element];
        window.expandDecider = function(e) {return e.status == "FAIL" && (e.isCritical === undefined || e.isCritical);};
        expandRecursively();
    }
}

function expandSuite(suite) {
    if (suite.status == "PASS")
        expandElement(suite);
    else
        expandCriticalFailed(suite);
}
