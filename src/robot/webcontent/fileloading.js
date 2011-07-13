window.fileLoading = (function () {

    var fileLoadingCallbacks = {};

    function loadKeywordsFile(filename, callback) {
        fileLoadingCallbacks[filename] = callback;
        var script = document.createElement('script');
        script.type = 'text/javascript';
        script.src = filename;
        document.getElementsByTagName("head")[0].appendChild(script);
    }

    function getCallbackHandlerForKeywords(parent) {
        var callableList = [];
        return function (callable) {
            if (!parent.isChildrenLoaded) {
                callableList.push(callable);
                if (callableList.length == 1) {
                    loadKeywordsFile(parent.childFileName, function () {
                        parent.isChildrenLoaded = true;
                        for (var i = 0; i < callableList.length; i++) {
                            callableList[i]();
                        }
                    });
                }
            } else {
                callable();
            }
        }
    }

    function notifyFileLoaded(filename) {
        fileLoadingCallbacks[filename]();
    }

    return {
        getCallbackHandlerForKeywords: getCallbackHandlerForKeywords,
        notify: notifyFileLoaded
    }
}());
