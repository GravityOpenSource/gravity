<!DOCTYPE HTML>
<%
    import os

    ## Generates hash (hdadict['id']) of history item
    hdadict = trans.security.encode_dict_ids( hda.to_dict() )

    ## Finds the parent directory of galaxy (/, /galaxy, etc.)
    root     = h.url_for( '/' )

    ## Determines the exposed URL of the ./static directory
    app_root = root + 'static/plugins/visualizations/'+visualization_name+'/static/'

    ## Actual file URL:
    file_url = os.path.join(root, 'datasets', hdadict['id'], "display?to_ext="+hda.ext)

    ## Extract info from tsv file,then covert into a dictionary
    output = {
        'depth': [],
        'cov_pct': [],
        'data_type':''
    }
    #data_type = ""
    depthcovfile = open(hda.file_name,'r')
    for line in depthcovfile:
        chunks = line.strip().split("\t")
        output["depth"].append(chunks[1])
        output["cov_pct"].append(float(chunks[2]))
    depthcovfile.close()
    if max(output["cov_pct"]) <=1:
        output['data_type'] = "Coverage"
    else:
        output['data_type'] = "Depth"

%>
<!DOCTYPE html>
<html lang="en" xml:lang="en" xmlns="http://www.w3.org/1999/xhtml">
<head>
    <meta content="text/html;charset=UTF-8" http-equiv="content-type">
    <title>DepthCoverage</title>
 
    <!-- jquery -->
    ${h.javascript_link( app_root + 'jquery-2.2.4.min.js' )}

    <!-- echarts -->
    ${h.javascript_link( app_root + 'echarts.min.js' )}
    <script>
        var file_url = "${file_url}";
        var output = ${output};
        console.log(output);

        var myChart;
        function DrawHistogram() {
            
            myChart = echarts.init(document.getElementById('main'));

            myChart.showLoading({
                text: "loading..."
            });

            var options = {
                color: ['#778899'],
                title: {
                    text: output.data_type,
                    left: 550
                },
                tooltip: {
                    trigger: 'axis',
                    axisPointer: {
                        type: 'shadow'
                    }
                },
                grid: {
                    bottom: 90
                },
                dataZoom: [{
                    type: 'inside'
                }, {
                    type: 'slider'
                }],
                xAxis: {
                        type: 'category',
                        data: []
                    },
                yAxis: {
                        type: 'value'
                    },
                series: [{
                    type: 'bar',
                    data:[],
                    showBackground: true,
                    backgroundStyle: {
                        color: 'rgba(240, 255, 240, 0.05)'
                        }
                }]
            };
   
            options.series[0].data = output.cov_pct;
            options.xAxis.data  =  output.depth;
            myChart.hideLoading();
            myChart.setOption(options);
                
        };
    </script>
</head>
<body onload="DrawHistogram()">
    <div id="main" style="width:1200px;height:800px;"></div>
</body>
</html>
