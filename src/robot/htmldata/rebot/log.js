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

function toggleElement(elementId, childrenNames) {
    var element = $('#' + elementId);
    var children = element.children('.children');
    children.toggle(100, '', function () {
        element.children('.element-header').toggleClass('closed');
    });
    populateChildren(elementId, children, childrenNames);
}

function populateChildren(elementId, childElement, childrenNames) {
    if (!childElement.hasClass('populated')) {
        var element = window.testdata.findLoaded(elementId);
        var callback = drawCallback(element, childElement, childrenNames);
        element.callWhenChildrenReady(callback);
        childElement.addClass('populated');
    }
}

function drawCallback(element, childElement, childrenNames) {
    return function () {
        util.map(childrenNames, function (childName) {
            var children = element[childName + 's']();
            var template = childName + 'Template';
            util.map(children, function (child) {
                $.tmpl(template, child).appendTo(childElement);
            });
        });
    }
}

function expandSuite(suite) {
    if (suite.status == "PASS")
        expandElement(suite);
    else
        expandCriticalFailed(suite);
}

function expandElement(item, retryCount) {
    retryCount = typeof retryCount !== 'undefined' ? retryCount : 3;
    var element = $('#' + item.id);
    var children = element.children('.children');
    // .css is faster than .show and .show w/ callback is terribly slow
    children.css({'display': 'block'});
    // in rare cases on large logs concurrent expanding fails => retry
    if (children.css('display') != 'block' && retryCount > 0) {
        console.debug('expandElement '+item.id+' failed! planning retry...');
        setTimeout(function() { expandElement(item, retryCount-1); }, 0);
        return;
    }
    populateChildren(item.id, children, item.childrenNames);
    element.children('.element-header').removeClass('closed');
}

function expandElementWithId(elementid) {
    expandElement(window.testdata.findLoaded(elementid));
}

function expandElementsWithIds(ids) {
    util.map(ids, expandElementWithId);
}

function loadAndExpandElementIds(ids) {
    for (var i in ids) {
        window.testdata.ensureLoaded(ids[i], expandElementsWithIds);
    }
}

function expandCriticalFailed(element) {
    if (element.status == "FAIL") {
        window.elementsToExpand = [element];
        window.expandDecider = function (e) {
            return e.status == "FAIL" && (e.isCritical === undefined || e.isCritical);
        };
        expandRecursively();
    }
}

function expandAll(elementId) {
    window.elementsToExpand = [window.testdata.findLoaded(elementId)];
    window.expandDecider = function () { return true; };
    expandRecursively();
}

function expandRecursively() {
    if (!window.elementsToExpand.length)
        return;
    var element = window.elementsToExpand.pop();
    if (!element || elementHiddenByUser(element.id)) {
        window.elementsToExpand = [];
        return;
    }
    expandElement(element);
    element.callWhenChildrenReady(function () {
        var children = element.children();
        for (var i = children.length-1; i >= 0; i--) {
            if (window.expandDecider(children[i]))
                window.elementsToExpand.push(children[i]);
        }
        if (window.elementsToExpand.length)
            setTimeout(expandRecursively, 0);
    });
}

function elementHiddenByUser(id) {
    var element = $('#' + id);
    return !element.is(":visible");
}

function collapseAll(id) {
    var element = $('#' + id);
    element.find('.children').css({'display': 'none'});
    element.find('.element-header').addClass('closed');
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
    anchors = util.map(anchors, closestVisibleParent);
    var shortest = anchors[0];
    for (var i = 1; i < anchors.length; i++)
        if (shortest.height() > anchors[i].height())
            shortest = anchors[i];
    shortest.get()[0].scrollIntoView(true);
}

function setMessageVisibility(level) {
    level = parseInt(level);
    changeClassDisplay(".trace-message", level <= LEVELS.TRACE);
    changeClassDisplay(".debug-message", level <= LEVELS.DEBUG);
    changeClassDisplay(".info-message", level <= LEVELS.INFO);
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

function selectMessage(parentId) {
    var element = $('#' + parentId).find('.message').get(0);
    selectText(element);
}

function selectText(element) {
    // Based on http://stackoverflow.com/questions/985272
    var range, selection;
    if (document.body.createTextRange) {  // IE 8
        range = document.body.createTextRange();
        range.moveToElementText(element);
        range.select();
    } else if (window.getSelection) {  // Others
        selection = window.getSelection();
        range = document.createRange();
        range.selectNodeContents(element);
        selection.removeAllRanges();
        selection.addRange(range);
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
