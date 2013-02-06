function getFromLocalStorage(name, defaultValue) {
    if (!localStorage)
        return defaultValue;
    var value = localStorage[name];
    if (typeof value === 'undefined')
        value = defaultValue;
    return value;
}

function setToLocalStorage(name, value) {
    if (localStorage)
        localStorage[name] = value;
}
