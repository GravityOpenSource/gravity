<!DOCTYPE HTML>
<html>
<head>
    <style type="text/css">
    body { color: #303030; background: #dfe5f9; font-family:"Lucida Grande",verdana,arial,helvetica,sans-serif; font-size:12px; line-height:16px; }
    .content { max-width: 720px; margin: auto; margin-top: 50px; }
    </style>
    <title>无授权</title>
</head>
<body>
    <div class="content">
        <h1>检测授权失败</h1>
        <h2>${verify.error_msg}</h2>
        <p>本机序列号：${verify.machine_code}</p>
        <p>授权截止日：${verify.expire}</p>
        <hr>
        <p>请输入从服务商处获取的授权码：</p>
        <form action="/admin/license_reg" method="post">
            <textarea name="code" rows="8" style="width: 100%">${verify.license}</textarea>
            <input type="submit">
        </form>
    </div>
</body>
</html>