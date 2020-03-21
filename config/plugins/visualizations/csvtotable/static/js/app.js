let data = [];
let columns = {};

function setData(url, type) {
    $.get(url, null, function (value) {
        parse(type, $.trim(value));
    }, "text");
    // $.ajax({
    //     type: "get",  // 请求方式
    //     url: url,  // 目标资源
    //     data: null, // 请求参数
    //     dataType: "text",  // 服务器响应的数据类型
    //     success: function (value) {  // readystate == 4 && status == 200
    //         parse(type, $.trim(value));
    //     }
    // });
};

function parse(type, value) {
    if (type === 'csv') {
        data = $.csv.toObjects(value);
    } else if (type === 'tsv') {
        data = $.tsv.toObjects(value);
    }
    setColumns(data);
    getData(data);
};

function setColumns(data) {
    columns = {};
    for (const value of data) {
        for (const i in value) {
            columns[i] = i;
        }
    }
}

let table = $('#table-sortable').tableSortable({
    element: '',
    data: [],
    rowsPerPage: 10,
    pagination: true,
    searchField: '#searchField',
    nextText: '<span> >> </span>',
    prevText: '<span> << </span>',
});

$('select').on('change', function () {
    table.updateRowsPerPage(parseInt($(this).val(), 10));
});

$('#refresh').click(function () {
    table.refresh();
});

// 测试函数
$('#csvBtn').click(function () {
    setData(csvUrl, csvType);
});

// 测试函数
$('#tsvBtn').click(function () {
    setData(tsvUrl, tsvType);
});

let getData = (data) => {
    // Push data into existing data
    table.setData(data, null, true);
    // or Set new data on table, columns is optional.
    table.setData(data, columns);
};
