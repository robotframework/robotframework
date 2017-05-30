storage = function () {

    var prefix = 'robot-framework-';

    function init(user) {
        prefix += user + '-';
    }

    function get(name, defaultValue) {
        try {
            if (!localStorage)
                return defaultValue;
            var value = localStorage[prefix + name];
            if (typeof value === 'undefined')
                return defaultValue;
            return value;
        } catch (exception) {
            return defaultValue;
        }
    }

    function set(name, value) {
        try {
            if (localStorage)
                localStorage[prefix + name] = value;
        } catch (exception) {}
    }

    return {init: init, get: get, set: set};
}();
