storage = function () {

    var prefix = 'robot-framework-';
    var storage;

    function init(user) {
        if (user)
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

    function get(key, defaultValue) {
        var value = storage[fullKey(key)];
        if (typeof value === 'undefined')
            return defaultValue;
        return value;
    }

    function set(key, value) {
        storage[fullKey(key)] = value;
    }

    function fullKey(key) {
        return prefix + key;
    }

    return {init: init, get: get, set: set, fullKey: fullKey};
}();
