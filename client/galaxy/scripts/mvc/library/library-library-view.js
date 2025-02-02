import _ from "underscore";
import $ from "jquery";
import Backbone from "backbone";
import { getAppRoot } from "onload/loadConfig";
import { getGalaxyInstance } from "app";
import { Toast } from "ui/toast";
import mod_library_model from "mvc/library/library-model";
import mod_select from "mvc/ui/ui-select";

var LibraryView = Backbone.View.extend({
    el: "#center",

    model: null,

    options: {},

    events: {
        "click .toolbtn_save_permissions": "savePermissions"
    },

    initialize: function(options) {
        this.options = _.extend(this.options, options);
        if (this.options.id) {
            this.fetchLibrary();
        }
    },

    fetchLibrary: function(options) {
        this.options = _.extend(this.options, options);
        this.model = new mod_library_model.Library({
            id: this.options.id
        });
        var that = this;
        this.model.fetch({
            success: function() {
                if (that.options.show_permissions) {
                    that.showPermissions();
                }
            },
            error: function(model, response) {
                const Galaxy = getGalaxyInstance();
                if (typeof response.responseJSON !== "undefined") {
                    // Toast.error(`${response.responseJSON.err_msg} Click this to go back.`, "", {
                    Toast.error(`${response.responseJSON.err_msg} 单击此处返回`, "", {
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

    showPermissions: function(options) {
        this.options = _.extend(this.options, options);
        $(".tooltip").remove();

        if (this.options.fetched_permissions !== undefined) {
            if (this.options.fetched_permissions.access_library_role_list.length === 0) {
                this.model.set({ is_unrestricted: true });
            } else {
                this.model.set({ is_unrestricted: false });
            }
        }
        var is_admin = false;
        const Galaxy = getGalaxyInstance();
        if (Galaxy.user) {
            is_admin = Galaxy.user.isAdmin();
        }
        var template = this.templateLibraryPermissions();
        this.$el.html(template({ library: this.model, is_admin: is_admin }));

        var self = this;
        $.get(`${getAppRoot()}api/libraries/${self.id}/permissions?scope=current`)
            .done(fetched_permissions => {
                self.prepareSelectBoxes({
                    fetched_permissions: fetched_permissions
                });
            })
            .fail(() => {
                // Toast.error("An error occurred while attempting to fetch library permissions.");
                Toast.error("试图获取库权限时出错。");
            });

        $('#center [data-toggle="tooltip"]').tooltip({ trigger: "hover" });
        //hack to show scrollbars
        $("#center").css("overflow", "auto");
    },

    _serializeRoles: function(role_list) {
        var selected_roles = [];
        for (var i = 0; i < role_list.length; i++) {
            selected_roles.push(`${role_list[i][1]}:${role_list[i][0]}`);
        }
        return selected_roles;
    },

    prepareSelectBoxes: function(options) {
        this.options = _.extend(this.options, options);
        var fetched_permissions = this.options.fetched_permissions;
        var self = this;

        var selected_access_library_roles = this._serializeRoles(fetched_permissions.access_library_role_list);
        var selected_add_item_roles = this._serializeRoles(fetched_permissions.add_library_item_role_list);
        var selected_manage_library_roles = this._serializeRoles(fetched_permissions.manage_library_role_list);
        var selected_modify_library_roles = this._serializeRoles(fetched_permissions.modify_library_role_list);

        self.accessSelectObject = new mod_select.View(
            this._createSelectOptions(this, "access_perm", selected_access_library_roles, true)
        );
        self.addSelectObject = new mod_select.View(
            this._createSelectOptions(this, "add_perm", selected_add_item_roles, false)
        );
        self.manageSelectObject = new mod_select.View(
            this._createSelectOptions(this, "manage_perm", selected_manage_library_roles, false)
        );
        self.modifySelectObject = new mod_select.View(
            this._createSelectOptions(this, "modify_perm", selected_modify_library_roles, false)
        );
    },

    _createSelectOptions: function(self, id, init_data, is_library_access) {
        is_library_access = is_library_access === true ? is_library_access : false;
        var select_options = {
            minimumInputLength: 0,
            css: id,
            multiple: true,
            placeholder: "单击此选择一个角色",
            container: self.$el.find(`#${id}`),
            ajax: {
                url: `${getAppRoot()}api/libraries/${
                    self.id
                }/permissions?scope=available&is_library_access=${is_library_access}`,
                dataType: "json",
                quietMillis: 100,
                data: function(term, page) {
                    // page is the one-based page number tracked by Select2
                    return {
                        q: term, //search term
                        page_limit: 10, // page size
                        page: page // page number
                    };
                },
                results: function(data, page) {
                    var more = page * 10 < data.total; // whether or not there are more results available
                    // notice we return the value of more so Select2 knows if more results can be loaded
                    return { results: data.roles, more: more };
                }
            },
            formatResult: function roleFormatResult(role) {
                return `${role.name} type: ${role.type}`;
            },

            formatSelection: function roleFormatSelection(role) {
                return role.name;
            },
            initSelection: function(element, callback) {
                // the input tag has a value attribute preloaded that points to a preselected role's id
                // this function resolves that id attribute to an object that select2 can render
                // using its formatResult renderer - that way the role name is shown preselected
                var data = [];
                $(element.val().split(",")).each(function() {
                    var item = this.split(":");
                    data.push({
                        id: item[0],
                        name: item[1]
                    });
                });
                callback(data);
            },
            // initialData: init_data.join(','),
            initialData: init_data,
            dropdownCssClass: "bigdrop" // apply css that makes the dropdown taller
        };

        return select_options;
    },

    makeDatasetPrivate: function() {
        var self = this;
        $.post(`${getAppRoot()}api/libraries/datasets/${self.id}/permissions?action=make_private`)
            .done(fetched_permissions => {
                self.model.set({ is_unrestricted: false });
                self.showPermissions({
                    fetched_permissions: fetched_permissions
                });
                // Toast.success("The dataset is now private to you.");
                Toast.success("数据集现在对您是私有的。");
            })
            .fail(() => {
                // Toast.error("An error occurred while attempting to make dataset private.");
                Toast.error("试图将数据集设为私有时出错。");
            });
    },

    removeDatasetRestrictions: function() {
        var self = this;
        $.post(`${getAppRoot()}api/libraries/datasets/${self.id}/permissions?action=remove_restrictions`)
            .done(fetched_permissions => {
                self.model.set({ is_unrestricted: true });
                self.showPermissions({
                    fetched_permissions: fetched_permissions
                });
                // Toast.success("Access to this dataset is now unrestricted.");
                Toast.success("现在对此数据集的访问不受限制。");
            })
            .fail(() => {
                // Toast.error("An error occurred while attempting to make dataset unrestricted.");
                Toast.error("试图将数据集设为不受限时出错。");
            });
    },

    _extractIds: function(roles_list) {
        var ids_list = [];
        for (var i = roles_list.length - 1; i >= 0; i--) {
            ids_list.push(roles_list[i].id);
        }
        return ids_list;
    },
    savePermissions: function(event) {
        var self = this;

        var access_ids = this._extractIds(this.accessSelectObject.$el.select2("data"));
        var add_ids = this._extractIds(this.addSelectObject.$el.select2("data"));
        var manage_ids = this._extractIds(this.manageSelectObject.$el.select2("data"));
        var modify_ids = this._extractIds(this.modifySelectObject.$el.select2("data"));

        $.post(`${getAppRoot()}api/libraries/${self.id}/permissions?action=set_permissions`, {
            "access_ids[]": access_ids,
            "add_ids[]": add_ids,
            "manage_ids[]": manage_ids,
            "modify_ids[]": modify_ids
        })
            .done(fetched_permissions => {
                //fetch dataset again
                self.showPermissions({
                    fetched_permissions: fetched_permissions
                });
                // Toast.success("Permissions saved.");
                Toast.success("权限已保存。");
            })
            .fail(() => {
                // Toast.error("An error occurred while attempting to set library permissions.");
                Toast.error("试图设置库权限时出错。");
            });
    },

    templateLibraryPermissions: function() {
        return _.template(
            `<div class="library_style_container">
                <div>
                    <a href="#">
                        <button data-toggle="tooltip" data-placement="top"
                            title="返回到库列表" class="btn btn-secondary primary-button" type="button">
                            <span class="fa fa-list"></span>&nbsp;库
                        </button>
                    </a>
                </div>
                <h1>
                    库: <%= _.escape(library.get("name")) %>
                </h1>
                <div class="alert alert-warning">
                    <% if (is_admin) { %>
<!--                        You are logged in as an <strong>administrator</strong> therefore you can manage any library-->
<!--                        on this Galaxy instance. Please make sure you understand the consequences.-->
                        您是以<strong>管理员</strong>身份登录的，因此可以管理这个系统上的任何库。请务必了解后果。
                    <% } else { %>
<!--                        You can assign any number of roles to any of the following permission types.-->
<!--                        However please read carefully the implications of such actions.-->
                        您可以将任意数量的角色分配给以下任何权限类型。
                        不过，请仔细阅读这些操作的含义。
                    <% }%>
                </div>
                <div class="dataset_table">
<!--                    <h2>Library permissions</h2>-->
                    <h2>库的权限</h2>
<!--                    <h4>Roles that can access the library</h4>-->
                    <h4>可以访问库的角色</h4>
                    <div id="access_perm" class="access_perm roles-selection"></div>
<!--                    <div class="alert alert-info roles-selection">-->
<!--                        User with <strong>any</strong> of these roles can access this library.-->
<!--                        If there are no access roles set on the library it is considered <strong>unrestricted</strong>.-->
                        具有<strong>任一</strong>这些角色的用户都可以访问这个库。
                        如果在库上没有设置访问角色，则认为是<strong>不受限制</strong>的。
                    </div>
<!--                    <h4>Roles that can manage permissions on this library</h4>-->
                    <h4>可以管理此库权限的角色</h4>
                    <div id="manage_perm" class="manage_perm roles-selection"></div>
                    <div class="alert alert-info roles-selection">
<!--                        User with <strong>any</strong> of these roles can manage permissions on this library-->
<!--                        (includes giving access).-->
                        具有<strong>任一</strong>这些角色的用户都可以管理这个库的权限(包括授予访问权)。
                    </div>
<!--                    <h4>Roles that can add items to this library</h4>-->
                    <h4>可以向此库添加项的角色</h4>
                    <div id="add_perm" class="add_perm roles-selection"></div>
                    <div class="alert alert-info roles-selection">
<!--                        User with <strong>any</strong> of these roles can add items to this library (folders and datasets).-->
                        具有<strong>任一</strong>这些角色的用户都可以将项添加到此库(文件夹和数据集)。
                    </div>
<!--                    <h4>Roles that can modify this library</h4>-->
                    <h4>可以修改此库的角色</h4>
                    <div id="modify_perm" class="modify_perm roles-selection"></div>
                    <div class="alert alert-info roles-selection">
<!--                        User with <strong>any</strong> of these roles can modify this library (name, synopsis, etc.).-->
                        具有<strong>任一</strong>这些角色的用户都可以修改这个库(名称、概要等)。
                    </div>
                    <button data-toggle="tooltip" data-placement="top"
                        title="保存在本页上所作的修改"
                        class="btn btn-secondary toolbtn_save_permissions primary-button" type="button">
                        <span class="fa fa-floppy-o"></span>&nbsp;保存
                    </button>
                </div>
            </div>`
        );
    }
});

export default {
    LibraryView: LibraryView
};
