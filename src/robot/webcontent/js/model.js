window.model = (function () {

    var STATUS = {
        pass:"pass",
        fail:"fail"
    };

    var KEYWORD_TYPE = {
        kw: 'KEYWORD',
        setup:'SETUP',
        teardown:'TEARDOWN'
    };

    function Suite(parent, name, source, doc, status, times, stats, metadata) {
        var suite = {};
        populateCommonAttrs(suite, name, doc, status, times);
        suite.parent = parent;
        suite.source = source;
        suite.fullname = parent ? parent.fullname + "." + name : name;
        suite.statusText = status.status.toUpperCase();
        setStats(suite, stats);
        suite.metadata = metadata;
        suite.populateKeywords = createIterablePopulator("Keyword");
        suite.populateTests = createIterablePopulator("Test");
        suite.populateSuites = createIterablePopulator("Suite");
        suite.children = function () { return suite.keywords().concat(suite.tests()).concat(suite.suites()); };
        suite.hasTeardownFailure = function () { return suiteTeardownFailed(suite) || status.parentSuiteTeardownFailed; };
        suite.getFailureMessage = function () {
            if(status.parentSuiteTeardownFailed)
                return "Teardown of the parent suite failed.";
            if(suite.hasTeardownFailure())
                return "Suite teardown failed:\n"+
                    suite.keyword(suite.numberOfKeywords-1).message(0).text;
        };
        suite.searchTests = function (predicate) {
            var tests = [];
            for (var i=0; i<this.numberOfSuites; i++)
                tests = tests.concat(this.suite(i).searchTests(predicate));
            return tests.concat(util.filter(this.tests(), predicate));
        };
        suite.searchTestsByTag = function (tag) {
            return suite.searchTests(function (test) { return containsTag(test.tags, tag.label, tag.info == 'combined'); });
        };
        suite.findSuiteByName = function (name) {
            return findSuiteByName(suite, name);
        };
        suite.allTests = function () {
            return suite.searchTests(function (test) { return true; });
        };
        suite.criticalTests = function () {
            return suite.searchTests(function (test) { return test.isCritical; });
        };
        return suite;
    }

    function containsTag(testTags, tagname, isCombined) {
        testTags = util.map(testTags, util.normalize);
        if (!isCombined)
            return util.contains(testTags, util.normalize(tagname));
        if (tagname.indexOf(' & ') != -1) {
            var tagnames = tagname.split(' & ');
            return util.all(util.map(tagnames, function (name) { return containsTag(testTags, name, true); }));
        }
        if (tagname.indexOf(' NOT ') != -1) {
            var tagnames = tagname.split(' NOT ');
            var required = tagnames[0];
            var notAllowed = tagnames.slice(1);
            return containsTag(testTags, required, true) &&
                    util.all(util.map(notAllowed, function (name) { return !containsTag(testTags, name, true); }))
        }
        var matcher = util.Matcher(tagname)
        return util.any(util.map(testTags, matcher.matches));
    }

    function findSuiteByName(suite, name) {
        if (suite.fullname == name)
            return suite;
        var subSuites = suite.suites();
        for (var i=0; i<subSuites.length; i++) {
            var match = findSuiteByName(subSuites[i], name);
            if (match)
                return match;
        }
        return null;
    }

    function suiteTeardownFailed(suite){
        if (suite.numberOfKeywords) {
            var kw = suite.keyword(suite.numberOfKeywords -1);
            if (kw.type == KEYWORD_TYPE.teardown)
                return kw.status == STATUS.fail;
        }
        return false;
    }

    function setStats(suite, stats) {
        for (var name in stats) {
            suite[name] = stats[name];
        }
    	if (suite.totalFailed > 0)
    	    suite.totalFailureClass = 'fail';
    	if (suite.criticalFailed > 0)
    	    suite.criticalFailureClass = 'fail';
    }

    function populateCommonAttrs(obj, name, doc, status, times) {
        obj.name = name;
        obj.documentation = doc;
        obj.status = status.status;
        obj.times = times;
    }

    function Test(parent, name, doc, timeout, isCritical, status, times, tags) {
        var test = {};
        populateCommonAttrs(test, name, doc, status, times);
        test.fullname= parent.fullname + "." + test.name;  // TODO: is this used?, could be function also
        test.parentName = function () {
            return parent.fullname.replace('.', ' . ', 'g') + ' . '; // TODO: duplicate
        };
        test.timeout = timeout;
        test.populateKeywords = createIterablePopulator("Keyword");
        test.children = function () { return test.keywords(); };
        test.isCritical = isCritical;
        test.statusText = test.status.toUpperCase() + (isCritical ? " (critical)" : "");
        test.tags = tags;
        test.parentSuiteTeardownFailed = status.parentSuiteTeardownFailed;
        test.getFailureMessage = function () { return getTestFailureMessage(test); };
        return test;
    }

    function Keyword(type, name, args, doc, status, times, parent, index) {
        var kw = {};
        populateCommonAttrs(kw, name, doc, status, times);
        kw.type = type;
        var parentPath = (parent.path === undefined) ? parent.fullname : parent.path;
        kw.path = parentPath + "." + index;
        kw.arguments = args;
        kw.populateKeywords = createIterablePopulator("Keyword");
        kw.populateMessages = createIterablePopulator("Message");
        kw.children = function () { return kw.keywords(); };
        kw.getFailureMessage = getKeywordFailureMessage;
        return kw;
    }

    function Message(level, time, text, link) {
        var message = {};
        message.level = level;
        message.levelText = level.toUpperCase();
        message.time = time;
        message.shortTime = function () {return timeFromDate(message.time);};
        message.date = function () {return formatDate(message.time);};
        message.text = text;
        message.link = link;
        return message;
    }

    function Status(status, parentSuiteTeardownFailed) {
        return {
            parentSuiteTeardownFailed: parentSuiteTeardownFailed,
            status: parentSuiteTeardownFailed? model.FAIL : status
        };
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
        return shortTime(date.getHours(), date.getMinutes(),
                date.getSeconds(), date.getMilliseconds());
    }

    function formatDate(date, excludeMillis) {
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

    function getKeywordFailureMessage() {
        var msg = getFailureMessageFromKeywords(this);
        if (msg)
            return msg;
        if (this.message(0)) return this.message(0).text;
        }

    function getFailureMessageFromKeywords(obj) {
        for(var i = 0; i < obj.numberOfKeywords; i++){
            var child = obj.keyword(i);
            if (child.status == STATUS.fail)
                return child.getFailureMessage();
        }
    }

    function getTestFailureMessage(test) {
        var msg = getFailureMessageFromKeywords(test);
        if (msg)
            return msg;
        if (test.parentSuiteTeardownFailed)
            return "Teardown of the parent suite failed.";
        return '';
    }

    return {
        Suite: Suite,
        Test: Test,
        Keyword: Keyword,
        Message: Message,
        Status: Status,
        Times: Times,
        PASS: STATUS.pass,
        FAIL: STATUS.fail,
        formatElapsed: formatElapsed,
        containsTag: containsTag,  // Exposed for tests
        shortTime: shortTime
    };
}());

window.stats = (function () {

    function Statistics(totalElems, tagElems, suiteElems){
        return {total: util.map(totalElems, statElem),
                tag:   util.map(tagElems, tagStatElem),
                suite: util.map(suiteElems, suiteStatElem)};
    }

    function statElem(data) {
        var stat = {
            label: data[0],
            pass:  data[1],
            fail:  data[2],
            total: data[1] + data[2],
            doc:   data[3]
        };
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
        stat.info = data[4];
        if (stat.info)
            stat.shownInfo = '(' + stat.info + ')';
        else
            stat.shownInfo = '';
        stat.links = parseLinks(data[5]);
        return stat;
    }

    function suiteStatElem(data) {
        var stat = statElem(data);
        stat.fullname = function () { return stat.doc; };
        var nameParts = stat.doc.split('.');
        stat.name = nameParts.pop();
        if (nameParts)
            nameParts.push('');
        stat.parentName = nameParts.join(' . ');
        return stat;
    }

    function parseLinks(linksData) {
        if (!linksData)
            return [];
        var items = linksData.split(':::');
        var links = [];
        for (var i=0; i<items.length; i++) {
            parts = items[i].split(':');
            links[i] = {title: parts[0], url: parts.splice(1).join(':')};
        }
        return links;
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
