var LEVELS = {TRACE: 0, DEBUG: 1, INFO: 2, WARN: 3, FAIL: 4, NONE: 5};

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
        var callback = drawCallback(element, childElement, childrenNames);
        element.callWhenChildrenReady(callback);
        childElement.addClass("populated");
    }
}

function drawCallback(element, childElement, childrenNames) {
    return function () {
        $.map(childrenNames, function (childName) {
            addElements(element[childName + 's'](),
                        childName + 'Template',
                        childElement);
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
    var element = $("#"+elementId);
    return !element.is(":visible");
}

function expandAllChildren(elementId) {
    window.elementsToExpand = [window.testdata.find(elementId)];
    window.expandDecider = function() { return true; };
    expandRecursively();
}

function expandCriticalFailed(element) {
    if (element.status == "FAIL") {
        window.elementsToExpand = [element];
        window.expandDecider = function(e) {
            return e.status == "FAIL" && (e.isCritical === undefined || e.isCritical);
        };
        expandRecursively();
    }
}

function expandSuite(suite) {
    if (suite.status == "PASS")
        expandElement(suite);
    else
        expandCriticalFailed(suite);
}

function logLevelSelected(level) {
    var anchors = getViewAnchorElements();
    setMessageVisibility(level);
    scrollToShortestVisibleAnchorElement(anchors);
}

function getViewAnchorElements() {
    var elem1 = $(document.elementFromPoint(100, 0));
    var elem2 = $(document.elementFromPoint(100, 20));
    return [elem1, elem2];
}

function scrollToShortestVisibleAnchorElement(anchors) {
    anchors = $.map(anchors, closestVisibleParent);
    var shortest = anchors[0];
    for (var i = 1; i < anchors.length; i++)
        if (shortest.height() > anchors[i].height())
            shortest = anchors[i];
    shortest.get()[0].scrollIntoView(true);
}

function setMessageVisibility(level) {
    level = parseInt(level);
    changeClassDisplay(".trace_message", level <= LEVELS.TRACE);
    changeClassDisplay(".debug_message", level <= LEVELS.DEBUG);
    changeClassDisplay(".info_message", level <= LEVELS.INFO);
}

function closestVisibleParent(elem) {
    while (!elem.is(":visible"))
        elem = elem.parent();
    return elem;
}

function changeClassDisplay(clazz, visible) {
    var styles = document.styleSheets;
    for (var i = 0; i < styles.length; i++) {
        var rules = getRules(styles[i]);
        if (rules === null)
            continue;
        for (var j = 0; j < rules.length; j++)
            if (rules[j].selectorText === clazz)
                rules[j].style.display = visible ? "table" : "none";
    }
}

function getRules(style) {
    // With Chrome external CSS files seem to have only null roles and with
    // Firefox accessing rules can result to security error.
    // Neither of these are a problem on with generated logs.
    try {
        return style.cssRules || style.rules;
    } catch (e) {
        return null;
    }
}

function LogLevelController(minLevel, defaultLevel) {
    minLevel = LEVELS[minLevel];
    defaultLevel = LEVELS[defaultLevel];

    function showLogLevelSelector() {
        return minLevel < LEVELS.INFO;
    }

    function defaultLogLevel() {
        if (minLevel > defaultLevel)
            return minLevel;
        return defaultLevel;
    }

    function showTrace() {
        return minLevel == LEVELS.TRACE;
    }

    return {
        showLogLevelSelector: showLogLevelSelector,
        defaultLogLevel: defaultLogLevel,
        showTrace: showTrace
    };
}
