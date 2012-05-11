describe("LogLevelController", function() {
    function check_combination(min_level, default_level, should_show, expected_default, show_trace) {
        var controller = LogLevelController(min_level, default_level);
        expect(controller.should_show_log_level_chooser()).toEqual(should_show);
        if(should_show){
          expect(controller.default_log_level()).toEqual(expected_default);
          expect(controller.show_trace()).toEqual(show_trace);
        }
    }

    it("Should select correct log level", function () {
        check_combination("TRACE", "TRACE", true, "TRACE", true);
        check_combination("DEBUG", "INFO", true, "INFO", false);
        check_combination("TRACE", "DEBUG", true, "DEBUG", true);
        check_combination("INFO", "INFO", false);
        check_combination("WARN", "INFO", false);
        check_combination("DEBUG", "TRACE", true, "DEBUG", false);
    });
});
