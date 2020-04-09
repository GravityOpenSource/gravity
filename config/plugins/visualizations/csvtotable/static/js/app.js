'use strict';

let colunms = [];
let tables;
let tableData = [];

function parse(type,value) {
  tableData = [];
  if(type==='csv') {
    tableData = $.csv.toObjects(value);
  }else if(type==='tsv') {
    tableData = $.tsv.toObjects(value);
  }
};

function createTable(url,type) {
  $.ajax({
    url: url,
    dataType: "text",
    success: function (result) {
      colunms = [];
      let obj = {};
      parse(type,$.trim(result));
      let results = tableData;
      $.each(results[0], function (key, val) {
        obj = {
          "title": key,
          "class": "center",
          "render": function (data, type, full, meta) {
            return full[key];
          }
        };
        colunms.push(obj);
      });
      console.log(tables);
      if (tables) {
        tables.destroy();
        $('#example').empty();
      }
      tables = $('#example').DataTable({
        "processing": true, //是否显示处理状态(排序的时候，数据很多耗费时间长的话，也会显示这个)
        "data": results,//设置数据
        "columns": colunms,
        "destroy": true,
        "dom": '<"myWrapper"lftip>',
        "language": {
          "lengthMenu": "每页_MENU_ 条记录",
          "zeroRecords": "没有找到记录",
          "info": "第 _PAGE_ 页 ( 总共 _PAGES_ 页 )",
          "infoEmpty": "无记录",
          "search": "搜索：",
          "infoFiltered": "(从 _MAX_ 条记录搜索)",
          "paginate": {
            "previous": "上一页",
            "next": "下一页"
          }
        }
      });
    }
  });
}
