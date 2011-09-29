describe("Searching by tags", function () {

    it("should find tags by name", function () {
        expect(model.containsTag(['name'], 'name')).toBeTruthy();
        expect(model.containsTag(['x', 'y', 'z'], 'y')).toBeTruthy();
        expect(model.containsTag([], 'name')).not.toBeTruthy();
        expect(model.containsTag(['x', 'y'], 'notthere')).not.toBeTruthy();
    });

    it("should find tags case and space insensitively", function() {
        expect(model.containsTag(['name'], 'Name')).toBeTruthy();
        expect(model.containsTag(['NaMe'], 'name')).toBeTruthy();
        expect(model.containsTag(['xx', 'yy', 'zz'], 'y y')).toBeTruthy();
        expect(model.containsTag(['x      x', 'y y', 'z z'], 'XX')).toBeTruthy();
    });

    it("should find tags combined with &", function() {
        expect(model.containsTagPattern(['x', 'y'], 'x&y')).toBeTruthy();
        expect(model.containsTagPattern(['xx', 'Yy', 'ZZ'], 'Y Y & X X & zz')).toBeTruthy();
        expect(model.containsTagPattern(['x', 'y'], 'xx&y')).not.toBeTruthy();
    });

    it("should find tags combined with NOT", function() {
        expect(model.containsTagPattern(['x', 'y'], 'xNOTz')).toBeTruthy();
        expect(model.containsTagPattern(['xx', 'yy'], 'X X NOT y NOT zz')).toBeTruthy();

        expect(model.containsTagPattern(['X X', 'Y Y'], 'xxNOTyy')).not.toBeTruthy();
    });

    it("should ignore underscore in patterns and tag names", function() {
        expect(model.containsTagPattern(['a_a_1', 'x'], '* NOT a_a_*')).not.toBeTruthy();
        expect(model.containsTagPattern(['a_a_1', 'x'], '* NOT a a *')).not.toBeTruthy();
        expect(model.containsTagPattern(['a a 1', 'x'], '* NOT a_a_*')).not.toBeTruthy();
        expect(model.containsTagPattern(['a a 1', 'x'], '* NOT a a *')).not.toBeTruthy();
    });

    it("should find tags combined with patterns (* and ?)", function() {
        expect(model.containsTagPattern(['x', 'y'], 'x*')).toBeTruthy();
        expect(model.containsTagPattern(['xxxyyy'], 'x*')).toBeTruthy();
        expect(model.containsTagPattern(['xyz'], 'x?z')).toBeTruthy();
        expect(model.containsTagPattern(['-x-'], '*x*')).toBeTruthy();
        expect(model.containsTagPattern(['x', 'y'], 'x')).toBeTruthy();
    });

    it("should find tags combined with patterns and & and NOT", function() {
        expect(model.containsTagPattern(['xx', 'yy'], 'x* & y?')).toBeTruthy();
        expect(model.containsTagPattern(['xxxyyy'], 'x* NOT y')).toBeTruthy();
        expect(model.containsTagPattern(['xxxyyy'], 'x* NOT *y')).not.toBeTruthy();
    });

    it("should esacpe regex metacharacters in patterns", function() {
        expect(model.containsTagPattern(['xyz'], 'x.*')).not.toBeTruthy();
        expect(model.containsTagPattern(['x.z'], 'x.*')).toBeTruthy();
    });
});
