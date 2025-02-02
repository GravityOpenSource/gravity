import _ from "underscore";
import $ from "jquery";
import Backbone from "backbone";
import { Toast } from "ui/toast";
import { getGalaxyInstance } from "app";

// galaxy library row view
var LibraryRowView = Backbone.View.extend({
    events: {
        "click .edit_library_btn": "edit_button_clicked",
        "click .cancel_library_btn": "cancel_library_modification",
        "click .save_library_btn": "save_library_modification",
        "click .delete_library_btn": "delete_library",
        "click .undelete_library_btn": "undelete_library"
    },

    edit_mode: false,

    element_visibility_config: {
        upload_library_btn: false,
        edit_library_btn: false,
        permission_library_btn: false,
        save_library_btn: false,
        cancel_library_btn: false,
        delete_library_btn: false,
        undelete_library_btn: false
    },

    initialize: function(library) {
        this.render(library);
    },

    render: function(library) {
        if (typeof library === "undefined") {
            const Galaxy = getGalaxyInstance();
            library = Galaxy.libraries.libraryListView.collection.get(this.$el.data("id"));
            console.log(library);
        }
        this.prepareButtons(library);
        var tmpl = this.templateRow();
        this.setElement(
            tmpl({
                library: library,
                button_config: this.element_visibility_config,
                edit_mode: this.edit_mode
            })
        );
        this.$el.show();
        return this;
    },

    repaint: function(library) {
        /* need to dispose manually because of the element removal in setElement
    invoked in render() */
        this.$el.find('[data-toggle="tooltip"]').tooltip("dispose");
        /* we need to store the old element to be able to replace it with
    new one */
        var old_element = this.$el;
        /* if user canceled the library param is undefined,
      if user saved and succeeded the updated library is rendered */
        this.render();
        old_element.replaceWith(this.$el);
        /* now we attach new tooltips to the newly created row element */
        this.$el.find('[data-toggle="tooltip"]').tooltip({ trigger: "hover" });
    },

    /**
     * Function modifies the visibility of buttons for
     * the filling of the row template of given library.
     */
    prepareButtons: function(library) {
        var vis_config = this.element_visibility_config;

        if (this.edit_mode === false) {
            vis_config.save_library_btn = false;
            vis_config.cancel_library_btn = false;
            vis_config.delete_library_btn = false;
            if (library.get("deleted") === true) {
                vis_config.undelete_library_btn = true;
                vis_config.upload_library_btn = false;
                vis_config.edit_library_btn = false;
                vis_config.permission_library_btn = false;
            } else if (library.get("deleted") === false) {
                vis_config.save_library_btn = false;
                vis_config.cancel_library_btn = false;
                vis_config.undelete_library_btn = false;
                if (library.get("can_user_add") === true) {
                    vis_config.upload_library_btn = true;
                }
                if (library.get("can_user_modify") === true) {
                    vis_config.edit_library_btn = true;
                }
                if (library.get("can_user_manage") === true) {
                    vis_config.permission_library_btn = true;
                }
            }
        } else if (this.edit_mode === true) {
            vis_config.upload_library_btn = false;
            vis_config.edit_library_btn = false;
            vis_config.permission_library_btn = false;
            vis_config.save_library_btn = true;
            vis_config.cancel_library_btn = true;
            vis_config.delete_library_btn = true;
            vis_config.undelete_library_btn = false;
        }

        this.element_visibility_config = vis_config;
    },

    /* User clicked the 'edit' button on row so we render a new row
    that allows editing */
    edit_button_clicked: function() {
        this.edit_mode = true;
        this.repaint();
    },

    /* User clicked the 'cancel' button so we render normal rowView */
    cancel_library_modification: function() {
        // Toast.info('Modifications canceled');
        this.edit_mode = false;
        this.repaint();
    },

    save_library_modification: function() {
        const Galaxy = getGalaxyInstance();
        var library = Galaxy.libraries.libraryListView.collection.get(this.$el.data("id"));
        var is_changed = false;

        var new_name = this.$el.find(".input_library_name").val();
        if (typeof new_name !== "undefined" && new_name !== library.get("name")) {
            if (new_name.length > 2) {
                library.set("name", new_name);
                is_changed = true;
            } else {
                // Toast.warning("Library name has to be at least 3 characters long.");
                Toast.warning("库的名称必须至少有3个字符");
                return;
            }
        }

        var new_description = this.$el.find(".input_library_description").val();
        if (typeof new_description !== "undefined" && new_description !== library.get("description")) {
            library.set("description", new_description);
            is_changed = true;
        }

        var new_synopsis = this.$el.find(".input_library_synopsis").val();
        if (typeof new_synopsis !== "undefined" && new_synopsis !== library.get("synopsis")) {
            library.set("synopsis", new_synopsis);
            is_changed = true;
        }

        if (is_changed) {
            var row_view = this;
            library.save(null, {
                patch: true,
                success: function(library) {
                    row_view.edit_mode = false;
                    row_view.repaint(library);
                    // Toast.success("Changes to library saved.");
                    Toast.success("已保存对库的修改。");
                },
                error: function(model, response) {
                    if (typeof response.responseJSON !== "undefined") {
                        Toast.error(response.responseJSON.err_msg);
                    } else {
                        // Toast.error("An error occurred while attempting to update the library.");
                        Toast.error("尝试更新库时出错。");
                    }
                }
            });
        } else {
            this.edit_mode = false;
            this.repaint(library);
            // Toast.info("Nothing has changed.");
            Toast.info("什么也没有修改。");
        }
    },

    delete_library: function() {
        const Galaxy = getGalaxyInstance();
        var library = Galaxy.libraries.libraryListView.collection.get(this.$el.data("id"));
        var row_view = this;
        // mark the library deleted
        library.destroy({
            success: function(library) {
                library.set("deleted", true);
                // add the new deleted library back to the collection (Galaxy specialty)
                Galaxy.libraries.libraryListView.collection.add(library);
                row_view.edit_mode = false;
                if (Galaxy.libraries.preferences.get("with_deleted") === false) {
                    $(".tooltip").hide();
                    row_view.repaint(library);
                    row_view.$el.remove();
                } else if (Galaxy.libraries.preferences.get("with_deleted") === true) {
                    row_view.repaint(library);
                }
                // Toast.success("Library has been marked deleted.");
                Toast.success("库已标记为已删除。");
            },
            error: function(model, response) {
                if (typeof response.responseJSON !== "undefined") {
                    Toast.error(response.responseJSON.err_msg);
                } else {
                    // Toast.error("An error occurred during deleting the library.");
                    Toast.error("删除库时出错。");
                }
            }
        });
    },

    undelete_library: function() {
        const Galaxy = getGalaxyInstance();
        var library = Galaxy.libraries.libraryListView.collection.get(this.$el.data("id"));
        var row_view = this;

        // mark the library undeleted
        library.url = `${library.urlRoot + library.id}?undelete=true`;
        library.destroy({
            success: function(library) {
                // add the newly undeleted library back to the collection
                // backbone does not accept changes through destroy, so update it too
                library.set("deleted", false);
                Galaxy.libraries.libraryListView.collection.add(library);
                row_view.edit_mode = false;
                row_view.repaint(library);
                // Toast.success("Library has been undeleted.");
                Toast.success("库已被取消删除。");
            },
            error: function(model, response) {
                if (typeof response.responseJSON !== "undefined") {
                    Toast.error(response.responseJSON.err_msg);
                } else {
                    // Toast.error("An error occurred while undeleting the library.");
                    Toast.error("删除库时出错。");
                }
            }
        });
    },

    templateRow: function() {
        return _.template(
            `<tr class="<% if(library.get("deleted") === true) { print("active") } %>"
                style="display:none;" data-id="<%- library.get("id") %>">
                <% if(!edit_mode) { %>
                    <% if(library.get("deleted")) { %>
                        <td style="color:grey;"><%- library.get("name") %></td>
                    <% } else { %>
                        <td>
                            <a href="#folders/<%- library.get("root_folder_id") %>"><%- library.get("name") %></a>
                        </td>
                    <% } %>
                    <% if(library.get("description")) { %>
                        <% if( (library.get("description")).length> 80 ) { %>
                            <td data-toggle="tooltip" data-placement="bottom"
                                title="<%= _.escape(library.get("description")) %>">
                                <%= _.escape(library.get("description")).substring(0, 80) + "..." %>
                            </td>
                        <% } else { %>
                            <td><%= _.escape(library.get("description"))%></td>
                        <% } %>
                    <% } else { %>
                        <td></td>
                    <% } %>
                    <% if(library.get("synopsis")) { %>
                        <% if( (library.get("synopsis")).length> 120 ) { %>
                            <td data-toggle="tooltip" data-placement="bottom"
                                title="<%= _.escape(library.get("synopsis")) %>">
                                <%= _.escape(library.get("synopsis")).substring(0, 120) + "..." %>
                            </td>
                        <% } else { %>
                            <td><%= _.escape(library.get("synopsis"))%></td>
                        <% } %>
                    <% } else { %>
                        <td></td>
                    <% } %>
                <% } else if(edit_mode){ %>
                    <td>
<!--                        <textarea rows="4" class="form-control input_library_name" placeholder="name" ><%- library.get("name") %></textarea>-->
                        <textarea rows="4" class="form-control input_library_name" placeholder="名称" ><%- library.get("name") %></textarea>
                    </td>
                    <td>
<!--                        <textarea rows="4" class="form-control input_library_description" placeholder="description"><%- library.get("description") %></textarea>-->
                        <textarea rows="4" class="form-control input_library_description" placeholder="描述"><%- library.get("description") %></textarea>
                    </td>
                    <td>
<!--                        <textarea rows="4" class="form-control input_library_synopsis" placeholder="synopsis"><%- library.get("synopsis") %></textarea>-->
                        <textarea rows="4" class="form-control input_library_synopsis" placeholder="简介"><%- library.get("synopsis") %></textarea>
                    </td>
                <% } %>
                <td class="right-center">
                    <% if( (library.get("public")) && (library.get("deleted") === false) ) { %>
                        <span data-toggle="tooltip" data-placement="left" title="无限制的库"
                            class="fa fa-globe fa-lg"></span>
                    <% }%>
                    <button data-toggle="tooltip" data-placement="left" title="修改 '<%- library.get("name") %>'"
                        class="btn btn-secondary btn-sm edit_library_btn" type="button"
                        style="<% if(button_config.edit_library_btn === false) { print("display:none;") } %>">
                        <span class="fa fa-pencil"></span> 编辑
                    </button>
                    <a data-toggle="tooltip" data-placement="left"
                        title="'<%- library.get("name") %>'的权限"
                        href="#library/<%- library.get("id") %>/permissions">
                        <button class="btn btn-secondary btn-sm permission_library_btn" type="button"
                            style="<% if(button_config.permission_library_btn === false) { print("display:none;") } %>">
                            <span class="fa fa-group"></span> 管理
                        </button>
                    </a>
                    <button data-toggle="tooltip" data-placement="left" title="保存修改"
                        class="btn btn-secondary btn-sm save_library_btn" type="button"
                        style="<% if(button_config.save_library_btn === false) { print("display:none;") } %>">
                        <span class="fa fa-floppy-o"></span> 保存
                    </button>
                    <button data-toggle="tooltip" data-placement="left" title="取消修改"
                        class="btn btn-secondary btn-sm cancel_library_btn" type="button"
                        style="<% if(button_config.cancel_library_btn === false) { print("display:none;") } %>">
                        <span class="fa fa-times"></span> 取消
                    </button>
                    <button data-toggle="tooltip" data-placement="left" title="删除 '<%- library.get("name") %>'"
                        class="btn btn-secondary btn-sm delete_library_btn" type="button"
                        style="<% if(button_config.delete_library_btn === false) { print("display:none;") } %>">
                        <span class="fa fa-trash-o"></span> 删除
                    </button>
                    <!-- For deleted libraries -->
                    <span data-toggle="tooltip" data-placement="left" title="标记删除"
                        style="color:grey; <% if(button_config.undelete_library_btn === false) { print("display:none;") } %>"
                        class="fa fa-ban fa-lg">
                    </span>
                    <button data-toggle="tooltip" data-placement="left" title="撤消删除 '<%- library.get("name") %>' "
                        class="btn btn-secondary btn-sm undelete_library_btn" type="button"
                        style="<% if(button_config.undelete_library_btn === false) { print("display:none;") } %>">
                        <span class="fa fa-unlock"></span> 撤消删除
                    </button>
                </td>
            </tr>`
        );
    }
});

export default {
    LibraryRowView: LibraryRowView
};
