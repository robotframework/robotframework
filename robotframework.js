function addEvent(element, event_, func) {
    if (element.attachEvent){
        return element.attachEvent('on' + event_, func);
    } else {
        return element.addEventListener(event_, func, false);
    }
}

function getIdAndVersion(evt) {
    var targetElement = (evt.srcElement) ? evt.srcElement : event.currentTarget;
    var id = targetElement.value;
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

function go(event_) {
    var target = getIdAndVersion(event_);
    window.location.href = getGoPath(target.id, target.version);
}

function download(event_) {
    var target = getIdAndVersion(event_);
    window.location.href = getZipPath(target.version);
}

window.onload = function() {
    var goButtons = document.getElementsByClassName('go-button');
    for (var i = goButtons.length - 1; i >= 0; i--) {
        addEvent(goButtons[i], 'click', go);
    };

    var downloadButtons = document.getElementsByClassName('download-button');
    for (var i = downloadButtons.length - 1; i >= 0; i--){
      addEvent(downloadButtons[i], 'click', download);
    }
};
