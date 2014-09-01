function addHandler(element, eventName, handler) {
    if (element.attachEvent) {
        return element.attachEvent('on' + eventName, handler);
    } else {
        return element.addEventListener(eventName, handler, false);
    }
}

function addHandlerToButtons(className, handler) {
    var buttons = getElementsByClassName(className);
    for (var i = buttons.length - 1; i >= 0; i--) {
        addHandler(buttons[i], 'click', handler);
    }
}

function getElementsByClassName(className) {
    if (document.getElementsByClassName) {
        return document.getElementsByClassName(className);
    } else {  // IE8
        return document.querySelectorAll('.' + className);
    }
}

function getIdAndVersion(evt) {
    var targetElement = (evt.srcElement) ? evt.srcElement : evt.currentTarget;
    var id = targetElement.value;
    return {
        'id' : id,
        'version' : document.getElementById(id).value
    };
}

function getViewUrl(targetId, targetVersion) {
    if (targetId === 'ug') {
        return targetVersion + '/RobotFrameworkUserGuide.html';
    }
    return targetVersion + '/libraries/' + targetId + '.html';
}

function getZipUrl(version) {
    return 'robotframework-userguide-' + version + '.zip'
}

function viewDoc(event) {
    var target = getIdAndVersion(event);
    window.location.href = getViewUrl(target.id, target.version);
}

function downloadDoc(event) {
    var target = getIdAndVersion(event);
    window.location.href = getZipUrl(target.version);
}

function viewTool(event) {
    var target = getIdAndVersion(event);
    var ugUrl = getViewUrl('ug', target.version);
    window.location.href = ugUrl + '#' + target.id;
}

window.onload = function() {
    addHandlerToButtons('download-doc', downloadDoc);
    addHandlerToButtons('view-doc', viewDoc);
    addHandlerToButtons('view-tool', viewTool);
};
