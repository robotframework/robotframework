function removeJavaScriptDisabledWarning() {
    $('#javascript_disabled').remove();
}

function addHeader(suiteName, type) {
    var givenTitle = window.settings.title;
    document.title = givenTitle ? givenTitle : suiteName + " Test " + type;
    var generatedAgoMillis = window.testdata.generated().getTime();
    var template =
        '<div id="generated">' +
        '<span>Generated<br />${generated}</span><br />' +
        '<span id="generated_ago">${generatedAgo} ago</span>' +
        '</div>' +
        '<div id="report_or_log_link"><a href="#"></a></div>' +
        '<h1>${title}</h1>';
    $.tmpl(template, {
        title: document.title,
        generated: window.output.generatedTimestamp,
        generatedAgo: util.createGeneratedAgoString(generatedAgoMillis)
    }).appendTo($('#header_div'));
    addReportOrLogLink(type);
}

function addReportOrLogLink(myType) {
    var url;
    var text;
    if (myType == 'Report') {
        url = window.settings.logURL;
        text = 'LOG';
    } else {
        url = window.settings.reportURL;
        text = 'REPORT';
    }
    if (url) {
        $('#report_or_log_link a').attr('href', url);
        $('#report_or_log_link a').text(text);
    } else {
        $('#report_or_log_link').remove();
    }
}

function addStatistics() {
    var statHeaders =
        '<th class="col_stat">Total</th>' +
        '<th class="col_stat">Pass</th>' +
        '<th class="col_stat">Fail</th>' +
        '<th class="col_graph">Graph</th>';
    var statTable =
        '<h2>Test Statistics</h2>' +
        '<table class="statistics" id="total_stats">' +
        '<tr><th class="col_stat_name">Total Statistics</th>' + statHeaders + '</tr>' +
        '</table>' +
        '<table class="statistics" id="tag_stats">' +
        '<tr><th class="col_stat_name">Statistics by Tag</th>' + statHeaders + '</tr>' +
        '</table>' +
        '<table class="statistics" id="suite_stats">' +
        '<tr><th class="col_stat_name">Statistics by Suite</th>' + statHeaders + '</tr>' +
        '</table>';
    $(statTable).appendTo('#statistics_container')
    $.map(['total', 'tag', 'suite'], addStatTable);
}

function addStatTable(tableName) {
    var stats = window.testdata.statistics()[tableName];
    if (tableName == 'tag' && stats.length == 0)
       renderStatTable(tableName, 'no_tags_row');
    else {
        var templateName = tableName + 'StatRow';
        renderStatTable(tableName, window.templates[templateName], stats);
    }
}

function renderStatTable(tableName, template, stats) {
    var tableId = "#" + tableName + "_stats";
    $.tmpl(template, stats).appendTo($(tableId));
}

$.template("stat_columns",
    '<td class="col_stat">${total}</td>' +
    '<td class="col_stat">${pass}</td>' +
    '<td class="col_stat">${fail}</td>' +
    '<td class="col_graph">' +
      '<div class="graph">' +
        '<b class="pass_bar" style="width: ${passWidth}%;" title="${passPercent}%"></b>' +
        '<b class="fail_bar" style="width: ${failWidth}%;" title="${failPercent}%"></b>' +
      '</div>' +
    '</td>'
);

$.template('no_tags_row',
    '<tr>' +
    '<td class="col_stat_name">No Tags</td>' +
    '<td class="col_stat"></td>' +
    '<td class="col_stat"></td>' +
    '<td class="col_stat"></td>' +
    '<td class="col_graph">' +
      '<div class="graph"></div>' +
    '</td>' +
    '</tr>'
);
