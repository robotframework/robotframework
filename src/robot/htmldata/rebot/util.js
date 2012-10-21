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

    function contains(elems, e) {
        for (var i=0; i<elems.length; i++) {
            if (elems[i] == e)
                return true;
        }
        return false;
    }

    function unescape(string) {
        return string.replace(/&lt;/g, '<').replace(/&gt;/g, '>').replace(/&amp;/g, '&');
    }

    function normalize(string) {
        return string.toLowerCase().replace(/ /g, '').replace(/_/g, '');
    }

    function regexpEscape(string) {
        return string.replace(/[-[\]{}()+?*.,\\^$|#]/g, "\\$&");
    }

    function Matcher(pattern) {
        pattern = regexpEscape(normalize(pattern));
        var rePattern = '^' + pattern.replace(/\\\?/g, ".").replace(/\\\*/g, ".*") + '$';
        var regexp = new RegExp(rePattern);
        return {
            matches: function (string) { return regexp.test(string); }
        }
    }

    function formatParentName(item) {
        var parentName = item.fullName.slice(0, item.fullName.length - item.name.length);
        return parentName.replace(/\./g, ' . ');
    }

    function timeFromDate(date) {
        if (!date)
            return 'N/A';
        return formatTime(date.getHours(), date.getMinutes(),
                          date.getSeconds(), date.getMilliseconds());
    }

    function dateFromDate(date) {
        if (!date)
            return 'N/A';
        return padTo(date.getFullYear(), 4) +
               padTo(date.getMonth() + 1, 2) +
               padTo(date.getDate(), 2);
    }

    function dateTimeFromDate(date) {
        if (!date)
            return 'N/A';
        return dateFromDate(date) + ' ' + timeFromDate(date);
    }

    function formatTime(hours, minutes, seconds, milliseconds) {
        return padTo(hours, 2) + ':' +
               padTo(minutes, 2) + ':' +
               padTo(seconds, 2) + '.' +
               padTo(milliseconds, 3);
    }

    function formatElapsed(elapsed) {
        var millis = elapsed;
        var hours = Math.floor(millis / (60 * 60 * 1000));
        millis -= hours * 60 * 60 * 1000;
        var minutes = Math.floor(millis / (60 * 1000));
        millis -= minutes * 60 * 1000;
        var seconds = Math.floor(millis / 1000);
        millis -= seconds * 1000;
        return formatTime(hours, minutes, seconds, millis);
    }

    function padTo(number, len) {
        var numString = number + "";
        while (numString.length < len) numString = "0" + numString;
        return numString;
    }

    function timestamp(millis) {
        return new Date(window.output.baseMillis + millis);
    }

    function createGeneratedAgoString(generatedMillis) {
        generatedMillis = timestamp(generatedMillis);
        function timeString(time, shortUnit) {
            var unit = {'y': 'year', 'd': 'day', 'h': 'hour',
                        'm': 'minute', 's': 'second'}[shortUnit];
            var end = time == 1 ? ' ' : 's ';
            return time + ' ' + unit + end;
        }
        function compensateLeapYears(days, years) {
            // Not a perfect algorithm but ought to be enough
            return days - Math.floor(years / 4);
        }
        var generated = Math.round(generatedMillis / 1000);
        var current = Math.round(new Date().getTime() / 1000);
        var elapsed = current - generated;
        if (elapsed < 0) {
            elapsed = Math.abs(elapsed);
            prefix = '- ';
        } else {
            prefix = '';
        }
        var secs  = elapsed % 60;
        var mins  = Math.floor(elapsed / 60) % 60;
        var hours = Math.floor(elapsed / (60*60)) % 24;
        var days  = Math.floor(elapsed / (60*60*24)) % 365;
        var years = Math.floor(elapsed / (60*60*24*365));
        if (years > 0) {
            days = compensateLeapYears(days, years);
            return prefix + timeString(years, 'y') + timeString(days, 'd');
        } else if (days > 0) {
            return prefix + timeString(days, 'd') + timeString(hours, 'h');
        } else if (hours > 0) {
            return prefix + timeString(hours, 'h') + timeString(mins, 'm');
        } else if (mins > 0) {
            return prefix + timeString(mins, 'm') + timeString(secs, 's');
        } else {
            return prefix + timeString(secs, 's');
        }
    }

    return {
        map: map,
        filter: filter,
        all: all,
        any: any,
        contains: contains,
        unescape: unescape,
        normalize: normalize,
        Matcher: Matcher,
        formatParentName: formatParentName,
        timeFromDate: timeFromDate,
        dateFromDate: dateFromDate,
        dateTimeFromDate: dateTimeFromDate,
        formatElapsed: formatElapsed,
        timestamp: timestamp,
        createGeneratedAgoString: createGeneratedAgoString
    };
}();
