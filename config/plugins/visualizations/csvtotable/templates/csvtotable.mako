<%
    root = h.url_for( "/static/" )
    app_root = root + "plugins/visualizations/csvtotable/static/"
    data_url = h.url_for(controller='/datasets', action='index')+"/"+trans.security.encode_id( hda.id )+"/display"
    data_type = hda.to_dict().get('data_type').split('.')[-1].lower()
    print(data_type)
%>
<!doctype html>
<html>
<head>
    <meta charset="utf-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge,chrome=1">
    <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
    <title>CSV/TSV转表格</title>
    <!--  css-->
    ${h.stylesheet_link( app_root + 'css/bootstrap.min.css' )}
    ${h.stylesheet_link( app_root + 'css/jquery.dataTables.css' )}
</head>
<body>
<div class="container" style="padding: 10px">
    <table id="example" class="table table-striped table-bordered"></table>
</div>
</div>
</body>

<!--  js-->
    ${h.javascript_link( app_root + 'js/jquery.min.js' )}
    ${h.javascript_link( app_root + 'js/jquery.dataTables.js' )}
    ${h.javascript_link( app_root + 'js/jquery.csv.js' )}
    ${h.javascript_link( app_root + 'js/jquery.tsv.js' )}
    ${h.javascript_link( app_root + 'js/app.js' )}
<!--  script-->
<script type="text/javascript">
    $(document).ready(() => {
        createTable("${data_url}", "${data_type}");
    });
</script>
</html>

