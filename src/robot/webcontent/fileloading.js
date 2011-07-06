window.fileLoading = (function () {

    var fileLoadingCallbacks = {};

    function loadTestKeywordsFile(filename, callback) {
        fileLoadingCallbacks[filename] = callback;
        var script = document.createElement('script');
        script.type = 'text/javascript';
        script.src = filename;
        document.getElementsByTagName("head")[0].appendChild(script);
    }

    function notifyFileLoaded(filename) {
        fileLoadingCallbacks[filename]();
    }

    return {
        load: loadTestKeywordsFile,
        notify: notifyFileLoaded
    }
}());
