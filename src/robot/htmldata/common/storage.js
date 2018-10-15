storage = function () {

    var prefix = 'robot-framework-';
    var storage;

    function init(user) {
        prefix += user + '-';
        storage = getStorage();
    }

    function getStorage() {
        // Use localStorage if it's accessible, normal object otherwise.
        // Inspired by https://stackoverflow.com/questions/11214404
        try {
            localStorage.setItem(prefix, prefix);
            localStorage.removeItem(prefix);
            return localStorage;
        } catch (exception) {
            return {};
        }
    }

    function get(name, defaultValue) {
        var value = storage[prefix + name];
        if (typeof value === 'undefined')
            return defaultValue;
        return value;
    }

    function set(name, value) {
        storage[prefix + name] = value;
    }

    return {init: init, get: get, set: set};
}();
