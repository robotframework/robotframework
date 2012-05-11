describe("LogLevelController", function() {
    function checkCombination(min_level, default_level, should_show, expected_default, show_trace) {
        var controller = LogLevelController(min_level, default_level);
        expect(controller.shouldShowLogLevelChooser()).toEqual(should_show);
        if(should_show){
          expect(controller.defaultLogLevel()).toEqual(expected_default);
          expect(controller.showTrace()).toEqual(show_trace);
        }
    }

    it("Should select correct log level", function () {
        checkCombination("TRACE", "TRACE", true, "TRACE", true);
        checkCombination("DEBUG", "INFO", true, "INFO", false);
        checkCombination("TRACE", "DEBUG", true, "DEBUG", true);
        checkCombination("INFO", "INFO", false);
        checkCombination("WARN", "INFO", false);
        checkCombination("DEBUG", "TRACE", true, "DEBUG", false);
    });
});
