import $ from "jquery";
import _ from "underscore";
import Backbone from "backbone";
import { Toast } from "ui/toast";
import mod_library_model from "mvc/library/library-model";
import mod_library_folderrow_view from "mvc/library/library-folderrow-view";
import { getGalaxyInstance } from "app";

var FolderListView = Backbone.View.extend({
    el: "#folder_items_element",
    // progress percentage
    progress: 0,
    // progress rate per one item
    progressStep: 1,

    folderContainer: null,

    current_sort_order: "asc",

    current_sort_key: "name",

    events: {
        "click #select-all-checkboxes": "selectAll",
        "click .dataset_row": "selectClickedRow",
        "click .folder_row": "selectClickedRow",
        "click .sort-folder-name": "sortColumnClicked",
        "click .sort-folder-file_ext": "sortColumnClicked",
        "click .sort-folder-message": "sortColumnClicked",
        "click .sort-folder-update_time": "sortColumnClicked",
        "click .sort-folder-raw_size": "sortColumnClicked",
        "click .sort-folder-state": "sortColumnClicked"
    },

    collection: null,

    defaults: {
        include_deleted: false,
        page_count: null,
        show_page: null
    },

    /**
     * Initialize and fetch the folder from the server.
     * @param  {object} options an object with options
     */
    initialize: function(options) {
        this.options = _.defaults(this.options || {}, this.defaults, options);
        this.modal = null;
        // map of folder item ids to item views = cache
        this.rowViews = {};

        // create a collection of folder items for this view
        this.collection = new mod_library_model.Folder();

        // start to listen if someone modifies the collection
        this.listenTo(this.collection, "add", this.renderOne);
        this.listenTo(this.collection, "remove", this.removeOne);
        this.listenTo(this.collection, "reset", this.rePaint);

        this.fetchFolder();
    },

    fetchFolder: function(options = {}) {
        this.options.include_deleted = options.include_deleted;
        var self = this;

        this.folderContainer = new mod_library_model.FolderContainer({
            id: this.options.id
        });
        this.folderContainer.url = `${this.folderContainer.attributes.urlRoot + this.options.id}/contents`;

        if (this.options.include_deleted) {
            this.folderContainer.url = `${this.folderContainer.url}?include_deleted=true`;
        }
        this.folderContainer.fetch({
            success: function(folder_container) {
                self.folder_container = folder_container;
                self.render();
            },
            error: function(model, response) {
                const Galaxy = getGalaxyInstance();
                if (typeof response.responseJSON !== "undefined") {
                    Toast.error(`${response.responseJSON.err_msg} 单击此处返回。`, "", {
                        onclick: function() {
                            Galaxy.libraries.library_router.back();
                        }
                    });
                } else {
                    // Toast.error("An error occurred. Click this to go back.", "", {
                    Toast.error("发生一个错误。单击此处返回。", "", {
                        onclick: function() {
                            Galaxy.libraries.library_router.back();
                        }
                    });
                }
            }
        });
    },

    render: function(options) {
        this.options = _.extend(this.options, options);
        var template = this.templateFolder();
        $(".tooltip").hide();

        // find the upper id in the full path
        var path = this.folderContainer.attributes.metadata.full_path;
        var upper_folder_id;
        if (path.length === 1) {
            // the library is above us
            upper_folder_id = 0;
        } else {
            upper_folder_id = path[path.length - 2][0];
        }

        this.$el.html(
            template({
                path: this.folderContainer.attributes.metadata.full_path,
                parent_library_id: this.folderContainer.attributes.metadata.parent_library_id,
                id: this.options.id,
                upper_folder_id: upper_folder_id,
                order: this.current_sort_order
            })
        );

        // when dataset_id is present render its details too
        if (this.options.dataset_id) {
            var row = _.findWhere(self.rowViews, {
                id: this.options.dataset_id
            });
            if (row) {
                row.showDatasetDetails();
            } else {
                // Toast.error("Requested dataset not found. Showing folder instead.");
                Toast.error("找不到请求的数据集。改为显示文件夹。");
            }
        } else {
            if (this.options.show_page === null || this.options.show_page < 1) {
                this.options.show_page = 1;
            }
            this.paginate();
        }
        $('#center [data-toggle="tooltip"]').tooltip({ trigger: "hover" });
        $("#center").css("overflow", "auto");
    },

    paginate: function(options) {
        const Galaxy = getGalaxyInstance();
        this.options = _.extend(this.options, options);

        if (this.options.show_page === null || this.options.show_page < 1) {
            this.options.show_page = 1;
        }
        this.options.total_items_count = this.folder_container.get("folder").models.length;
        this.options.page_count = Math.ceil(
            this.options.total_items_count / Galaxy.libraries.preferences.get("folder_page_size")
        );
        var page_start = Galaxy.libraries.preferences.get("folder_page_size") * (this.options.show_page - 1);
        var items_to_render = null;
        items_to_render = this.folder_container
            .get("folder")
            .models.slice(page_start, page_start + Galaxy.libraries.preferences.get("folder_page_size"));
        this.options.items_shown = items_to_render.length;
        // User requests page with no items
        if (
            Galaxy.libraries.preferences.get("folder_page_size") * this.options.show_page >
            this.options.total_items_count + Galaxy.libraries.preferences.get("folder_page_size")
        ) {
            items_to_render = [];
        }
        Galaxy.libraries.folderToolbarView.renderPaginator(this.options);
        this.collection.reset(items_to_render);
    },

    rePaint: function(options) {
        this.options = _.extend(this.options, options);
        this.removeAllRows();
        this.renderAll();
        this.checkEmptiness();
    },

    /**
     * Adds all given models to the collection.
     * @param {array of Item or FolderAsModel} array of models that should
     *  be added to the view's collection.
     */
    addAll: function(models) {
        const Galaxy = getGalaxyInstance();
        _.each(models, model => {
            Galaxy.libraries.folderListView.collection.add(model, {
                current_sort_order: false
            });
        });
        $('#center [data-toggle="tooltip"]').tooltip({ trigger: "hover" });
        this.checkEmptiness();
        this.postRender();
    },

    /**
     * Call this after all models are added to the collection
     * to ensure that the folder toolbar will show proper options
     * and that event will be bound on all subviews.
     */
    postRender: function() {
        const Galaxy = getGalaxyInstance();
        var fetched_metadata = this.folderContainer.attributes.metadata;
        fetched_metadata.contains_file_or_folder =
            typeof this.collection.findWhere({ type: "file" }) !== "undefined" ||
            typeof this.collection.findWhere({ type: "folder" }) !== "undefined";
        Galaxy.libraries.folderToolbarView.configureElements(fetched_metadata);
    },

    /**
     * Iterates this view's collection and calls the render
     * function for each. Also binds the hover behavior.
     */
    renderAll: function() {
        var self = this;
        _.each(this.collection.models.reverse(), model => {
            self.renderOne(model);
        });
        this.postRender();
    },

    /**
     * Creates a view for the given model and adds it to the folder view.
     * @param {Item or FolderAsModel} model of the view that will be rendered
     */
    renderOne: function(model) {
        this.options.contains_file_or_folder = true;
        //if (model.get('type') !== 'folder'){
        // model.set('readable_size', this.size_to_string(model.get('file_size')));
        //}
        model.set("folder_id", this.id);
        var rowView = new mod_library_folderrow_view.FolderRowView({
            model: model
        });

        // save new rowView to cache
        this.rowViews[model.get("id")] = rowView;

        this.$el.find("#first_folder_item").after(rowView.el);
    },

    /**
     * Remove the view of the given model from the DOM.
     * @param {Item or FolderAsModel} model of the view that will be removed
     */
    removeOne: function(model) {
        this.$el
            .find("tr")
            .filter(function() {
                return $(this).data("id") && $(this).data("id") === model.id;
            })
            .remove();
    },

    /**
     * Remove all dataset and folder row elements from the DOM.
     */
    removeAllRows: function() {
        $(".library-row").remove();
    },

    /** Checks whether the list is empty and adds/removes the message */
    checkEmptiness: function() {
        if (this.$el.find(".dataset_row").length === 0 && this.$el.find(".folder_row").length === 0) {
            this.$el.find(".empty-folder-message").show();
        } else {
            this.$el.find(".empty-folder-message").hide();
        }
    },

    sortColumnClicked: function(event) {
        event.preventDefault();
        this.current_sort_order = this.current_sort_order === "asc" ? "desc" : "asc";
        this.current_sort_key = event.currentTarget.className.replace("sort-folder-", "");
        const sorted_folder = this.folder_container.sortFolder(this.current_sort_key, this.current_sort_order);
        this.collection.reset(sorted_folder.models);
        this.renderSortIcon();
    },

    /**
     * In case the search_term is not empty perform the search and render
     * the result. Render all visible folder items otherwise.
     * @param  {string} search_term string to search for
     */
    searchFolder: function(search_term) {
        const trimmed_term = $.trim(search_term);
        if (trimmed_term !== "") {
            const result_collection = this.folder_container.search(search_term);
            this.collection.reset(result_collection);
        } else {
            this.paginate();
        }
    },

    /**
     * User clicked the checkbox in the table heading
     * @param  {context} event
     */
    selectAll: function(event) {
        var selected = event.target.checked;
        var self = this;
        // Iterate each checkbox
        $(":checkbox", "#folder_list_body").each(function() {
            this.checked = selected;
            var $row = $(this).closest("tr");
            // Change color of selected/unselected
            if (selected) {
                self.makeDarkRow($row);
            } else {
                self.makeWhiteRow($row);
            }
        });
    },

    /**
     * Check checkbox if user clicks on the whole row or
     *  on the checkbox itself
     */
    selectClickedRow: function(event) {
        var checkbox = "";
        var $row;
        var source;
        $row = $(event.target).closest("tr");
        if (event.target.localName === "input") {
            checkbox = event.target;
            source = "input";
        } else if (event.target.localName === "td") {
            checkbox = $row.find(":checkbox")[0];
            source = "td";
        }
        if (checkbox.checked) {
            if (source === "td") {
                checkbox.checked = "";
                this.makeWhiteRow($row);
            } else if (source === "input") {
                this.makeDarkRow($row);
            }
        } else {
            if (source === "td") {
                checkbox.checked = "selected";
                this.makeDarkRow($row);
            } else if (source === "input") {
                this.makeWhiteRow($row);
            }
        }
    },

    makeDarkRow: function($row) {
        $row.addClass("table-primary");
    },

    makeWhiteRow: function($row) {
        $row.removeClass("table-primary");
    },

    renderSortIcon: function() {
        $('[class*="sort-icon"]')
            .removeClass("fa-sort-alpha-desc")
            .removeClass("fa-sort-alpha-asc");

        if (this.current_sort_order === "asc") {
            $(`.sort-icon-${this.current_sort_key}`).addClass("fa-sort-alpha-asc");
        } else {
            $(`.sort-icon-${this.current_sort_key}`).addClass("fa-sort-alpha-desc");
        }
    },

    /**
     * Create the new folder inline
     */
    createFolderInline: function() {
        if (this.$el.find("tr.new-row").length) {
            this.$el.find("tr.new-row textarea")[0].focus();
        } else {
            const template = this.templateNewFolder();
            this.$el.find("#first_folder_item").after(template);

            this.$el.find("tr.new-row textarea")[0].focus();

            this.$el.find("tr.new-row .save_folder_btn").click(() => {
                this.createNewFolder(
                    this.$el.find("tr.new-row textarea")[0].value,
                    this.$el.find("tr.new-row textarea")[1].value
                );
            });

            this.$el.find("tr.new-row .cancel_folder_btn").click(() => {
                this.$el.find("tr.new-row").remove();
            });
        }
    },

    /**
     * Create the new library using the API asynchronously.
     */
    createNewFolder: function(name, description) {
        const Galaxy = getGalaxyInstance();
        const folderDetails = {
            name,
            description
        };
        if (folderDetails.name !== "") {
            var folder = new mod_library_model.FolderAsModel();
            var url_items = Backbone.history.fragment.split("/");
            var current_folder_id;
            if (url_items.indexOf("page") > -1) {
                current_folder_id = url_items[url_items.length - 3];
            } else {
                current_folder_id = url_items[url_items.length - 1];
            }
            folder.url = folder.urlRoot + current_folder_id;

            folder.save(folderDetails, {
                success: folder => {
                    // Toast.success("Folder created.");
                    Toast.success("文件夹已创建。");
                    folder.set({ type: "folder" });
                    this.$el.find("tr.new-row").remove();
                    Galaxy.libraries.folderListView.collection.add(folder);

                    $(`tr[data-id="${folder.attributes.id}"`)
                        .addClass("table-success")
                        .on("mouseover click", function() {
                            $(this).removeClass("table-success");
                        });
                },
                error: (model, response) => {
                    Galaxy.modal.hide();
                    if (typeof response.responseJSON !== "undefined") {
                        Toast.error(response.responseJSON.err_msg);
                    } else {
                        // Toast.error("An error occurred.");
                        Toast.error("发生一个错误。");
                    }
                }
            });
        } else {
            // Toast.error("Folder's name is missing.");
            Toast.error("缺少文件夹名称。");
        }
        return false;
    },

    templateNewFolder: function() {
        return _.template(
            `<tr class="new-row">
                <td class="mid">
                    <span title="文件夹" class="fa fa-folder-o"></span>
                </td>
                <td></td>
                <td>
                    <textarea name="input_folder_name" rows="4" class="form-control input_folder_name" placeholder="名称" ></textarea>
                </td>
                <td>
                    <textarea rows="4" class="form-control input_folder_description" placeholder="描述" ></textarea>
                </td>
                <td>文件夹</td>
                <td></td>
                <td></td>
                <td></td>
                <td class="right-center">
                    <button data-toggle="tooltip" data-placement="left" title="保存修改"
                        class="btn btn-secondary btn-sm save_folder_btn" type="button">
                        <span class="fa fa-floppy-o"></span> 保存
                    </button>
                    <button data-toggle="tooltip" data-placement="left" title="取消修改"
                        class="btn btn-secondary btn-sm cancel_folder_btn" type="button">
                        <span class="fa fa-times"></span> 关闭
                    </button>
                </td>
            </tr>`
        );
    },

    templateFolder: function() {
        return _.template(
            `<ol class="breadcrumb">
                <li class="breadcrumb-item">
<!--                    <a title="Return to the list of libraries" href="#">Libraries</a>-->
                    <a title="返回到库列表" href="#">库</a>
                </li>
                <% _.each(path, function(path_item) { %>
                    <% if (path_item[0] != id) { %>
                        <li class="breadcrumb-item">
<!--                            <a title="Return to this folder" href="#/folders/<%- path_item[0] %>">-->
                            <a title="返回此文件夹" href="#/folders/<%- path_item[0] %>">
                                <%- path_item[1] %>
                            </a>
                        </li>
                    <% } else { %>
                        <li class="breadcrumb-item active">
<!--                            <span title="You are in this folder">-->
                            <span title="您在这个文件夹里">
                                <%- path_item[1] %>
                            </span>
                        </li>
                    <% } %>
                <% }); %>
            </ol>

            <!-- FOLDER CONTENT -->
            <table data-library-id="<%- parent_library_id  %>" class="grid table table-hover table-sm">
                <thead>
                    <th class="button_heading"></th>
                    <th class="mid" style="width: 20px;"
                        title="选中以选择所有数据集">
                        <input id="select-all-checkboxes" style="margin: 0;" type="checkbox">
                    </th>
                    <th>
                        <a class="sort-folder-name" title="点击转换排序" href="javascript:void(0)" role="button">名称</a>
                        <span title="按名称排序" class="sort-icon-name fa fa-sort-alpha-<%- order %>"></span>
                    </th>
                    <th style="width:20%;">
                        <a class="sort-folder-message" title="点击转换排序" href="javascript:void(0)" role="button">描述</a>
                        <span title="按描述排序" class="sort-icon-message fa"></span>
                    </th>
                    <th style="width:5%;">
                        <span>标签</span>
                    </th>
                    <th style="width:5%;">
                        <a class="sort-folder-file_ext" title="点击转换排序" href="javascript:void(0)" role="button">数据类型</a>
                        <span title="按类型排序" class="sort-icon-file_ext fa"></span>
                    </th>
                    <th style="width:10%;">
                        <a class="sort-folder-raw_size" title="点击转换排序" href="javascript:void(0)" role="button">大小</a>
                        <span title="按大小排序" class="sort-icon-raw_size fa"></span>
                    </th>
                    <th style="width:160px;">
                        <a class="sort-folder-update_time" title="点击转换排序" href=href="javascript:void(0)" role="button">更新日期（UTC）</a>
                        <span title="按日期排序" class="sort-icon-update_time fa"></span>
                    </th>
                    <th style="width:5%;">
                        <a class="sort-folder-state" title="点击转换排序" href="javascript:void(0)">状态</a>
                        <span title="按状态排序" class="sort-icon-state fa"></span>
                    </th>
                    <th style="width:160px;"></th>
                </thead>
                <tbody id="folder_list_body">
                    <tr id="first_folder_item">
                        <td>
                            <a href="#<% if (upper_folder_id !== 0){ print("folders/" + upper_folder_id)} %>"
                                title="回到父文件夹" class="btn_open_folder btn btn-secondary btn-sm">..<a>
                        </td>
                        <td></td>
                        <td></td>
                        <td></td>
                        <td></td>
                        <td></td>
                        <td></td>
                        <td></td>
                        <td></td>
                    </tr>
                </tbody>
            </table>
            <div class="empty-folder-message" style="display:none;">
<!--                This folder is either empty or you do not have proper access permissions to see the contents.-->
<!--                If you expected something to show up please consult the-->
<!--                <a href="https://galaxyproject.org/data-libraries/#permissions" target="_blank">-->
<!--                    library security wikipage-->
<!--                </a>.-->
                此文件夹或为空，或您没有查看内容的适当访问权限。
                如果您想显示某些内容，请联系管理员。
            </div>`
        );
    }
});

export default {
    FolderListView: FolderListView
};
