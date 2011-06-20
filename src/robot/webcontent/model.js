window.model = function () {

    var STATUS = {
        pass: "PASS",
        fail: "FAIL",
        notRun: "NOT RUN"
    };

    var KEYWORD_TYPE = {
        kw: 'KEYWORD',
        setup:'SETUP',
        teardown:'TEARDOWN'
    };

    function Suite(data) {
        var suite = createModelObject(data);
        suite.source = data.source;
        suite.fullname = data.parent ? data.parent.fullname + "." + data.name : data.name;
        setStats(suite, data.statistics);
        suite.metadata = data.metadata;
        suite.populateKeywords = createIterablePopulator("Keyword");
        suite.populateTests = createIterablePopulator("Test");
        suite.populateSuites = createIterablePopulator("Suite");
        suite.message = data.message;
        suite.children = function () {
            return suite.keywords().concat(suite.tests()).concat(suite.suites());
        };
        suite.hasTeardownFailure = function () {
            return suiteTeardownFailed(suite) || data.parentSuiteTeardownFailed;
        };
        suite.searchTests = function (predicate) {
            var tests = [];
            for (var i = 0; i < this.numberOfSuites; i++)
                tests = tests.concat(this.suite(i).searchTests(predicate));
            return tests.concat(util.filter(this.tests(), predicate));
        };
        suite.searchTestsByTag = function (tag) {
            return suite.searchTests(function (test) {
                if (tag.combined)
                    return containsTagPattern(test.tags, tag.combined);
                return containsTag(test.tags, tag.label);
            });
        };
        suite.findSuiteByName = function (name) {
            return findSuiteByName(suite, name);
        };
        suite.allTests = function () {
            return suite.searchTests(function (test) {
                return true;
            });
        };
        suite.criticalTests = function () {
            return suite.searchTests(function (test) {
                return test.isCritical;
            });
        };
        return suite;
    }

    function containsTag(testTags, tagname) {
        testTags = util.map(testTags, util.normalize);
        return util.contains(testTags, util.normalize(tagname));
    }

    function containsTagPattern(testTags, pattern) {
        testTags = util.map(testTags, util.normalize);
        if (pattern.indexOf('&') != -1) {
            var tagnames = pattern.split('&');
            return util.all(util.map(tagnames, function (name) {
                return containsTagPattern(testTags, name);
            }));
        }
        if (pattern.indexOf('NOT') != -1) {
            var tagnames = pattern.split('NOT');
            var required = tagnames[0];
            var notAllowed = tagnames.slice(1);
            return containsTagPattern(testTags, required) &&
                    util.all(util.map(notAllowed, function (name) {
                        return !containsTagPattern(testTags, name);
                    }));
        }
        var matcher = util.Matcher(pattern);
        return util.any(util.map(testTags, matcher.matches));
    }

    function findSuiteByName(suite, name) {
        if (suite.fullname == name)
            return suite;
        var subSuites = suite.suites();
        for (var i = 0; i < subSuites.length; i++) {
            var match = findSuiteByName(subSuites[i], name);
            if (match)
                return match;
        }
        return null;
    }

    function suiteTeardownFailed(suite) {
        if (suite.numberOfKeywords) {
            var kw = suite.keyword(suite.numberOfKeywords - 1);
            if (kw.type == KEYWORD_TYPE.teardown)
                return kw.status == STATUS.fail;
        }
        return false;
    }

    function setStats(suite, stats) {
        for (var name in stats) {
            suite[name] = stats[name];
        }
    }

    function createModelObject(data) {
        var obj = {};
        obj.name = data.name;
        obj.documentation = data.doc; // TODO: rename documentation -> doc
        obj.status = data.status;
        obj.times = data.times;
        return obj
    }

    function Test(data) {
        var names = ['name', 'doc', 'status', '...']
        var test = createModelObject(data);
        test.fullname = data.parent.fullname + "." + test.name;  // TODO: is this used?, could be function also
        test.parentName = function () {
            return data.parent.fullname.replace(/\./g, ' . ') + ' . '; // TODO: duplicate
        };
        test.timeout = data.timeout;
        test.populateKeywords = createIterablePopulator("Keyword");
        test.children = function () {
            return test.keywords();
        };
        test.isCritical = data.isCritical;
        test.tags = data.tags;
        test.message = data.message;
        // TODO: Handle failures in parent teardowns
        // data.status.parentSuiteTeardownFailed;
        // return "Teardown of the parent suite failed.";
        return test;
    }

    function Keyword(data) {
        var kw = createModelObject(data);
        kw.type = data.type;
        var parent = data.parent
        var parentPath = (parent.path === undefined) ? parent.fullname : parent.path;
        kw.path = parentPath + "." + data.index;
        kw.arguments = data.args;
        kw.populateKeywords = createIterablePopulator("Keyword");
        kw.populateMessages = createIterablePopulator("Message");
        kw.children = function () {
            return kw.keywords();
        };
        return kw;
    }

    function Message(level, time, text, link) {
        var message = {};
        message.level = level;
        message.levelText = level.toUpperCase();
        message.time = time;
        message.shortTime = function () {
            return timeFromDate(message.time);
        };
        message.date = function () {
            return formatDate(message.time);
        };
        message.text = text;
        message.link = link;
        return message;
    }

    function Times(timedata) {
        var start = timedata[0];
        var end = timedata[1];
        var elapsed = timedata[2];
        var times = {}
        times.elapsedMillis = elapsed;
        times.elapsedTime = function (excludeMillis) {
            return formatElapsed(elapsed, excludeMillis);
        };
        times.startTime = function (excludeMillis) {
            return formatDate(start, excludeMillis);
        }
        times.endTime = function (excludeMillis) {
            return formatDate(end, excludeMillis);
        }
        return times;
    }

    function timeFromDate(date) {
        if(date == null)
            return "N/A"
        return shortTime(date.getHours(), date.getMinutes(),
                date.getSeconds(), date.getMilliseconds());
    }

    function formatDate(date, excludeMillis) {
        if(date == null)
            return "N/A"
        var milliseconds = date.getMilliseconds();
        if (excludeMillis)
            milliseconds = undefined
        return padTo(date.getFullYear(), 4) +
                padTo(date.getMonth() + 1, 2) +
                padTo(date.getDate(), 2) + " " +
                shortTime(date.getHours(), date.getMinutes(), date.getSeconds(), milliseconds);
    }

    function shortTime(hours, minutes, seconds, milliseconds) {
        var ret = padTo(hours, 2) + ":" + padTo(minutes, 2) + ":" + padTo(seconds, 2);
        if (milliseconds != undefined)
            ret += "." + padTo(milliseconds, 3);
        return ret;
    }

    function formatElapsed(elapsed, excludeMillis) {
        var millis = elapsed;
        var hours = Math.floor(millis / (60 * 60 * 1000));
        millis -= hours * 60 * 60 * 1000;
        var minutes = Math.floor(millis / (60 * 1000));
        millis -= minutes * 60 * 1000;
        var seconds = Math.floor(millis / 1000);
        millis -= seconds * 1000;
        if (excludeMillis)
            millis = undefined;
        return shortTime(hours, minutes, seconds, millis);
    }

    function padTo(number, len) {
        var numString = number + "";
        while (numString.length < len) numString = "0" + numString;
        return numString;
    }

    function createIterablePopulator(name) {
        return function (populator) {
            populateIterable(this, name, populator);
        };
    }

    function populateIterable(obj, name, populator) {
        obj["numberOf" + name + "s"] = populator.numberOfItems;
        var nameInLowerCase = name.toLowerCase();
        obj[nameInLowerCase] = createGetFunction(populator.numberOfItems, populator.creator);
        obj[nameInLowerCase + "s"] = createGetAllFunction(populator.numberOfItems, obj[nameInLowerCase]);
    }

    function createGetFunction(numberOfElements, creator) {
        var cache = new Array();
        return function (index) {
            if (numberOfElements <= index)
                return undefined;
            if (!cache[index])
                cache[index] = creator(index);
            return cache[index];
        };
    }

    function createGetAllFunction(numberOfElements, getter) {
        var cached = undefined;
        return function () {
            if (cached === undefined) {
                cached = [];
                for (var i = 0; i < numberOfElements; i++) {
                    cached.push(getter(i));
                }
            }
            return cached;
        };
    }

    return {
        Suite: Suite,
        Test: Test,
        Keyword: Keyword,
        Message: Message,
        Times: Times,
        PASS: STATUS.pass,
        FAIL: STATUS.fail,
        NOT_RUN: STATUS.notRun,
        formatElapsed: formatElapsed,
        containsTag: containsTag,  // Exposed for tests
        containsTagPattern: containsTagPattern,  // Exposed for tests
        shortTime: shortTime
    };
}();

window.stats = (function () {

    function Statistics(totalElems, tagElems, suiteElems){
        return {total: util.map(totalElems, statElem),
                tag:   util.map(tagElems, tagStatElem),
                suite: util.map(suiteElems, suiteStatElem)};
    }

    function statElem(stat) {
        stat.total = stat.pass + stat.fail;
        var percents = calculatePercents(stat.total, stat.pass, stat.fail);
        stat.passPercent = percents[0];
        stat.failPercent = percents[1];
        var widths = calculateWidths(stat.passPercent, stat.failPercent);
        stat.passWidth = widths[0];
        stat.failWidth = widths[1];
        return stat;
    }

    function tagStatElem(data) {
        var stat = statElem(data);
        stat.links = parseLinks(stat.links);
        // TODO: move to templates.
        if (stat.info)
            stat.shownInfo = '(' + stat.info + ')';
        else
            stat.shownInfo = '';
        return stat;
    }

    function suiteStatElem(data) {
        var stat = statElem(data);
        stat.parentName = stat.label.slice(0, stat.label.length-stat.name.length);
        stat.parentName = stat.parentName.replace(/\./g, ' . ');
        // compatibility with RF 2.5 outputs
        if (!stat.name)
            stat.name = stat.label.split('.').pop();
        return stat;
    }

    function parseLinks(linksData) {
        if (!linksData)
            return [];
        return util.map(linksData.split(':::'), function (link) {
                var index = link.indexOf(':');
                return {title: link.slice(0, index), url: link.slice(index+1)};
            });
    }

    function calculatePercents(total, passed, failed) {
        if (total == 0)
            return [0.0, 0.0];
        pass = 100.0 * passed / total;
        fail = 100.0 * failed / total;
        if (pass > 0 && pass < 0.1)
            return [0.1, 99.9];
        if (fail > 0 && fail < 0.1)
            return [99.9, 0.1];
        return [Math.round(pass*10)/10, Math.round(fail*10)/10];
    }

    function calculateWidths(num1, num2) {
        if (num1 + num2 == 0)
            return [0.0, 0.0];
        // Make small percentages better visible
        if (num1 > 0 && num1 < 1)
            return [1.0, 99.0];
        if (num2 > 0 && num2 < 1)
            return [99.0, 1.0];
        // Handle situation where both are rounded up
        while (num1 + num2 > 100) {
            if (num1 > num2)
                num1 -= 0.1;
            if (num2 > num1)
                num2 -= 0.1;
        }
        return [num1, num2];
    }

    return {
        Statistics: Statistics
    };

}());
