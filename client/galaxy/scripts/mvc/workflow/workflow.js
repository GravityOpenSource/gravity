/** Workflow view */
import _ from "underscore";
import $ from "jquery";
import Backbone from "backbone";
import { getAppRoot } from "onload/loadConfig";
import { getGalaxyInstance } from "app";
import { Toast } from "ui/toast";
import WORKFLOWS from "mvc/workflow/workflow-model";
import QueryStringParsing from "utils/query-string-parsing";
import _l from "utils/localization";
import LoadingIndicator from "ui/loading-indicator";
import { mountModelTags } from "components/Tags";

/** View of the individual workflows */
const WorkflowItemView = Backbone.View.extend({
    tagName: "tr", // name of (orphan) root tag in this.el
    initialize: function() {
        _.bindAll(
            this,
            "render",
            "_rowTemplate",
            "renderTagEditor",
            "_templateActions",
            "removeWorkflow",
            "copyWorkflow"
        ); // every function that uses 'this' as the current object should be in here
        Toast.options.timeOut = 1500;
    },

    events: {
        "click #show-in-tool-panel": "showInToolPanel",
        "click #delete-workflow": "removeWorkflow",
        "click #rename-workflow": "renameWorkflow",
        "click #copy-workflow": "copyWorkflow"
    },

    render: function() {
        $(this.el).html(this._rowTemplate());
        return this;
    },

    showInToolPanel: function() {
        // This reloads the whole page, so that the workflow appears in the tool panel.
        // Ideally we would notify only the tool panel of a change
        this.model.save(
            { show_in_tool_panel: !this.model.get("show_in_tool_panel") },
            {
                success: function() {
                    window.location = `${getAppRoot()}workflows/list`;
                }
            }
        );
    },

    removeWorkflow: function() {
        const wfName = this.model.get("name");
        // if (window.confirm(`Are you sure you want to delete workflow '${wfName}'?`)) {
        if (window.confirm(`您确定要删除流程:'${wfName}'?`)) {
            this.model.destroy({
                success: function() {
                  // Toast.success(`Successfully deleted workflow '${wfName}'`);
                  Toast.success(`成功删除流程:'${wfName}'`);
                }
            });
            this.remove();
        }
    },

    renameWorkflow: function() {
        const oldName = this.model.get("name");
      // const newName = window.prompt(`Enter a new Name for workflow '${oldName}'`, oldName);
      const newName = window.prompt(`输入流程'${oldName}'的新名称:`, oldName);
        if (newName) {
            this.model.save(
                { name: newName },
                {
                    success: function() {
                      // Toast.success(`Successfully renamed workflow '${oldName}' to '${newName}'`);
                      Toast.success(`修改成功, 已将流程'${oldName}'改为'${newName}'`);
                    }
                }
            );
            this.render();
        }
    },

    copyWorkflow: function() {
        const Galaxy = getGalaxyInstance();
        const oldName = this.model.get("name");
        $.getJSON(`${this.model.urlRoot}/${this.model.id}/download`, wfJson => {
            let newName = `${oldName}的副本`;
            const currentOwner = this.model.get("owner");
            if (currentOwner != Galaxy.user.attributes.username) {
              // newName += ` shared by user ${currentOwner}`;
              newName += `由用户${currentOwner}分享`;
            }
            wfJson.name = newName;
            this.collection.create(wfJson, {
                at: 0,
                wait: true,
                success: function() {
                  // Toast.success(`Successfully copied workflow '${oldName}' to '${newName}'`);
                  Toast.success(`复制成功, 已将流程'${oldName}'复制为'${newName}'`);
                },
                error: function(model, resp, options) {
                    // signature seems to have changed over the course of backbone dev
                    // see https://github.com/jashkenas/backbone/issues/2606#issuecomment-19289483
                    Toast.error(options.errorThrown);
                }
            });
        }).error((jqXHR, textStatus, errorThrown) => {
            Toast.error(jqXHR.responseJSON.err_msg);
        });
    },

    _rowTemplate: function() {
        const Galaxy = getGalaxyInstance();
        const show = this.model.get("show_in_tool_panel");
        const wfId = this.model.id;
        const checkboxHtml = `<input id="show-in-tool-panel" type="checkbox" class="show-in-tool-panel" ${
            show ? `checked="${show}"` : ""
        } value="${wfId}">`;
        return `
            <td>
                <div class="btn-group">
                    <a href="${getAppRoot()}workflow/editor?id=${this.model.id}" class="btn btn-secondary">
                        ${_.escape(this.model.get("name"))}
                    </a>
                    <button type="button" class="btn btn-secondary dropdown-toggle dropdown-toggle-split" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
<!--                      <span class="sr-only">Toggle Dropdown</span>-->
                      <span class="sr-only">展开</span>
                    </button>
                    ${this._templateActions()}
                </div>
            </td>
            <td>
                <div class="${wfId} tags-display"></div>
            </td>
            <td>
<!--                ${this.model.get("owner") === Galaxy.user.attributes.username ? "You" : this.model.get("owner")}-->
                ${this.model.get("owner") === Galaxy.user.attributes.username ? "你" : this.model.get("owner")}
            </td>
            <td>${this.model.get("number_of_steps")}</td>
<!--        <td>${this.model.get("published") ? "Yes" : "No"}</td>-->
            <td>${this.model.get("published") ? "是" : "否"}</td>
            <td>${checkboxHtml}</td>`;
    },

    renderTagEditor: function() {
        const el = $(this.el).find(".tags-display")[0];
        const propsData = {
            model: this.model,
            disabled: false,
          // context: "workflow"
          context: "流程"
        };
        return mountModelTags(propsData, el);
    },

    /** Template for user actions for workflows */
    _templateActions: function() {
        const Galaxy = getGalaxyInstance();
        if (this.model.get("owner") == Galaxy.user.attributes.username) {
            return `<div class="dropdown-menu">
                        <a class="dropdown-item" href="${getAppRoot()}workflow/editor?id=${this.model.id}">编辑</a>
                        <a class="dropdown-item" href="${getAppRoot()}workflows/run?id=${this.model.id}">运行</a>
                        <a class="dropdown-item" href="${getAppRoot()}workflow/sharing?id=${this.model.id}">分享</a>
                        <a class="dropdown-item" href="${getAppRoot()}api/workflows/${
                this.model.id
            }/download?format=json-download">下载</a>
                        <a class="dropdown-item" href="javascript:void(0)" id="copy-workflow">复制</a>
                        <a class="dropdown-item" href="javascript:void(0)" id="rename-workflow">重命名</a>
                        <a class="dropdown-item" href="${getAppRoot()}workflow/display_by_id?id=${
                this.model.id
            }">流程图</a>
                        <a class="dropdown-item" href="javascript:void(0)" id="delete-workflow">删除</a>
                    </div>`;
        } else {
            return `<div class="dropdown-menu">
                        <a class="dropdown-item" href="${getAppRoot()}workflow/display_by_username_and_slug?username=${this.model.get(
                "owner"
            )}&slug=${this.model.get("slug")}">流程图</a>
                        <a class="dropdown-item" href="${getAppRoot()}workflows/run?id=${this.model.id}">运行</a>
                        <a class="dropdown-item" href="javascript:void(0)" id="copy-workflow">复制</a>
                        <a class="dropdown-item link-confirm-shared-${
                            this.model.id
                        }" href="${getAppRoot()}workflow/sharing?unshare_me=True&id=${this.model.id}">移除</a></li>
                    </div>`;
        }
    }
});

/** View of the main workflow list page */
const WorkflowListView = Backbone.View.extend({
    title: _l("Workflows"),
    active_tab: "workflow",
    initialize: function() {
        LoadingIndicator.markViewAsLoading(this);
        _.bindAll(this, "adjustActiondropdown");
        this.collection = new WORKFLOWS.WorkflowCollection();
        this.collection.fetch().done(this.render());
        this.collection.bind("add", this.appendItem);
        this.collection.on("sync", this.render, this);
    },

    events: {
        dragover: "highlightDropZone",
        dragleave: "unhighlightDropZone"
    },

    highlightDropZone: function(ev) {
        $(".hidden_description_layer").addClass("dragover");
        $(".menubutton").addClass("background-none");
        ev.preventDefault();
    },

    unhighlightDropZone: function() {
        $(".hidden_description_layer").removeClass("dragover");
        $(".menubutton").removeClass("background-none");
    },

    drop: function(e) {
        // TODO: check that file is valid galaxy workflow
        this.unhighlightDropZone();
        e.preventDefault();
        const files = e.dataTransfer.files;
        for (let i = 0, f; (f = files[i]); i++) {
            this.readWorkflowFiles(f);
        }
    },

    readWorkflowFiles: function(f) {
        const reader = new FileReader();
        reader.onload = theFile => {
            let wf_json;
            try {
                wf_json = JSON.parse(reader.result);
            } catch (e) {
              // Toast.error(`Could not read file '${f.name}'. Verify it is a valid Galaxy workflow`);
              Toast.error(`无法读取文件: '${f.name}'; 请验证它是有效的流程`);
                wf_json = null;
            }
            if (wf_json) {
                this.collection.create(wf_json, {
                    at: 0,
                    wait: true,
                    success: function() {
                      // Toast.success(`Successfully imported workflow '${wf_json.name}'`);
                      Toast.success(`成功导入流程: '${wf_json.name}'`);
                    },
                    error: function(model, resp, options) {
                        Toast.error(options.errorThrown);
                    }
                });
            }
        };
        reader.readAsText(f, "utf-8");
    },

    _showArgErrors: _.once(() => {
        // Parse args out of params, display if there's a message.
        const msg_text = QueryStringParsing.get("message");
        const msg_status = QueryStringParsing.get("status");
        if (msg_status === "error") {
          // Toast.error(_.escape(msg_text || "Unknown Error, please report this to an administrator."));
            Toast.error(_.escape(msg_text || "未知错误，请联系管理员。"));
        } else if (msg_text) {
            Toast.info(_.escape(msg_text));
        }
    }),

    render: function() {
        // Add workflow header
        const header = this._templateHeader();
        // Add the actions buttons
        const templateActions = this._templateActionButtons();
        const tableTemplate = this._templateWorkflowTable();
        this.$el.html(header + templateActions + tableTemplate);
        _.each(this.collection.models, item => {
            // in case collection is not empty
            this.appendItem(item);
            this.confirmDelete(item);
        });
        const minQueryLength = 3;
        this.searchWorkflow(this.$(".search-wf"), this.$(".workflow-search tr"), minQueryLength);
        this.adjustActiondropdown();
        this._showArgErrors();
        this.$(".hidden_description_layer")
            .get(0)
            .addEventListener("drop", _.bind(this.drop, this));
        return this;
    },

    appendItem: function(item) {
        const workflowItemView = new WorkflowItemView({
            model: item,
            collection: this.collection
        });
        $(".workflow-search").append(workflowItemView.render().el);
        workflowItemView.renderTagEditor();
    },

    /** Add confirm box before removing/unsharing workflow */
    confirmDelete: function(workflow) {
        const $el_shared_wf_link = this.$(`.link-confirm-shared-${workflow.id}`);
        $el_shared_wf_link.click(() =>
            // window.confirm(`Are you sure you want to remove the shared workflow '${workflow.attributes.name}'?`)
            window.confirm(`您确定要删除共享流程:'${workflow.attributes.name}'?`)
        );
    },

    /** Implement client side workflow search/filtering */
    searchWorkflow: function($el_searchinput, $el_tabletr, min_querylen) {
        $el_searchinput.on("keyup", function() {
            const query = $(this).val();
            // Filter when query is at least 3 characters
            // otherwise show all rows
            if (query.length >= min_querylen) {
                // Ignore the query's case using 'i'
                const regular_expression = new RegExp(query, "i");
                $el_tabletr.hide();
                $el_tabletr
                    .filter(function() {
                        // Apply regular expression on each row's text
                        // and show when there is a match
                        return regular_expression.test($(this).text());
                    })
                    .show();
            } else {
                $el_tabletr.show();
            }
        });
    },

    /** Ajust the position of dropdown with respect to table */
    adjustActiondropdown: function() {
        $(this.el).on("show.bs.dropdown", function() {
            $(this.el).css("overflow", "inherit");
        });
        $(this.el).on("hide.bs.dropdown", function() {
            $(this.el).css("overflow", "auto");
        });
    },

    /** Template for no workflow */
    _templateNoWorkflow: function() {
      // return '<div class="wf-nodata"> You have no workflows. </div>';
      return '<div class="wf-nodata"> 没有你发布的流程。 </div>';
    },

    /** Template for actions buttons */
    _templateActionButtons: function() {
        return `<ul class="manage-table-actions"><li><input class="search-wf form-control" type="text" autocomplete="off" placeholder="搜索流程..."></li><li><a class="action-button fa fa-plus wf-action" id="new-workflow" title="创建新的流程" href="${getAppRoot()}workflows/create"></a></li><li><a class="action-button fa fa-upload wf-action" id="import-workflow" title="上传或导入流程" href="${getAppRoot()}workflows/import"></a></li></ul>`;
    },

    /** Template for workflow table */
    _templateWorkflowTable: function() {
        const tableHtml =
            '<table class="table colored"><thead>' +
            '<tr class="header">' +
            "<th>名称</th>" +
            "<th>标签</th>" +
            "<th>发布者</th>" +
            "<th>#步骤</th>" +
            "<th>发布</th>" +
            "<th>显示到工具面板</th>" +
            "</tr></thead>";
        return `${tableHtml}<tbody class="workflow-search "><div class="hidden_description_layer"><p>拖拽流程文件到此导入</p></tbody></table></div>`;
    },

    /** Main template */
    _templateHeader: function() {
        return (
            '<div class="page-container">' +
            '<div class="user-workflows wf">' +
            '<div class="response-message"></div>' +
            "<h2>" +
            _l("你发布的流程") +
            "</h2>" +
            "</div>" +
            "</div>"
        );
    }
});

export default {
    View: WorkflowListView
};
