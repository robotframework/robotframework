window.util = function () {

    function map(elems, func){
        var ret = [];
        for (var i=0; i<elems.length; i++) {
            ret[i] = func(elems[i]);
        }
        return ret;
    }

    function filter(elems, predicate) {
        var ret = [];
        for (var i=0; i<elems.length; i++) {
            if (predicate(elems[i]))
                ret.push(elems[i]);
        }
        return ret;
    }

    function all(elems) {
        for (var i=0; i<elems.length; i++) {
            if (!elems[i])
                return false;
        }
        return true;
    }

    function any(elems) {
        for (var i=0; i<elems.length; i++) {
            if (elems[i])
                return elems[i];
        }
        return false;
    }

    function normalize(string) {
        return string.toLowerCase().replace(' ', '', 'g');
    }

    function regexpEscape(string) {
        return string.replace(/[-[\]{}()+?*.,\\^$|#\s]/g, "\\$&");
    }

    function Matcher(pattern) {
        pattern = normalize(regexpEscape(pattern));
        var rePattern = '^' + pattern.replace('\\?', '.', 'g').replace('\\*', '.*', 'g') + '$'
        var regexp = new RegExp(rePattern);
        return {
            matches: function (string) { return regexp.test(string); }
        }
    }

    return {
        map: map,
        filter: filter,
        all: all,
        any: any,
        normalize: normalize,
        Matcher: Matcher
    };
}();
