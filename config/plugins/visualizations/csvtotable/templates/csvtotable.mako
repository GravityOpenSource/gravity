<%
    root = h.url_for( "/static/" )
    app_root = root + "plugins/visualizations/csvtotable/static/"
    data_url = h.url_for(controller='/datasets', action='index')+"/"+trans.security.encode_id( hda.id )+"/display"
    data_type = hda.to_dict().get('file_ext')
%>
<!doctype html>
<html>
<head>
    <meta charset="utf-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge,chrome=1">
    <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
    <title>CSV/TSV转表格</title>
    <!-- CSS -->
    ${h.stylesheet_link( app_root + 'css/bootstrap.min.css' )}
    ${h.stylesheet_link( app_root + 'css/jquerysctipttop.css' )}
    ${h.stylesheet_link( app_root + 'css/style.css' )}
</head>
<body>
<div class="container clearfix">
    <div class="container-title">
        <!--div>
            <button class="btn main-button" id="refresh">刷新</button>
        </div-->
        <input type="text" placeholder="搜索……" id="searchField">
        <span>
      每页行数:
      <select name="rowsPerPage" id="changeRows">
        <option value="10">10</option>
        <option value="20" selected>20</option>
        <option value="50">50</option>
        <option value="100">100</option>
      </select>
    </span>
    </div>
    <div id="table-sortable"></div>
</div>
</body>
<!-- JS -->
    ${h.javascript_link( app_root + 'js/jquery.min.js' )}
    ${h.javascript_link( app_root + 'js/table-sortable.js' )}
    ${h.javascript_link( app_root + 'js/jquery.csv.js' )}
    ${h.javascript_link( app_root + 'js/jquery.tsv.js' )}
    ${h.javascript_link( app_root + 'js/app.js' )}
<!-- SCRIPT -->
<script type="text/javascript">
    $(document).ready(() => {
        ##  let dataUrl = "${h.url_for( controller='/datasets', action='index')}/${trans.security.encode_id( hda.id )}/display";
            window.console.log("${data_type}")
        setData("${data_url}", "${data_type}");
    });
</script>
</html>
