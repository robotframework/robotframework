storage = function () {

    var prefix = 'robot-framework-';

    function init(user) {
        prefix += user + '-';
    }

    function get(name, defaultValue) {
        try {
            var value = localStorage[prefix + name];
        } catch (exception) {
            return defaultValue;
        }
        if (typeof value === 'undefined')
            return defaultValue;
        return value;

    }

    function set(name, value) {
        try {
            localStorage[prefix + name] = value;
        } catch (exception) {}
    }

    return {init: init, get: get, set: set};
}();
