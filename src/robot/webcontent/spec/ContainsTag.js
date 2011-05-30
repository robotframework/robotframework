describe("Searching by tags", function () {

    it("should find tags by name", function () {
        expect(testmodel.containsTag(['name'], 'name')).toBeTruthy();
        expect(testmodel.containsTag(['x', 'y', 'z'], 'y')).toBeTruthy();
        expect(testmodel.containsTag([], 'name')).not.toBeTruthy();
        expect(testmodel.containsTag(['x', 'y'], 'notthere')).not.toBeTruthy();
    });

    it("should find tags case and space insensitively", function() {
        expect(testmodel.containsTag(['name'], 'Name')).toBeTruthy();
        expect(testmodel.containsTag(['NaMe'], 'name')).toBeTruthy();
        expect(testmodel.containsTag(['xx', 'yy', 'zz'], 'y y')).toBeTruthy();
        expect(testmodel.containsTag(['x      x', 'y y', 'z z'], 'XX')).toBeTruthy();
    });

    it("should find tags combined with &", function() {
        expect(testmodel.containsTag(['x', 'y'], 'x & y', true)).toBeTruthy();
        expect(testmodel.containsTag(['xx', 'Yy', 'ZZ'], 'Y Y & X X & zz', true)).toBeTruthy();
        expect(testmodel.containsTag(['x', 'y'], 'xx & y', true)).not.toBeTruthy();
    });

    it("should find tags combined with NOT", function() {
        expect(testmodel.containsTag(['x', 'y'], 'x NOT z', true)).toBeTruthy();
        expect(testmodel.containsTag(['xx', 'yy'], 'X X NOT y NOT zz', true)).toBeTruthy();
        expect(testmodel.containsTag(['X X', 'Y Y'], 'xx NOT yy', true)).not.toBeTruthy();
    });

    it("should find tags combined with patterns (* and ?)", function() {
        expect(testmodel.containsTag(['x', 'y'], 'x*', true)).toBeTruthy();
        expect(testmodel.containsTag(['xxxyyy'], 'x*', true)).toBeTruthy();
        expect(testmodel.containsTag(['xyz'], 'x?z', true)).toBeTruthy();
        expect(testmodel.containsTag(['-x-'], '*x*', true)).toBeTruthy();
        expect(testmodel.containsTag(['x', 'y'], 'x', true)).toBeTruthy();
    });

    it("should find tags combined with patterns and & and NOT", function() {
        expect(testmodel.containsTag(['xx', 'yy'], 'x* & y?', true)).toBeTruthy();
        expect(testmodel.containsTag(['xxxyyy'], 'x* NOT y', true)).toBeTruthy();
        expect(testmodel.containsTag(['xxxyyy'], 'x* NOT *y', true)).not.toBeTruthy();
    });

    it("should esacpe regex metacharacters in patterns", function() {
        expect(testmodel.containsTag(['xyz'], 'x.*', true)).not.toBeTruthy();
        expect(testmodel.containsTag(['x.z'], 'x.*', true)).toBeTruthy();
    });
});
