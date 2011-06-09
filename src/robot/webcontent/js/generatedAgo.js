function createGeneratedAgoString(generatedAgoMillis) {
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
    var generated = Math.round(generatedAgoMillis / 1000);
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
