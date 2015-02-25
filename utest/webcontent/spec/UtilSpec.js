describe("Testing Matcher", function () {

    it("should match equal string", function () {
        expect(util.Matcher('xxx').matches('xxx')).toBeTruthy();
        expect(util.Matcher('xxx').matches('yyy')).not.toBeTruthy();
    });

    it("should match case and space sensitively", function () {
        var matches = util.Matcher('Hello World').matches;
        expect(matches('hello WORLD')).toBeTruthy();
        expect(matches('HELLOWORLD')).toBeTruthy();
        expect(matches('h e l l o   w o r l d')).toBeTruthy();
    });

    it("should support * wildcard", function () {
        var matches = util.Matcher('Hello*').matches;
        expect(matches('Hello')).toBeTruthy();
        expect(matches('Hello world')).toBeTruthy();
        expect(matches('HELLOWORLD')).toBeTruthy();
        expect(matches('Hillo')).not.toBeTruthy();
    });

    it("should support ? wildcard", function () {
        var matches = util.Matcher('H???o').matches;
        expect(matches('Hello')).toBeTruthy();
        expect(matches('happo')).toBeTruthy();
        expect(matches('Hello!')).not.toBeTruthy();
    });

    it("should escape regexp meta characters", function () {
        var matches = util.Matcher('a+.?').matches;
        expect(matches('a+.x')).toBeTruthy();
        expect(matches('A+.X')).toBeTruthy();
        expect(matches('a+.')).not.toBeTruthy();
        expect(matches('aaa')).not.toBeTruthy();
    });

    it("should match multi line string", function () {
        var matches = util.Matcher('first*last').matches;
        expect(matches('first line\nand last')).toBeTruthy();
        expect(matches('first\nsecond\nthird\nlast')).toBeTruthy();
    });

    it("should support matching any", function () {
        var matchesAny = util.Matcher('ab?d*').matchesAny;
        expect(matchesAny(['xxx', 'abcd'])).toBeTruthy();
        expect(matchesAny(['xxx', 'abc'])).not.toBeTruthy();
        expect(matchesAny([])).not.toBeTruthy();
    });

});

describe("Testing parseQueryString", function () {
    var parse = util.parseQueryString;

    it("should parse empty string", function () {
        expect(parse('')).toEqual({});
    });

    it("should parse one param", function () {
        expect(parse('foo=bar')).toEqual({foo: 'bar'});
    });

    it("should parse multiple params", function () {
        expect(parse('a=1&b=2&c=3')).toEqual({a: '1', b: '2', c: '3'});
    });

    it("should accept param with name alone (i.e. no =)", function () {
        expect(parse('foo')).toEqual({foo: ''});
        expect(parse('foo&bar')).toEqual({foo: '', bar: ''});
        expect(parse('a&b=2&c=&d')).toEqual({a: '', b: '2', c: '', d: ''});
    });

    it("should accept = in value (although it should be encoded)", function () {
        expect(parse('a=1=2&b==')).toEqual({a: '1=2', b: '='});
    });

    it("should convert + to space", function () {
        expect(parse('value=hello+world')).toEqual({value: 'hello world'});
    });

    it("should decode uri", function () {
        expect(parse('value=%26%20%3d')).toEqual({value: '& ='});
    });

});
