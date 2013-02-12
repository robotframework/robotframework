function removeJavaScriptDisabledWarning() {
    // Not using jQuery here for maximum speed
    document.getElementById('javascript_disabled').style.display = 'none';
}

function addJavaScriptDisabledWarning() {
    document.getElementById('javascript_disabled').style.display = 'block';
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

function setTitle(suiteName, type) {
    var givenTitle = window.settings.title;
    var title = givenTitle ? givenTitle : suiteName + " Test " + type;
    document.title = util.unescape(title);
}

function addHeader() {
    $.tmpl('<div id="generated">' +
             '<span>Generated<br>${generated}</span><br>' +
             '<span id="generated_ago">${ago} ago</span>' +
           '</div>' +
           '<div id="top_right_header">' +
             '<div id="report_or_log_link"><a href="#"></a></div>' +
           '</div>' +
           '<h1>${title}</h1>', {
        generated: window.output.generatedTimestamp,
        ago: util.createGeneratedAgoString(window.output.generatedMillis),
        title: document.title
    }).appendTo($('#header'));
}

function addReportOrLogLink(myType) {
    var url;
    var text;
    var container = $('#report_or_log_link');
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
        '<th class="stats_col_stat">Total</th>' +
        '<th class="stats_col_stat">Pass</th>' +
        '<th class="stats_col_stat">Fail</th>' +
        '<th class="stats_col_elapsed">Elapsed</th>' +
        '<th class="stats_col_graph">Pass / Fail</th>';
    var statTable =
        '<h2>Test Statistics</h2>' +
        '<table class="statistics" id="total_stats"><thead><tr>' +
        '<th class="stats_col_name">Total Statistics</th>' + statHeaders +
        '</tr></thead><tbody></tbody></table>' +
        '<table class="statistics" id="tag_stats"><thead><tr>' +
        '<th class="stats_col_name">Statistics by Tag</th>' + statHeaders +
        '</tr></thead><tbody></tbody></table>' +
        '<table class="statistics" id="suite_stats"><thead><tr>' +
        '<th class="stats_col_name">Statistics by Suite</th>' + statHeaders +
        '</tr></thead><tbody></tbody></table>';
    $(statTable).appendTo('#statistics_container');
    $.map(['total', 'tag', 'suite'], addStatTable);
    stopStatLinkClickPropagation();
    addTooltipsToElapsedTimes();
    enableStatisticsSorter();
}

function stopStatLinkClickPropagation() {
    $('.statistics a').click(stopPropagation);
}

function addTooltipsToElapsedTimes() {
    $('.stats_col_elapsed').attr('title',
        'Total execution time of these test cases. ' +
        'Excludes suite setups and teardowns.');
    $('#suite_stats').find('.stats_col_elapsed').attr('title',
        'Total execution time of this test suite.');
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
        headers: {0: {sorter:'statName', sortInitialOrder: 'asc'},
                  5: {sorter: false}}
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
    $('<tr class="row-0">' +
        '<td class="stats_col_name">No Tags</td>' +
        '<td class="stats_col_stat"></td>' +
        '<td class="stats_col_stat"></td>' +
        '<td class="stats_col_stat"></td>' +
        '<td class="stats_col_elapsed"></td>' +
        '<td class="stats_col_graph">' +
          '<div class="empty_graph"></div>' +
        '</td>' +
      '</tr>').appendTo($('#tag_stats > tbody'));
}

function renderStatTable(tableName, stats) {
    var template = tableName + 'StatisticsRowTemplate';
    var target = $('#' + tableName + '_stats > tbody');
    // Need explicit for loop because $.tmpl() does not handle very large lists
    for (var i = 0; stats !== undefined && i < stats.length; i++) {
        $.tmpl(template, stats[i], {index: i}).appendTo(target);
    }
}

$.template("stat_columns",
    '<td class="stats_col_stat">${total}</td>' +
    '<td class="stats_col_stat">${pass}</td>' +
    '<td class="stats_col_stat">${fail}</td>' +
    '<td class="stats_col_elapsed">${elapsed}</td>' +
    '<td class="stats_col_graph">' +
      '{{if total}}' +
      '<div class="graph">' +
        '<div class="pass_bar" style="width: ${passWidth}%" title="${passPercent}%"></div>' +
        '<div class="fail_bar" style="width: ${failWidth}%" title="${failPercent}%"></div>' +
      '</div>' +
      '{{else}}' +
      '<div class="empty_graph"></div>' +
      '{{/if}}' +
    '</td>'
);

$.template('suiteStatusMessageTemplate',
    '${critical} critical test, ' +
    '${criticalPassed} passed, ' +
    '<span class="{{if criticalFailed}}fail{{else}}pass{{/if}}">${criticalFailed} failed</span><br>' +
    '${total} test total, ' +
    '${totalPassed} passed, ' +
    '<span class="{{if totalFailed}}fail{{else}}pass{{/if}}">${totalFailed} failed</span>'
);

// For complete cross-browser experience..
// http://www.quirksmode.org/js/events_order.html
function stopPropagation(event) {
    var event = event || window.event;
    event.cancelBubble = true;
    if (event.stopPropagation)
        event.stopPropagation();
}
