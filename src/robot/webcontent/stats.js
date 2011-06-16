function addStatistics() {
    $.map(['total', 'tag', 'suite'], addStatTable);
}

function addStatTable(tableName) {
    var stats = window.testdata.statistics()[tableName];
    if (tableName == 'tag' && stats.length == 0)
       renderStatTable(tableName, window.templates.noTagsRow);
    else {
        var templateName = tableName + 'StatRow';
        renderStatTable(tableName, window.templates[templateName], stats);
    }
}

function renderStatTable(tableName, template, stats) {
    var tableId = "#" + tableName + "_stats";
    $.tmpl(template, stats).appendTo($(tableId));
}


