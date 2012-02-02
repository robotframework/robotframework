function toggleSuite(suiteId) {
    toggleElement(suiteId, ['keyword', 'suite', 'test']);
}

function toggleTest(testId) {
    toggleElement(testId, ['keyword']);
}

function toggleKeyword(kwId) {
    toggleElement(kwId, ['keyword', 'message']);
}

function addElements(elems, templateName, target){
    for (var i in elems) {
        $.tmpl(templateName, elems[i]).appendTo(target);
    }
}

function toggleElement(elementId, childrenNames) {
    var childElement = $("#"+elementId+"_children");
    childElement.toggle(100, function () {
        var foldingButton = $('#'+elementId+'_foldingbutton');
        foldingButton.text(foldingButton.text() == '+' ? '-' : '+');
    });
    populateChildren(elementId, childElement, childrenNames);
}

function populateChildren(elementId, childElement, childrenNames) {
    if (!childElement.hasClass("populated")) {
        var element = window.testdata.find(elementId);
        element.callWhenChildrenReady(drawCallback(element, childElement, childrenNames));
        childElement.addClass("populated");
    }
}

function drawCallback(element, childElement, childrenNames) {
    return function () {
        $.map(childrenNames, function (childName) {
            addElements(element[childName + 's'](), childName + 'Template', childElement);
        });
    }
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
    var childElement = $("#" + element.id + "_children");
    childElement.show();
    populateChildren(element.id, childElement, element.childrenNames);
    $('#'+element.id+'_foldingbutton').text('-');
}

function expandElementWithId(elementid) {
    expandElement(window.testdata.find(elementid));
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
