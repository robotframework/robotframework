function addEvent(element, event_, func) {
    if (element.attachEvent){
        return element.attachEvent('on' + event_, func);
    } else {
        return element.addEventListener(event_, func, false);
    }
}

function getIdAndVersion(evt) {
    var id = evt.srcElement.value;
    return {
        'id' : id,
        'version' : document.getElementById(id).value
    };
}

function getGoPath(targetId, targetVersion) {
    if (targetId === 'ug'){
        return targetVersion + '/RobotFrameworkUserGuide.html';
    }
    return targetVersion + '/libraries/' + targetId + '.html';
}

function getZipPath(version) {
    return 'robotframework-userguide-' + version + '.zip'
}

function getBaseURL() {
    return window.location.href.replace(window.location.hash, '');
}

function go(event_) {
    var target = getIdAndVersion(event_);
    document.location = getBaseURL() + getGoPath(target.id, target.version);
}

function download(event_) {
    var target = getIdAndVersion(event_);
    document.location = getBaseURL() + getZipPath(target.version);
}

window.onload = function() {
    var goButtons = document.getElementsByClassName('go-button');
    var downloadButtons = document.getElementsByClassName('download-button');
    for (var i = goButtons.length - 1; i >= 0; i--) {
        addEvent(goButtons[i], 'click', go);
        addEvent(downloadButtons[i], 'click', download);
    };
};
