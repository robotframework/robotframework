storage = function () {

    var prefix = 'robot-framework-';

    function init(user) {
        prefix += user + '-';
    }

    function get(name, defaultValue) {
        if (!localStorage)
            return defaultValue;
        var value = localStorage[prefix + name];
        if (typeof value === 'undefined')
            return defaultValue;
        return value;
    }

    function set(name, value) {
        if (localStorage)
            localStorage[prefix + name] = value;
    }

    return {init: init, get: get, set: set};
}();
