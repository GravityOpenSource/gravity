/** zh localization */
/* any suggestions, please contact me: ishenweiyan@qq.com */
define({
    // ----------------------------------------------------------------------------- masthead
    "Analyze Data": "数据分析",
    Workflow: "流程",
    "Shared Data": "共享的数据",
    "Data Libraries": "数据库",
    Histories: "已发布的历史",
    Workflows: "已发布的流程",
    Visualizations: "已发布的可视化",
    Pages: "已发布的页面",
    Visualization: "可视化",
    "New Track Browser": "创建 Track Browser",
    "Saved Visualizations": "已保存的可视化",
    "Interactive Environments": "交互式环境",
    Admin: "管理员",
    Help: "帮助",
    Support: "支持",
    Search: "搜索",
    "Mailing Lists": "邮件列表",
    Videos: "视频",
    Wiki: false,
    "How to Cite Galaxy": "引用",
    "Interactive Tours": "使用引导",
    User: "用户",
    Login: "登陆",
    Register: "注册",
    "Login or Register": "登陆或注册",
    "Logged in as": "您已登陆为",
    Preferences: "用户偏好性",
    "Custom Builds": "自定义构建集",
    Logout: "退出",
    "Saved Histories": "保存历史",
    "Saved Datasets": "保存数据集",
    "Saved Pages": "保存页面",
    "Create Visualization": "创建可视化",
    Datasets: "数据集",
    "Histories shared with me": "与我分享的历史",
    "Active InteractiveTools": "活动的交互工具",
    Tools: "工具",
    "Show favorites": "显示收藏夹",
    "All workflows": "所有流程",
    "clear search (esc)": "清除搜索 (esc键)",
    "Using ": "使用 ",
    Details: "详情",
    "(empty)": "(空)",

    //Tooltip
    "Account and saved data": "账号及数据保存",
    "Account registration or login": "注册与登录",
    "Support, contact, and community": "支持，联系，社区",
    "Administer this Galaxy": "管理您的平台",
    "Visualize datasets": "数据集可视化",
    "Access published resources": "访问发布的资源",
    "Chain tools into workflows": "将工具链接到工作流程中",
    "Analysis home view": "数据分析主页",
    "Log in or register a new account": "登录或注册一个新帐户",
    // ---------------------------------------------------------------------------- histories
    History: "历史",
    "Refresh history": "刷新历史记录",
    "Create new history": "创建新的历史记录",
    "View all histories": "查看所有历史记录",
    "History options": "操作历史记录",
    "Switch to": "切换",
    "History Actions": "历史操作",
    "Set Permissions": "设置权限",
    "Make Private": "设为私有",
    "Collapse Expanded Datasets": "合并数据集",
    "This will make all the data in this history private (excluding library datasets), and will set permissions such that all new data is created as private.  Any datasets within that are currently shared will need to be re-shared or published.  Are you sure you want to do this?": "这将使此历史记录中的所有数据成为私有(不包括数据库)，并将设置权限，以便将所有新数据创建为私有。任何当前共享的数据集都需要重新共享或发布。您确定要这么做吗?",
    "Really unhide all hidden datasets?": "确认显示所有隐藏的数据集吗?",
    "Really delete all hidden datasets?": "确认删除所有隐藏的数据集吗?",
    "Really delete all deleted datasets permanently? This cannot be undone.": "确认清空所有已删除的数据集吗？此操作无法恢复！",
    // ---- history/options-menu
    "History Lists": "历史列表",
    // Saved histories is defined above.
    "Saved Histories": "保存历史",
    "Histories Shared with Me": "分享给您历史",
    "Current History": "当前历史",
    "Create New": "创建新的历史",
    "Copy History": "复制历史",
    "Share or Publish": "分享或发布历史",
    "Show Structure": "展示结构",
    "Extract Workflow": "提取为工作流",
    // Delete is defined elsewhere, but is also in this menu.
    Copy: "复制",
    Delete: "删除",
    Undelete: "撤销删除",
    Purge: "清空",
    "Delete Permanently": "永久删除",
    "Dataset Actions": "数据操作",
    "Copy Datasets": "复制数据集",
    "Dataset Security": "数据安全",
    "Resume Paused Jobs": "恢复已暂停的任务",
    // "Collapse Expanded Datasets": false,
    "Unhide Hidden Datasets": "取消隐藏的数据集",
    "Delete Hidden Datasets": "删除隐藏的数据集",
    "Purge Deleted Datasets": "清空已删除的数据集",
    Downloads: "下载",
    "Export Tool Citations": "导出工具文献引用",
    "Export History to File": "导出历史到文件",
    "Other Actions": "其他操作",
    "Import from File": "从文件导入",
    Webhooks: false,

    // ---- history-model
    // ---- history-view
    "This history is empty": "历史已空",
    "No matching datasets found": "未找到匹配的数据集",
    "An error occurred while getting updates from the server": "从服务器更新出现错误",
    "Please contact a Galaxy administrator if the problem persists": "如果问题仍然存在，请联系Galaxy管理员",
    //TODO:
    "An error was encountered while <% where %>": "出现错误，当执行以下操作时: <% where %>",
    "search datasets": "搜索数据集",
    "You are currently viewing a deleted history!": "您正在查看已删除的历史记录",
    "You are over your disk quota": "您超出了您的磁盘配额",
    "Tool execution is on hold until your disk usage drops below your allocated quota":
        "工具执行处于暂停状态，直到您的磁盘使用量低于您分配的配额",
    All: "全选",
    None: "不选",
    "For all selected": "为所有选中",
    Server: "服务器",
    "Visualize this data": "可视化数据",

    // ---- history-view-edit
    "shown": "显示",
    "hide deleted": "隐藏删除",
    "deleted": "删除",
    "hide hidden": "收起隐藏",
    "hidden": "隐藏",
    "Edit history tags": "编辑历史标签",
    "Edit history annotation": "编辑历史备注",
    "Edit history Annotation": "编辑历史备注", //大写
    "Unnamed history": "未命名的历史",
    "Click to rename history": "单击要重命名的历史",
    "Drag datasets here to copy them to the current history": "将数据集拖到此处以将其复制到当前历史记录",
    // multi operations
    "search histories": "搜索历史记录",
    "search all datasets": "搜索所有数据集",
    "Operations on multiple datasets": "编辑多个数据集",
    "Create new": "新增",
    "Hide datasets": "隐藏数据集",
    "Unhide datasets": "显示数据集",
    "Delete datasets": "删除数据集",
    "Undelete datasets": "取消删除数据集",
    "Permanently delete datasets": "永久删除数据集",
    "Build Dataset List": "建立数据集列表",
    "Build Dataset Pair": "建立数据集对",
    "Build List of Dataset Pairs": "建立数据集对列表",
    "Build Collection from Rules": "从规则中构建集合",
    "This will permanently remove the data in your datasets. Are you sure?": "这将永久在您的数据集删除数据。您确定吗？",

    // ---- history-view-annotated
    Dataset: "数据",
    Annotation: "备注",

    // ---- history-view-edit-current
    "This history is empty. Click 'Get Data' on the left tool menu to start": "历史已空，请单击左边窗格中‘获取数据’",
    "You must be logged in to create histories": "您必须登录后才能创建历史",
    //TODO:
    "You can ": "您可以 ",
    " or ": " 或者 ",
    "load your own data": "上传您的个人数据",
    "get data from an external source": "从外部来源获取数据",

    // these aren't in zh/ginga.po and the template doesn't localize
    //"Include Deleted Datasets" :
    //false,
    //"Include Hidden Datasets" :
    //false,

    // ---------------------------------------------------------------------------- upload-view
    "Download from web or upload from disk": "从网站下载或从磁盘上传文件",
    // ---------------------------------------------------------------------------- upload-button
    // "Download from URL or upload files from disk": false,
    "Download from URL or upload files from disk": "从网站下载或从磁盘上传文件",

    // ---------------------------------------------------------------------------- trackster
    "New Visualization": "新的可视化",
    "Add Data to Saved Visualization": "将数据添加到保存的可视化中",
    "Close visualization": "关闭可视化",
    Circster: false,
    Bookmarks: "书签",
    "Add group": "添加组",

    // ---------------------------------------------------------------------------- library-dataset-view
    "Import into History": "导入历史",
    // ---------------------------------------------------------------------------- library-foldertoolbar-view
    "Location Details": "位置详情",
    "Deleting selected items": "删除选中项",
    "Please select folders or files": "请选择文件夹或文件",
    "Please enter paths to import": "请输入要导入的路径",
    "Adding datasets from your history": "从您的历史添加数据集",
    "Create New Folder": "创建新的文件夹",
    // ---------------------------------------------------------------------------- library-librarytoolbar-view
    "Create New Library": "创建新的库",

    // ---------------------------------------------------------------------------- datasets
    // ---------------------------------------------------------------------------- dataset-edit-attributes
    "Save permissions.": "保存权限。",
    "Change the datatype to a new type.": "将数据类型更改为新类型。",
    "Convert the datatype to a new format.": "将数据类型转换为新的格式。",
    "Save attributes of the dataset.": "保存数据集的属性。",
    "Change data type": "改变数据类型",
    "Edit dataset attributes": "编辑数据集属性",
    "Save permissions": "保存权限",
    "Manage dataset permissions": "数据集管理权限",
    "Change datatype": "改变数据类型",
    "Convert datatype": "转换数据类型",
    "Convert to new format": "转换为新格式",
    "Detect datatype": "检测数据类型",
    "Detect the datatype and change it.": "检测数据类型并更改它。",
    Save: "保存",
    Permissions: "权限",
    Datatypes: "数据类型",
    Convert: "转换",
    Attributes: "属性",

    // ---- hda-model
    "Unable to purge dataset": "无法清除数据集",

    // ---- hda-base
    // display button
    "Cannot display datasets removed from disk": "无法显示已从磁盘中删除的数据集",
    "This dataset must finish uploading before it can be viewed": "此数据集必须先完成上传, 然后才能查看",
    "This dataset is not yet viewable": "此数据集是不可见的",
    "View data": "查看数据",
    // download button
    Download: "下载",
    "Download dataset": "下载数据集",
    "Additional files": "其他文件",
    // info/show_params
    "View details": "查看详情",

    // dataset states
    // state: new
    "This is a new dataset and not all of its data are available yet": "这是一个新的数据集，并不是所有的数据都可用",
    // state: noPermission
    "You do not have permission to view this dataset": "您无权查看此数据集",
    // state: discarded
    "The job creating this dataset was cancelled before completion": "创建此数据集的任务在完成之前已被取消",
    // state: queued
    "This job is waiting to run": "任务正在等待运行",
    // state: upload
    "This dataset is currently uploading": "此数据集正在上传中",
    // state: setting_metadata
    "Metadata is being auto-detected": "元数据正在被自动检测中",
    // state: running
    "This job is currently running": "任务正在运行中",
    // state: paused
    'This job is paused. Use the "Resume Paused Jobs" in the history menu to resume':
        '此任务已暂停。使用历史菜单中的 "恢复已暂停的工作" 来恢复',
    // state: error
    "An error occurred with this dataset": "此数据集发生错误",
    // state: empty
    "No data": "没有数据",
    // state: failed_metadata
    "An error occurred setting the metadata for this dataset": "设置此数据集的元数据时发生错误",

    // ajax error prefix
    "There was an error getting the data for this dataset": "获取此数据集的数据时出错",

    // purged'd/del'd msg
    "This dataset has been deleted and removed from disk": "此数据集已被删除并从磁盘中删除",
    "This dataset has been deleted": "此数据集已被删除",
    "This dataset has been hidden": "此数据集已被隐藏",

    format: "格式",
    database: "数据库",

    // ---- hda-edit
    "Edit attributes": "编辑属性",
    "Cannot edit attributes of datasets removed from disk": "无法编辑已从磁盘中删除的数据集的属性",
    "Undelete dataset to edit attributes": "取消删除数据集以编辑属性",
    "This dataset must finish uploading before it can be edited": "该数据集必须先上传完成, 然后才能编辑",
    "This dataset is not yet editable": "该数据集不可编辑",

    Delete: "删除",
    "Dataset is already deleted": "数据集已被删除",

    "View or report this error": "查看或报告此错误",

    "Run this job again": "重新运行此任务",

    Visualize: "可视化",
    "Visualize in": "的可视化",

    "Undelete it": "取消删除",
    "Permanently remove it from disk": "从磁盘中永久删除",
    "Unhide it": "取消隐藏",

    "You may be able to": "您可能可以",
    "set it manually or retry auto-detection": "手动设置或重试自动检测",

    "Edit dataset tags": "编辑数据集标签",
    "Edit dataset annotation": "编辑数据集备注",

    "Tool Help": "工具帮助",

    // ---------------------------------------------------------------------------- admin
    "Search Tool Shed": "搜索 Tool Shed",
    "Monitor installing repositories": "",
    "Manage installed tools": "管理已安装的工具",
    "Reset metadata": "重置元数据",
    "Download local tool": "下载本地工具",
    "Tool lineage": false,
    "Reload a tool's configuration": "重新加载工具的配置",
    "Review tool migration stages": "查看工具迁移状态",
    "View Tool Error Logs": "查看工具错误日志",
    "Manage Display Whitelist": "管理显示白名单",
    "Manage Tool Dependencies": "管理工具依赖",
    Users: "用户",
    Groups: "组别",
    "API keys": false,
    "Impersonate a user": "模拟用户",
    Data: "数据",
    Quotas: "配额",
    Roles: "角色",
    "Local data": "本地数据",
    "Form Definitions": "定义表单",
    "Data types": "数据类型",
    "Data tables": "数据表",
    "Display applications": "显示应用程序",
    Jobs: "工作",
    "Workflow invocations": "流程调用",
    "User Management": "用户管理",
     Forms: "表单",
    "Tool Management": "工具管理",
    "Install or Uninstall": "安装或卸载",
    "Monitor installation": "监控安装",
    "Manage tools": "管理工具",
    "Manage metadata": "管理元数据",
    "Manage whitelist": "管理白名单",
    "Manage dependencies": "管理依赖关系",
    "View lineage": "查看家系",
    "View migration stages": "查看迁移阶段",
    "View error logs": "查看错误日志",

    // ---------------------------------------------------------------------------- Scratchbook
    "Enable/Disable Scratchbook": "启用/禁用 Scratchbook",
    "Show/Hide Scratchbook": "显示/隐藏 Scratchbook",

    // ---------------------------------------------------------------------------- misc. MVC
    Tags: "标签",
    "Edit annotation": "编辑备注",

    // ---------------------------------------------------------------------------- error-modal
    "An error occurred": "发生一个错误",
    "Please contact a Galaxy administrator if the problem persists.": "如果问题仍然存在，请联系系统管理员。",
    "An error occurred while updating information with the server.": "使用服务器更新信息时出错。",
    "The following information can assist the developers in finding the source of the error:":  "以下信息可以帮助开发人员查找错误的来源：",
    "Error:":  "错误：",
    "You appear to be offline. Please check your connection and try again.": "您似乎处于离线状态。 请检查您的连接，然后重试。",
    "Offline?": "离线？",
    "Galaxy is currently unreachable. Please try again in a few minutes.": "系统目前无法访问。请过几分钟再试。",
    "Cannot connect to Galaxy": "无法连接到系统",


    // ---------------------------------------------------------------------------- RuleCollectionBuilder
    "Numeric sorting.": "数值排序。",



  ja: true,
    fr: true,
    zh: true
});
