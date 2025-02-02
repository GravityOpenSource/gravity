/** Renders the collection uploader rows */
import _l from "utils/localization";
import $ from "jquery";
import _ from "underscore";
import Backbone from "backbone";
import Utils from "utils/utils";
import UploadSettings from "mvc/upload/upload-settings";
import Popover from "mvc/ui/ui-popover";
export default Backbone.View.extend({
    /** Dictionary of upload states and associated icons */
    status_classes: {
        init: "upload-icon-button fa fa-trash-o",
        queued: "upload-icon fa fa-spinner fa-spin",
        running: "upload-icon fa fa-spinner fa-spin",
        success: "upload-icon-button fa fa-check",
        error: "upload-icon-button fa fa-exclamation-triangle"
    },

    initialize: function(app, options) {
        var self = this;
        this.app = app;
        this.model = options.model;
        this.setElement(this._template(options.model));
        this.$mode = this.$(".upload-mode");
        this.$title = this.$(".upload-title-extended");
        this.$text = this.$(".upload-text");
        this.$size = this.$(".upload-size");
        this.$info_text = this.$(".upload-info-text");
        this.$info_progress = this.$(".upload-info-progress");
        this.$text_content = this.$(".upload-text-content");
        this.$symbol = this.$(".upload-symbol");
        this.$progress_bar = this.$(".upload-progress-bar");
        this.$percentage = this.$(".upload-percentage");

        // append popup to settings icon
        this.settings = new Popover({
            title: _l("Upload configuration"),
            container: this.$(".upload-settings"),
            placement: "bottom"
        });

        // identify default genome and extension values
        // TODO: These appear unused.
        //var default_genome = this.app.select_genome.value();
        //var default_extension = this.app.select_extension.value();

        // handle click event
        this.$symbol.on("click", () => {
            self._removeRow();
        });

        // handle text editing event
        this.$text_content.on("change input", e => {
            self.model.set({
                url_paste: $(e.target).val(),
                file_size: $(e.target).val().length
            });
        });

        // model events
        this.listenTo(this.model, "change:percentage", () => {
            self._refreshPercentage();
        });
        this.listenTo(this.model, "change:status", () => {
            self._refreshStatus();
        });
        this.listenTo(this.model, "change:info", () => {
            self._refreshInfo();
        });
        this.listenTo(this.model, "change:file_size", () => {
            self._refreshFileSize();
        });
        this.listenTo(this.model, "remove", () => {
            self.remove();
        });
        this.app.collection.on("reset", () => {
            self.remove();
        });
    },

    render: function() {
        var options = this.model.attributes;
        this.$title.html(_.escape(options.file_name));
        this.$size.html(Utils.bytesToString(options.file_size));
        this.$mode
            .removeClass()
            .addClass("upload-mode")
            .addClass("text-primary");
        if (options.file_mode == "new") {
            this.$text
                .css({
                    width: `${this.$el.width() - 16}px`,
                    top: `${this.$el.height() - 8}px`
                })
                .show();
            this.$el.height(this.$el.height() - 8 + this.$text.height() + 16);
            this.$mode.addClass("fa fa-edit");
        } else if (options.file_mode == "local") {
            this.$mode.addClass("fa fa-laptop");
        } else if (options.file_mode == "ftp") {
            this.$mode.addClass("fa fa-folder-open-o");
        }
    },

    /** Refresh info text */
    _refreshInfo: function() {
        var info = this.model.get("info");
        if (info) {
            this.$info_text.html(`<strong>Failed: </strong>${info}`).show();
        } else {
            this.$info_text.hide();
        }
    },

    /** Refresh percentage status */
    _refreshPercentage: function() {
        var percentage = parseInt(this.model.get("percentage"));
        this.$progress_bar.css({ width: `${percentage}%` });
        this.$percentage.html(percentage != 100 ? `${percentage}%` : "Adding to history...");
    },

    /** Refresh status */
    _refreshStatus: function() {
        var status = this.model.get("status");
        this.$symbol
            .removeClass()
            .addClass("upload-symbol")
            .addClass(this.status_classes[status]);
        this.model.set("enabled", status == "init");
        var enabled = this.model.get("enabled");
        this.$text_content.attr("disabled", !enabled);
        if (status == "success") {
            this.$el.addClass("table-success");
            this.$percentage.html("100%");
        }
        if (status == "error") {
            this.$el.addClass("table-danger");
            this.$info_progress.hide();
        }
    },

    /** Refresh file size */
    _refreshFileSize: function() {
        this.$size.html(Utils.bytesToString(this.model.get("file_size")));
    },

    /** Remove row */
    _removeRow: function() {
        if (["init", "success", "error"].indexOf(this.model.get("status")) !== -1) {
            this.app.collection.remove(this.model);
        }
    },

    /** Attach file info popup */
    _showSettings: function() {
        this.settings.show(new UploadSettings(this).$el);
    },

    /** View template */
    _template: function(options) {
        return `<tr id="upload-row-${
            options.id
        }" class="upload-row"><td><div class="upload-text-column"><div class="upload-mode"/><div class="upload-title-extended"/><div class="upload-text"><div class="upload-text-info">通过输入URL（每行一个）或直接粘贴内容从web下载数据。</div><textarea class="upload-text-content form-control"/></div></div></td><td><div class="upload-size"/></td><td><div class="upload-info"><div class="upload-info-text"/><div class="upload-info-progress progress"><div class="upload-progress-bar progress-bar progress-bar-success"/><div class="upload-percentage">0%</div></div></div></td><td><div class="upload-symbol ${
            this.status_classes.init
        }"/></td></tr>`;
    }
});
