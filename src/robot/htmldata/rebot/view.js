const lightModeIcon = `
<svg class="light-mode-icon" xmlns="http://www.w3.org/2000/svg" enable-background="new 0 0 24 24"
    viewBox="0 0 24 24" fill="var(--text-color)">
    <rect fill="none" height="24" width="24" />
    <path
        d="M12,7c-2.76,0-5,2.24-5,5s2.24,5,5,5s5-2.24,5-5S14.76,7,12,7L12,7z M2,13l2,0c0.55,0,1-0.45,1-1s-0.45-1-1-1l-2,0 c-0.55,0-1,0.45-1,1S1.45,13,2,13z M20,13l2,0c0.55,0,1-0.45,1-1s-0.45-1-1-1l-2,0c-0.55,0-1,0.45-1,1S19.45,13,20,13z M11,2v2 c0,0.55,0.45,1,1,1s1-0.45,1-1V2c0-0.55-0.45-1-1-1S11,1.45,11,2z M11,20v2c0,0.55,0.45,1,1,1s1-0.45,1-1v-2c0-0.55-0.45-1-1-1 C11.45,19,11,19.45,11,20z M5.99,4.58c-0.39-0.39-1.03-0.39-1.41,0c-0.39,0.39-0.39,1.03,0,1.41l1.06,1.06 c0.39,0.39,1.03,0.39,1.41,0s0.39-1.03,0-1.41L5.99,4.58z M18.36,16.95c-0.39-0.39-1.03-0.39-1.41,0c-0.39,0.39-0.39,1.03,0,1.41 l1.06,1.06c0.39,0.39,1.03,0.39,1.41,0c0.39-0.39,0.39-1.03,0-1.41L18.36,16.95z M19.42,5.99c0.39-0.39,0.39-1.03,0-1.41 c-0.39-0.39-1.03-0.39-1.41,0l-1.06,1.06c-0.39,0.39-0.39,1.03,0,1.41s1.03,0.39,1.41,0L19.42,5.99z M7.05,18.36 c0.39-0.39,0.39-1.03,0-1.41c-0.39-0.39-1.03-0.39-1.41,0l-1.06,1.06c-0.39,0.39-0.39,1.03,0,1.41s1.03,0.39,1.41,0L7.05,18.36z" />
</svg>`

const darkModeIcon = `
<svg class="dark-mode-icon" xmlns="http://www.w3.org/2000/svg" enable-background="new 0 0 24 24"
    viewBox="0 0 24 24" fill="var(--text-color)">
    <rect fill="none" height="24" width="24" />
    <path
        d="M11.01,3.05C6.51,3.54,3,7.36,3,12c0,4.97,4.03,9,9,9c4.63,0,8.45-3.5,8.95-8c0.09-0.79-0.78-1.42-1.54-0.95 c-0.84,0.54-1.84,0.85-2.91,0.85c-2.98,0-5.4-2.42-5.4-5.4c0-1.06,0.31-2.06,0.84-2.89C12.39,3.94,11.9,2.98,11.01,3.05z" />
</svg>`


function removeJavaScriptDisabledWarning() {
    // Not using jQuery here for maximum speed
    document.getElementById('javascript-disabled').style.display = 'none';
}

function addJavaScriptDisabledWarning(error) {
    if (window.console)
        console.error('Opening failed: ' + error.name + ': ' + error.message);
    document.getElementById('javascript-disabled').style.display = 'block';
}

function initLayout(suiteName, type) {
    parseTemplates();
    setTitle(suiteName, type);
    addHeader();
    addReportOrLogLink(type);
}

function parseTemplates() {
    $('script[type="text/x-jquery-tmpl"]').map(function (idx, elem) {
        $.template(elem.id, elem.text);
    });
}

function testOrTask(text) {
    return text.replace(/{(.*)}/, function (match, group, offset, string) {
        if (!window.settings.rpa)
            return group;
        return {'TEST': 'TASK', 'Test': 'Task', 'test': 'task'}[group];
    });
}

function setTitle(suiteName, type) {
    var givenTitle = window.settings.title;
    var title = givenTitle ? givenTitle : suiteName + " " + type;
    document.title = util.unescape(title);
}

function addHeader() {
    var generated = util.timestamp(window.output.generated);
    $.tmpl('<h1>${title}</h1>' +
           '<button id=theme-toggle>' +
             lightModeIcon +
             darkModeIcon +
           '</button>' +
           '<div id="generated">' +
             '<span>Generated<br>${generated}</span><br>' +
             '<span id="generated-ago">${ago} ago</span>' +
           '</div>' +
           '<div id="top-right-header">' +
             '<div id="report-or-log-link"><a href="#"></a></div>' +
           '</div>', {
        generated: util.createGeneratedString(generated),
        ago: util.createGeneratedAgoString(generated),
        title: document.title
    }).appendTo($('#header'));
    document.getElementById('theme-toggle')?.addEventListener('click', theme.onClick);
}

function addReportOrLogLink(myType) {
    var url;
    var text;
    var container = $('#report-or-log-link');
    if (myType == 'Report') {
        url = window.settings.logURL;
        text = 'LOG';
    } else {
        url = window.settings.reportURL;
        text = 'REPORT';
    }
    if (url) {
        container.find('a').attr('href', url);
        container.find('a').text(text);
    } else {
        container.remove();
    }
}

function addStatistics() {
    var statHeaders =
        '<th class="stats-col-stat">Total</th>' +
        '<th class="stats-col-stat">Pass</th>' +
        '<th class="stats-col-stat">Fail</th>' +
        '<th class="stats-col-stat">Skip</th>' +
        '<th class="stats-col-elapsed">Elapsed</th>' +
        '<th class="stats-col-graph">Pass / Fail / Skip</th>';
    var statTable =
        '<h2>{Test} Statistics</h2>' +
        '<table class="statistics" id="total-stats"><thead><tr>' +
        '<th class="stats-col-name">Total Statistics</th>' + statHeaders +
        '</tr></thead></table>' +
        '<table class="statistics" id="tag-stats"><thead><tr>' +
        '<th class="stats-col-name">Statistics by Tag</th>' + statHeaders +
        '</tr></thead></table>' +
        '<table class="statistics" id="suite-stats"><thead><tr>' +
        '<th class="stats-col-name">Statistics by Suite</th>' + statHeaders +
        '</tr></thead></table>';
    $(testOrTask(statTable)).appendTo('#statistics-container');
    util.map(['total', 'tag', 'suite'], addStatTable);
    addTooltipsToElapsedTimes();
    enableStatisticsSorter();
}

function addTooltipsToElapsedTimes() {
    $('.stats-col-elapsed').attr('title',
        testOrTask('Total execution time of these {test}s. ') +
        'Excludes suite setups and teardowns.');
    $('#suite-stats').find('.stats-col-elapsed').attr('title',
        'Total execution time of this suite.');
}

function enableStatisticsSorter() {
    $.tablesorter.addParser({
        id: 'statName',
        type: 'numeric',
        is: function(s) {
            return false;  // do not auto-detect
        },
        format: function(string, table, cell, cellIndex) {
            // Rows have class in format 'row-<index>'.
            var index = $(cell).parent().attr('class').substring(4);
            return parseInt(index);
        }
    });
    $(".statistics").tablesorter({
        sortInitialOrder: 'desc',
        headers: {0: {sorter: 'statName', sortInitialOrder: 'asc'},
                  6: {sorter: false}}
    });
}

function addStatTable(tableName) {
    var stats = window.testdata.statistics()[tableName];
    if (tableName == 'tag' && stats.length == 0) {
        renderNoTagStatTable();
    } else {
        renderStatTable(tableName, stats);
    }
}

function renderNoTagStatTable() {
    $('<tbody><tr class="row-0">' +
        '<td class="stats-col-name">No Tags</td>' +
        '<td class="stats-col-stat"></td>' +
        '<td class="stats-col-stat"></td>' +
        '<td class="stats-col-stat"></td>' +
        '<td class="stats-col-stat"></td>' +
        '<td class="stats-col-elapsed"></td>' +
        '<td class="stats-col-graph">' +
          '<div class="empty-graph"></div>' +
        '</td>' +
      '</tr></tbody>').appendTo('#tag-stats');
}

function renderStatTable(tableName, stats) {
    var template = tableName + 'StatisticsRowTemplate';
    var tbody = $('<tbody></tbody>');
    for (var i = 0, len = stats.length; i < len; i++) {
        $.tmpl(template, stats[i], {index: i}).appendTo(tbody);
    }
    tbody.appendTo('#' + tableName + '-stats');
}

$.template('statColumnsTemplate',
    '<td class="stats-col-stat">${total}</td>' +
    '<td class="stats-col-stat">${pass}</td>' +
    '<td class="stats-col-stat">${fail}</td>' +
    '<td class="stats-col-stat">${skip}</td>' +
    '<td class="stats-col-elapsed">${elapsed}</td>' +
    '<td class="stats-col-graph">' +
      '{{if total}}' +
      '<div class="graph">' +
        '<div class="pass-bar" style="width: ${passWidth}%" title="${passPercent}%"></div>' +
        '<div class="fail-bar" style="width: ${failWidth}%" title="${failPercent}%"></div>' +
        '<div class="skip-bar" style="width: ${skipWidth}%" title="${skipPercent}%"></div>' +
      '</div>' +
      '{{else}}' +
      '<div class="empty-graph"></div>' +
      '{{/if}}' +
    '</td>'
);

$.template('suiteStatusMessageTemplate',
    '${total} {{= testOrTask("{test}")}}{{if total != 1}}s{{/if}} total, ' +
    '${pass} passed, ${fail} failed, ${skip} skipped'
);

// For complete cross-browser experience..
// http://www.quirksmode.org/js/events_order.html
function stopPropagation(event) {
    var event = event || window.event;
    event.cancelBubble = true;
    if (event.stopPropagation)
        event.stopPropagation();
}


const theme = function () {

    const storageKey = 'theme-preference';
    const urlParams = new URLSearchParams(window.location.search);
    var storage;
    var theme;

    function init(givenStorage) {
        storage = givenStorage;
        theme = { value: getPreference() };
        document.body.setAttribute('data-theme', theme.value);
        reflectPreference();

        window.matchMedia('(prefers-color-scheme: dark)')
            .addEventListener('change', ({matches:isDark}) => {
                theme.value = isDark ? 'dark' : 'light';
                setPreference();
            });

        window.addEventListener('storage', ({key, newValue}) => {
            if (key === storage.fullKey(storageKey)) {
                theme.value = newValue === 'dark' ? 'dark' : 'light';
                setPreference();
            }
        });
    }

    function getPreference() {
        if (urlParams.has('theme')) {
            var urlTheme = urlParams.get('theme') === 'dark' ? 'dark' : 'light';
            storage.set(storageKey, urlTheme);
            urlParams.delete('theme');
            return urlTheme;
        }
        if (storage.get(storageKey))
            return storage.get(storageKey) === 'dark' ? 'dark' : 'light';
        return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
    }

    function setPreference() {
        storage.set(storageKey, theme.value);
        reflectPreference();
    }

    function reflectPreference() {
        document.body.setAttribute('data-theme', theme.value);
        document.querySelector('#theme-toggle')?.setAttribute('aria-label', theme.value);
        const event = new Event('theme-change', {value: theme.value});
        document.dispatchEvent(event);
    }

    function onClick() {
        theme.value = theme.value === 'light' ? 'dark' : 'light';
        document.body.setAttribute('theme-toggled', "");
        setPreference();
    }

    return {init: init, getPreference: getPreference, setPreference: setPreference,
        reflectPreference: reflectPreference, onClick: onClick};
}();
