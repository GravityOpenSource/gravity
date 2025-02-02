import $ from "jquery";
import Utils from "utils/utils";
import _ from "underscore";

// grid view templates
export default {
    // template
    grid: function(options) {
        let tmpl;
        if (options.embedded) {
            tmpl = this.grid_header(options) + this.grid_table(options);
        } else {
            tmpl = `
                <div class="loading-elt-overlay"></div>
                <table class="grid-table">
                    <tr>
                        <td width="75%">${this.grid_header(options)}</td>
                        <td></td>
                        <td></td>
                    </tr>
                    <tr>
                        <td width="100%" id="grid-message" valign="top"></td>
                        <td></td>
                        <td></td>
                    </tr>
                </table>
                ${this.grid_table(options)}
            `;
        }

        // add info text
        if (options.info_text) {
            tmpl += `<br><div class="toolParamHelp" style="clear: both;">${options.info_text}</div>`;
        }

        // return
        return tmpl;
    },

    // template
    grid_table: function() {
        return `
            <form method="post" onsubmit="return false;">
                <table id="grid-table" class="grid">
                    <thead id="grid-table-header"></thead>
                    <tbody id="grid-table-body"></tbody>
                    <tfoot id="grid-table-footer"></tfoot>
                </table>
            </form>`;
    },

    // template
    grid_header: function(options) {
        var tmpl = '<div class="grid-header">';
        if (!options.embedded) {
            let id_str = "";
            if (options.title_id) {
                id_str += ` id="${options.title_id}"`;
            }
            tmpl += `<h2${id_str}>${options.title}</h2>`;
        }
        if (options.global_actions) {
            tmpl += '<ul class="manage-table-actions">';
            var show_popup = options.global_actions.length >= 3;
            if (show_popup) {
                tmpl +=
                    '<li><a class="action-button" id="popup-global-actions" class="menubutton">操作</a></li>' +
                    '<div popupmenu="popup-global-actions">';
            }
            for (const action of options.global_actions) {
                tmpl += `<li><a class="action-button use-target" target="${action.target}" href="${
                    action.url_args
                }" onclick="return false;" >${action.label}</a></li>`;
            }
            if (show_popup) {
                tmpl += "</div>";
            }
            tmpl += "</ul>";
        }
        if (options.insert) {
            tmpl += options.insert;
        }

        // add grid filters
        tmpl += this.grid_filters(options);
        tmpl += "</div>";

        // return template
        return tmpl;
    },

    // template
    header: function(options) {
        // start
        var tmpl = "<tr>";

        // add checkbox
        if (options.show_item_checkboxes) {
            tmpl += "<th>";
            if (options.items.length > 0) {
                tmpl +=
                    '<input type="checkbox" id="check_all" name=select_all_checkbox value="true">' +
                    '<input type="hidden" name=select_all_checkbox value="true">';
            }
            tmpl += "</th>";
        }

        // create header elements
        for (const column of options.columns) {
            if (column.visible) {
                tmpl += `<th id="${column.key}-header">`;
                if (column.sortable) {
                    tmpl += `<a href="javascript:void(0)" class="sort-link" sort_key="${column.key}">${
                        column.label
                    }</a>`;
                } else {
                    tmpl += column.label;
                }
                tmpl += `<span class="sort-arrow">${column.extra}</span></th>`;
            }
        }

        // finalize
        tmpl += "</tr>";

        // return template
        return tmpl;
    },

    // template
    body: function(options) {
        // initialize
        var tmpl = "";
        var items_length = options.items.length;

        // empty grid?
        if (items_length === 0) {
            // No results.
            // tmpl += '<tr><td colspan="100"><em>No Items</em></td></tr>';
            tmpl += '<tr><td colspan="100"><em>没有项目</em></td></tr>';
        }

        // create rows
        for (const item of options.items) {
            // Tag current
            tmpl += "<tr ";
            if (options.current_item_id == item.id) {
                tmpl += 'class="current"';
            }
            tmpl += ">";

            // Item selection column
            if (options.show_item_checkboxes) {
                tmpl += `<td style="width: 1.5em;"><input type="checkbox" name="id" value="${item.encode_id}" id="${
                    item.encode_id
                }" class="grid-row-select-checkbox" /></td>`;
            }

            // Data columns
            for (const column of options.columns) {
                if (column.visible) {
                    // Nowrap
                    var nowrap = "";
                    if (column.nowrap) {
                        nowrap = 'style="white-space:nowrap;"';
                    }

                    // get column settings
                    var column_settings = item.column_config[column.label];

                    // load attributes
                    var link = column_settings.link;
                    var value = column_settings.value;
                    var target = column_settings.target;

                    // unescape value
                    if ($.type(value) === "string") {
                        value = value.replace(/\/\//g, "/");
                    }

                    // Attach popup menu?
                    var popup_id = "";
                    if (column.attach_popup) {
                        popup_id = `grid-${item.encode_id}-popup`;
                    }

                    // Check for row wrapping
                    tmpl += `<td ${nowrap}>`;

                    // Determine cell content
                    if (column.delayed) {
                        tmpl += `<div class="delayed-value-${column.key}" data-id="${
                            item.encode_id
                        }" data-value="${value}"><span class="fa fa-spinner fa-spin"></span></div>`;
                    } else if (column.attach_popup && link) {
                        tmpl += `<div class="btn-group">
                                    <button class="btn btn-secondary use-target" target="${target}" href="${link}" onclick="return false;">${value}</button>
                                    <button id="${popup_id}" class="btn btn-secondary dropdown-toggle dropdown-toggle-split" data-toggle="dropdown"/>
                                </div>`;
                    } else if (column.attach_popup) {
                        tmpl += `<button id="${popup_id}" class="btn dropdown-toggle" data-toggle="dropdown">${value}</button>`;
                    } else if (link) {
                        tmpl += `<a class="use-target" target="${target}" href="${link}" onclick="return false;">${value}</a>`;
                    } else {
                        tmpl += `<label>${value || ""}</label>`;
                    }
                    tmpl += "</td>";
                }
            }
            tmpl += "</tr>";
        }
        return tmpl;
    },

    // template
    footer: function(options) {
        // create template string
        var tmpl = "";

        // paging
        if (options.use_paging && options.num_pages > 1) {
            // get configuration
            var num_page_links = options.num_page_links;
            var cur_page_num = options.cur_page_num;
            var num_pages = options.num_pages;

            // First pass on min page.
            var page_link_range = num_page_links / 2;
            var min_page = cur_page_num - page_link_range;
            var min_offset = 0;
            if (min_page <= 0) {
                // Min page is too low.
                min_page = 1;
                min_offset = page_link_range - (cur_page_num - min_page);
            }

            // Set max page.
            var max_range = page_link_range + min_offset;
            var max_page = cur_page_num + max_range;
            var max_offset;
            if (max_page <= num_pages) {
                // Max page is fine.
                max_offset = 0;
            } else {
                // Max page is too high.
                max_page = num_pages;
                // +1 to account for the +1 in the loop below.
                max_offset = max_range - (max_page + 1 - cur_page_num);
            }

            // Second and final pass on min page to add any unused
            // offset from max to min.
            if (max_offset !== 0) {
                min_page -= max_offset;
                if (min_page < 1) {
                    min_page = 1;
                }
            }

            // template header
            tmpl += '<tr id="page-links-row">';
            if (options.show_item_checkboxes) {
                tmpl += "<td></td>";
            }
            tmpl += '<td colspan="100">' + '<span id="page-link-container">' + "页面:";

            if (min_page > 1) {
                tmpl +=
                    '<span class="page-link-grid" id="page-link-1"><a href="javascript:void(0);" page_num="1" onclick="return false;">1</a></span> ...';
            }

            // create page urls
            for (var page_index = min_page; page_index < max_page + 1; page_index++) {
                if (page_index == options.cur_page_num) {
                    tmpl += `<span class="page-link-grid inactive-link" id="page-link-${page_index}">${page_index}</span>`;
                } else {
                    tmpl += `<span class="page-link-grid" id="page-link-${page_index}"><a href="javascript:void(0);" onclick="return false;" page_num="${page_index}">${page_index}</a></span>`;
                }
            }

            // show last page
            if (max_page < num_pages) {
                tmpl += `...<span class="page-link-grid" id="page-link-${num_pages}"><a href="javascript:void(0);" onclick="return false;" page_num="${num_pages}">${num_pages}</a></span>`;
            }
            tmpl += "</span>";

            // Show all link
            tmpl += `
                    <span class="page-link-grid" id="show-all-link-span"> | <a href="javascript:void(0);" onclick="return false;" page_num="all">显示全部</a></span>
                    </td>
                </tr>`;
        }

        // Grid operations for multiple items.
        if (options.show_item_checkboxes) {
            // start template
            tmpl += `
                <tr>
                    <input type="hidden" id="operation" name="operation" value="">
                    <td></td>
                    <td colspan="100">
                        有<span class="grid-selected-count"></span> 个选择的项目: 
            `;

            // configure buttons for operations
            for (const operation of options.operations) {
                if (operation.allow_multiple) {
                    tmpl += `<input type="button" value="${
                        operation.label
                    }" class="operation-button action-button">&nbsp;`;
                }
            }

            // finalize template
            tmpl += "</td>" + "</tr>";
        }

        // count global operations
        var found_global = false;
        for (const operation of options.operations) {
            if (operation.global_operation) {
                found_global = true;
                break;
            }
        }

        // add global operations
        if (found_global) {
            tmpl += "<tr>" + '<td colspan="100">';
            for (const operation of options.operations) {
                if (operation.global_operation) {
                    tmpl += `<a class="action-button" href="${operation.global_operation}">${operation.label}</a>`;
                }
            }
            tmpl += "</td>" + "</tr>";
        }

        // add legend
        if (options.legend) {
            tmpl += `<tr><td colspan="100">${options.legend}</td></tr>`;
        }

        // return
        return tmpl;
    },

    // template
    message: function(options) {
        var status = options.status;
        if (["success", "ok"].indexOf(status) != -1) {
            status = "done";
        }
        return `<p><div class="${status}message transient-message">${_.escape(
            options.message
        )}</div><div style="clear: both"></div></p>`;
    },

    // template
    grid_filters: function(options) {
        // get filters
        var default_filter_dict = options.default_filter_dict;
        var filters = options.filters;

        // show advanced search if flag set or if there are filters for advanced search fields
        var advanced_search_display = "none";
        if (options.advanced_search) {
            advanced_search_display = "block";
        }

        // identify columns with advanced filtering
        var show_advanced_search_link = false;
        for (const column of options.columns) {
            if (column.filterable == "advanced") {
                var column_key = column.key;
                var f_key = filters[column_key];
                var d_key = default_filter_dict[column_key];
                if (f_key && d_key && f_key != d_key) {
                    advanced_search_display = "block";
                }
                show_advanced_search_link = true;
            }
        }

        // hide standard search if advanced is shown
        var standard_search_display = "block";
        if (advanced_search_display == "block") {
            standard_search_display = "none";
        }

        //
        // standard search
        //
        var tmpl = `<div id="standard-search" style="display: ${standard_search_display};"><table><tr><td style="padding: 0;"><table>`;

        // add standard filters
        for (const column of options.columns) {
            if (column.filterable == "standard") {
                tmpl += this.grid_column_filter(options, column);
            }
        }

        // finalize standard search
        tmpl += "</table>" + "</td>" + "</tr>" + "<tr>" + "<td>";

        // show advanced search link in standard display
        if (show_advanced_search_link) {
            tmpl += '<a href="javascript:void(0)" class="advanced-search-toggle">高级搜索</a>';
        }

        // finalize standard search display
        tmpl += "</td>" + "</tr>" + "</table>" + "</div>";

        //
        // advanced search
        //
        tmpl += `<div id="advanced-search" style="display: ${advanced_search_display}; margin-top: 5px;"><table><tr><td style="text-align: left" colspan="100"><a href="javascript:void(0)" class="advanced-search-toggle">关闭高级搜索</a></td></tr>`;

        // add advanced filters
        for (const column of options.columns) {
            if (column.filterable == "advanced") {
                tmpl += this.grid_column_filter(options, column);
            }
        }

        // finalize advanced search template
        tmpl += "</table>" + "</div>";

        // return template
        return tmpl;
    },

    // template
    grid_column_filter: function(options, column) {
        // collect parameters
        var filters = options.filters;
        var column_label = column.label;
        var column_key = column.key;
        if (column.filterable == "advanced") {
            column_label = column_label.toLowerCase();
        }

        // start
        var tmpl = "<tr>";

        if (column.filterable == "advanced") {
            tmpl += `<td align="left" style="padding-left: 10px">${column_label}:</td>`;
        }
        tmpl += '<td style="padding-bottom: 1px;">';
        if (column.is_text) {
            tmpl += `<form class="text-filter-form" column_key="${column_key}" action="${options.url}" method="get" >`;
            // Carry forward filtering criteria with hidden inputs.
            for (const column of options.columns) {
                var filter_value = filters[column.key];
                if (filter_value) {
                    if (filter_value != "All") {
                        if (column.is_text) {
                            filter_value = JSON.stringify(filter_value);
                        }
                        tmpl += `<input type="hidden" id="${column.key}" name="f-${
                            column.key
                        }" value="${filter_value}"/>`;
                    }
                }
            }
            // Print current filtering criteria and links to delete.
            tmpl += `<span id="${column_key}-filtering-criteria">`;

            // add filters
            var column_filter = filters[column_key];
            if (column_filter) {
                // identify type
                var type = $.type(column_filter);

                // single filter value
                if (type == "string") {
                    if (column_filter != "All") {
                        // append template
                        tmpl += this.filter_element(column_key, column_filter);
                    }
                }

                // multiple filter values
                if (type == "array") {
                    for (const i in column_filter) {
                        // copy filters and remove entry
                        var params = column_filter;
                        params = params.slice(i);

                        // append template
                        tmpl += this.filter_element(column_key, column_filter[i]);
                    }
                }
            }

            // close span
            tmpl += "</span>";

            // Set value, size of search input field. Minimum size is 20 characters.
            var value = "";
            var size = 20;
            if (column.filterable == "standard") {
                value = column.label.toLowerCase();
                if (value.length < 20) {
                    size = value.length;
                }
                // +4 to account for space after placeholder
                size = size + 4;
            }

            // print input field for column
            tmpl += `
                <span class="search-box">
                    <input class="search-box-input" id="input-${column_key}-filter" name="f-${column_key}" type="text" placeholder="${value}" size="${size}"/>
                    <button type="submit" style="background: transparent; border: none; padding: 4px; margin: 0px;">
                        <i class="fa fa-search"></i>
                    </button>
                </span>
            </form>`;
        } else {
            // filter criteria
            tmpl += `<span id="${column_key}-filtering-criteria">`;

            // add category filters
            var seperator = false;
            for (var cf_label in options.categorical_filters[column_key]) {
                // get category filter
                var cf = options.categorical_filters[column_key][cf_label];

                // each filter will have only a single argument, so get that single argument
                var cf_key = "";
                var cf_arg = "";
                for (var key in cf) {
                    cf_key = key;
                    cf_arg = cf[key];
                }

                // add seperator
                if (seperator) {
                    tmpl += " | ";
                }
                seperator = true;

                // add category
                var filter = filters[column_key];
                if (filter && cf[column_key] && filter == cf_arg) {
                    tmpl += `<span class="categorical-filter ${column_key}-filter current-filter">${cf_label}</span>`;
                } else {
                    tmpl += `<span class="categorical-filter ${column_key}-filter"><a href="javascript:void(0);" filter_key="${cf_key}" filter_val="${cf_arg}">${cf_label}</a></span>`;
                }
            }
            tmpl += "</span>";
        }
        tmpl += "</td>" + "</tr>";

        // return template
        return tmpl;
    },

    // template for filter items
    filter_element: function(filter_key, filter_value) {
        filter_value = Utils.sanitize(filter_value);
        return `<span class="text-filter-val">${filter_value}<a href="javascript:void(0);" filter_key="${filter_key}" filter_val="${filter_value}"><i class="fa fa-times" style="padding-left: 5px; padding-bottom: 6px;"/></a></span>`;
    }
};
