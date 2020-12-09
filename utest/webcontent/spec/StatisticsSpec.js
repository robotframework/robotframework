window.output = {};

describe("Statistics", function () {
    var totals = [
        {label: "All Tests",
            pass: 2,
            fail: 3,
            skip: 1}
    ];
    var tags = [
        {label: "first tag",
            pass: 3,
            fail: 0,
            skip: 1,
            doc: "tagdoc",
            info: "critical",
            links: "title:url:::t2:u2"},
        {label: "second tag",
            pass: 1,
            fail: 0,
            skip: 0}
    ];
    var suites = [
        {label: "Suite",
            pass: 4,
            fail: 0,
            skip: 0,
            name: "Suite"},
        {label:"Suite.Sub",
            pass: 4,
            fail: 0,
            skip: 0,
            name: "Sub"}
    ];
    var stats = window.stats.Statistics(totals, tags, suites);
    var totalStats = stats.total;
    var tagStats = stats.tag;
    var suiteStats = stats.suite;

    function verifyBasicStatAttributes(stat, label, pass, fail, skip) {
        expect(stat.label).toEqual(label);
        expect(stat.pass).toEqual(pass);
        expect(stat.fail).toEqual(fail);
        expect(stat.skip).toEqual(skip);
        expect(stat.total).toEqual(pass + fail + skip);
    }

    function verifySuiteStatNames(stat, name, parentName) {
        expect(stat.name).toEqual(name);
        expect(stat.formatParentName()).toEqual(parentName);
    }

    it("should contain all stats", function () {
        verifyBasicStatAttributes(totalStats[0], 'All Tests', 2, 3, 1);
    });

    it("should contain tag statistics", function () {
        var firstTagStats = tagStats[0];
        verifyBasicStatAttributes(firstTagStats, 'first tag', 3, 0, 1);
        expect(firstTagStats.doc).toEqual('tagdoc');
        var secondTagStats = tagStats[1];
        verifyBasicStatAttributes(secondTagStats, 'second tag', 1, 0, 0);
    });

    it("should contain tag stat links", function () {
        var tagWithLink = tagStats[0];
        expect(tagWithLink.links).toEqual([
            {title: "title", url: "url"},
            {title: "t2", url: "u2"}
        ]);
        var tagWithNoLink = tagStats[1];
        expect(tagWithNoLink.links).toEqual([])
    });

    it("should contain suite statistics", function () {
        var suitestats = suiteStats[0];
        verifyBasicStatAttributes(suitestats, 'Suite', 4, 0, 0);
    });

    it("should contain names and parent names for suite stats", function () {
        var statNoParents = suiteStats[0];
        verifySuiteStatNames(statNoParents, 'Suite', '');
        var statWithParents = suiteStats[1];
        verifySuiteStatNames(statWithParents, 'Sub', 'Suite . ');
    });

});


describe("Statistics percents and widths", function () {
    var totals = [
        {label: "All Tests",
            pass:2,
            fail:1,
            skip:1}
    ];
    var tags = [
        {label: "<0.1% failed",
            pass: 2000,
            fail: 1,
            skip: 0},
        {label: "<0.1% passed",
            pass: 1,
            fail: 4000,
            skip: 0},
        {label: "0% failed",
            pass: 100,
            fail: 0,
            skip: 0},
        {label: "0% passed",
            pass: 0,
            fail: 30,
            skip: 0},
        {label: "0% passed",
            pass: 5005,
            fail: 4995,
            skip: 0}
    ]

    var stats = window.stats.Statistics(totals, tags, []);
    var totalStats = stats.total;
    var tagStats = stats.tag;

    function percentagesShouldBe(stat, passPercent, failPercent, skipPercent) {
        expect(stat.passPercent).toEqual(passPercent);
        expect(stat.failPercent).toEqual(failPercent);
        expect(stat.skipPercent).toEqual(skipPercent);
    }

    function widthsShouldBe(stat, passWidth, failWidth, skipWidth) {
        expect(stat.passWidth).toEqual(passWidth);
        expect(stat.failWidth).toEqual(failWidth);
        expect(stat.skipWidth).toEqual(skipWidth);
    }

    it("should round floats to one digit in percentages and widths", function () {
        var stat = totalStats[0];
        percentagesShouldBe(stat, 50.0, 25.0, 25.0);
        widthsShouldBe(stat, 50.0, 25.0, 25.0);
    });

    it("should guarantee that non-zero percentages are at least 0.1", function () {
        var stat = tagStats[0];
        percentagesShouldBe(stat, 99.9, 0.1, 0);
        stat = tagStats[1];
        percentagesShouldBe(stat, 0.1, 99.9, 0);
    });

    it("should guarantee that non-zero widths are at least 1", function () {
        var stat = tagStats[0];
        widthsShouldBe(stat, 99, 1, 0);
        stat = tagStats[1];
        widthsShouldBe(stat, 1, 99, 0);
    });

    it("should handle pass/fail/skip percentages and widths of 0 and 100", function () {
        var stat = tagStats[2];
        percentagesShouldBe(stat, 100, 0, 0);
        widthsShouldBe(stat, 100, 0, 0);
        stat = tagStats[3];
        percentagesShouldBe(stat, 0, 100, 0);
        widthsShouldBe(stat, 0, 100, 0);
    });

    it("should guarantee that widths do not add up to over 100", function () {
        var stat = tagStats[4];
        percentagesShouldBe(stat, 50.1, 50, 0);
        widthsShouldBe(stat, 50, 50, 0);
    });
});
