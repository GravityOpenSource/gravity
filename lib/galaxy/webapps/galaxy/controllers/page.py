
from markupsafe import escape
from sqlalchemy import (
    and_,
    desc,
    false,
    true
)
from sqlalchemy.orm import (
    eagerload,
    undefer
)

from galaxy import (
    exceptions,
    model,
    util,
    web
)
from galaxy.managers.hdas import HDAManager
from galaxy.managers.histories import HistoryManager, HistorySerializer
from galaxy.managers.pages import (
    get_page_identifiers,
    PageContentProcessor,
    PageManager,
)
from galaxy.model.item_attrs import UsesItemRatings
from galaxy.util import unicodify
from galaxy.util.sanitize_html import sanitize_html
from galaxy.web import (
    error,
    url_for
)
from galaxy.web.framework.helpers import (
    grids,
    time_ago
)
from galaxy.webapps.base.controller import (
    BaseUIController,
    SharableMixin,
    UsesStoredWorkflowMixin,
    UsesVisualizationMixin
)


def format_bool(b):
    if b:
        return "yes"
    else:
        return ""


class PageListGrid(grids.Grid):
    # Custom column.
    class URLColumn(grids.PublicURLColumn):
        def get_value(self, trans, grid, item):
            return url_for(controller='page', action='display_by_username_and_slug', username=item.user.username, slug=item.slug)

    # Grid definition
    use_panels = True
#     title = "Pages"
    title = "页面"
    model_class = model.Page
    default_filter = {"published": "All", "tags": "All", "title": "All", "sharing": "All"}
    default_sort_key = "-update_time"
    columns = [
        grids.TextColumn("标题", key="title", attach_popup=True, filterable="advanced", link=(lambda item: dict(action="display_by_username_and_slug", username=item.user.username, slug=item.slug))),
#         URLColumn("Public URL"),
        URLColumn("公共的URL"),
        grids.OwnerAnnotationColumn("注释", key="annotation", model_annotation_association_class=model.PageAnnotationAssociation, filterable="advanced"),
        grids.IndividualTagsColumn("标签", key="tags", model_tag_association_class=model.PageTagAssociation, filterable="advanced", grid_name="PageListGrid"),
        grids.SharingStatusColumn("分享", key="sharing", filterable="advanced", sortable=False),
        grids.GridColumn("创建时间", key="create_time", format=time_ago),
        grids.GridColumn("最后更新时间", key="update_time", format=time_ago),
    ]
    columns.append(grids.MulticolFilterColumn(
        "搜索",
        cols_to_filter=[columns[0], columns[2]],
        key="free-text-search", visible=False, filterable="standard"))
    global_actions = [
        grids.GridAction("添加新页面", dict(controller="", action="pages/create"))
    ]
    operations = [
        grids.DisplayByUsernameAndSlugGridOperation("视图", allow_multiple=False),
        grids.GridOperation("编辑内容", allow_multiple=False, url_args=dict(action="edit_content")),
        grids.GridOperation("编辑属性", allow_multiple=False, url_args=dict(controller="", action="pages/edit")),
        grids.GridOperation("分享或发布", allow_multiple=False, condition=(lambda item: not item.deleted), url_args=dict(controller="", action="pages/sharing")),
        grids.GridOperation("删除", confirm="您确定要删除此页面吗?"),
    ]

    def apply_query_filter(self, trans, query, **kwargs):
        return query.filter_by(user=trans.user, deleted=False)


class PageAllPublishedGrid(grids.Grid):
    # Grid definition
    use_panels = True
#     title = "Published Pages"
    title = "已发布的页面"
    model_class = model.Page
    default_sort_key = "update_time"
    default_filter = dict(title="All", username="All")
    columns = [
        grids.PublicURLColumn("标题", key="title", filterable="advanced"),
        grids.OwnerAnnotationColumn("注释", key="annotation", model_annotation_association_class=model.PageAnnotationAssociation, filterable="advanced"),
        grids.OwnerColumn("作者", key="username", model_class=model.User, filterable="advanced"),
        grids.CommunityRatingColumn("社区评价", key="rating"),
        grids.CommunityTagsColumn("社区标签", key="tags", model_tag_association_class=model.PageTagAssociation, filterable="advanced", grid_name="PageAllPublishedGrid"),
        grids.ReverseSortColumn("最后更新时间", key="update_time", format=time_ago)
    ]
    columns.append(
        grids.MulticolFilterColumn(
#             "Search title, annotation, owner, and tags",
            "搜索标题、注释、作者和标签",
            cols_to_filter=[columns[0], columns[1], columns[2], columns[4]],
            key="free-text-search", visible=False, filterable="standard")
    )

    def build_initial_query(self, trans, **kwargs):
        # See optimization description comments and TODO for tags in matching public histories query.
        return trans.sa_session.query(self.model_class).join("user").options(eagerload("user").load_only("username"), eagerload("annotations"), undefer("average_rating"))

    def apply_query_filter(self, trans, query, **kwargs):
        return query.filter(self.model_class.deleted == false()).filter(self.model_class.published == true())


class ItemSelectionGrid(grids.Grid):
    """ Base class for pages' item selection grids. """
    # Custom columns.
    class NameColumn(grids.TextColumn):
        def get_value(self, trans, grid, item):
            if hasattr(item, "get_display_name"):
                return escape(item.get_display_name())
            else:
                return escape(item.name)

    # Grid definition.
    show_item_checkboxes = True
    default_filter = {"deleted": "False", "sharing": "All"}
    default_sort_key = "-update_time"
    use_paging = True
    num_rows_per_page = 10

    def apply_query_filter(self, trans, query, **kwargs):
        return query.filter_by(user=trans.user)


class HistorySelectionGrid(ItemSelectionGrid):
    """ Grid for selecting histories. """
    # Grid definition.
#     title = "Saved Histories"
    title = "保存的历史"
    model_class = model.History
    columns = [
        ItemSelectionGrid.NameColumn("名称", key="name", filterable="advanced"),
        grids.IndividualTagsColumn("标签", key="tags", model_tag_association_class=model.HistoryTagAssociation, filterable="advanced"),
        grids.GridColumn("最后更新时间", key="update_time", format=time_ago),
        # Columns that are valid for filtering but are not visible.
        grids.DeletedColumn("删除", key="deleted", visible=False, filterable="advanced"),
        grids.SharingStatusColumn("分享", key="sharing", filterable="advanced", sortable=False, visible=False),
    ]
    columns.append(
        grids.MulticolFilterColumn(
            "搜索",
            cols_to_filter=[columns[0], columns[1]],
            key="free-text-search", visible=False, filterable="standard")
    )

    def apply_query_filter(self, trans, query, **kwargs):
        return query.filter_by(user=trans.user, purged=False)


class HistoryDatasetAssociationSelectionGrid(ItemSelectionGrid):
    """ Grid for selecting HDAs. """
    # Grid definition.
#     title = "Saved Datasets"
    title = "保存的数据集"
    model_class = model.HistoryDatasetAssociation
    columns = [
        ItemSelectionGrid.NameColumn("名称", key="name", filterable="advanced"),
        grids.IndividualTagsColumn("标签", key="tags", model_tag_association_class=model.HistoryDatasetAssociationTagAssociation, filterable="advanced"),
        grids.GridColumn("做后更新时间", key="update_time", format=time_ago),
        # Columns that are valid for filtering but are not visible.
        grids.DeletedColumn("删除", key="deleted", visible=False, filterable="advanced"),
        grids.SharingStatusColumn("分享", key="sharing", filterable="advanced", sortable=False, visible=False),
    ]
    columns.append(
        grids.MulticolFilterColumn(
            "搜索",
            cols_to_filter=[columns[0], columns[1]],
            key="free-text-search", visible=False, filterable="standard")
    )

    def apply_query_filter(self, trans, query, **kwargs):
        # To filter HDAs by user, need to join HDA and History table and then filter histories by user. This is necessary because HDAs do not have
        # a user relation.
        return query.select_from(model.HistoryDatasetAssociation.table.join(model.History.table)).filter(model.History.user == trans.user)


class WorkflowSelectionGrid(ItemSelectionGrid):
    """ Grid for selecting workflows. """
    # Grid definition.
#     title = "Saved Workflows"
    title = "保存的流程"
    model_class = model.StoredWorkflow
    columns = [
        ItemSelectionGrid.NameColumn("名称", key="name", filterable="advanced"),
        grids.IndividualTagsColumn("标签", key="tags", model_tag_association_class=model.StoredWorkflowTagAssociation, filterable="advanced"),
        grids.GridColumn("最后更新时间", key="update_time", format=time_ago),
        # Columns that are valid for filtering but are not visible.
        grids.DeletedColumn("删除", key="deleted", visible=False, filterable="advanced"),
        grids.SharingStatusColumn("分享", key="sharing", filterable="advanced", sortable=False, visible=False),
    ]
    columns.append(
        grids.MulticolFilterColumn(
            "搜索",
            cols_to_filter=[columns[0], columns[1]],
            key="free-text-search", visible=False, filterable="standard")
    )


class PageSelectionGrid(ItemSelectionGrid):
    """ Grid for selecting pages. """
    # Grid definition.
#     title = "Saved Pages"
    title = "保存的页面"
    model_class = model.Page
    columns = [
        grids.TextColumn("标题", key="title", filterable="advanced"),
        grids.IndividualTagsColumn("标签", key="tags", model_tag_association_class=model.PageTagAssociation, filterable="advanced"),
        grids.GridColumn("最后更新时间", key="update_time", format=time_ago),
        # Columns that are valid for filtering but are not visible.
        grids.DeletedColumn("删除", key="deleted", visible=False, filterable="advanced"),
        grids.SharingStatusColumn("分享", key="sharing", filterable="advanced", sortable=False, visible=False),
    ]
    columns.append(
        grids.MulticolFilterColumn(
            "搜索",
            cols_to_filter=[columns[0], columns[1]],
            key="free-text-search", visible=False, filterable="standard")
    )


class VisualizationSelectionGrid(ItemSelectionGrid):
    """ Grid for selecting visualizations. """
    # Grid definition.
#     title = "Saved Visualizations"
    title = "保存的可视化"
    model_class = model.Visualization
    columns = [
        grids.TextColumn("标题", key="title", filterable="advanced"),
        grids.TextColumn("类型", key="type"),
        grids.IndividualTagsColumn("标签", key="tags", model_tag_association_class=model.VisualizationTagAssociation, filterable="advanced", grid_name="VisualizationListGrid"),
        grids.SharingStatusColumn("分享", key="sharing", filterable="advanced", sortable=False),
        grids.GridColumn("最后更新时间", key="update_time", format=time_ago),
    ]
    columns.append(
        grids.MulticolFilterColumn(
            "搜索",
            cols_to_filter=[columns[0], columns[2]],
            key="free-text-search", visible=False, filterable="standard")
    )


# Adapted from the _BaseHTMLProcessor class of https://github.com/kurtmckee/feedparser
class PageController(BaseUIController, SharableMixin,
                     UsesStoredWorkflowMixin, UsesVisualizationMixin, UsesItemRatings):

    _page_list = PageListGrid()
    _all_published_list = PageAllPublishedGrid()
    _history_selection_grid = HistorySelectionGrid()
    _workflow_selection_grid = WorkflowSelectionGrid()
    _datasets_selection_grid = HistoryDatasetAssociationSelectionGrid()
    _page_selection_grid = PageSelectionGrid()
    _visualization_selection_grid = VisualizationSelectionGrid()

    def __init__(self, app):
        super(PageController, self).__init__(app)
        self.page_manager = PageManager(app)
        self.history_manager = HistoryManager(app)
        self.history_serializer = HistorySerializer(self.app)
        self.hda_manager = HDAManager(app)

    @web.expose
    @web.json
    @web.require_login()
    def list(self, trans, *args, **kwargs):
        """ List user's pages. """
        # Handle operation
        if 'operation' in kwargs and 'id' in kwargs:
            session = trans.sa_session
            operation = kwargs['operation'].lower()
            ids = util.listify(kwargs['id'])
            for id in ids:
                item = session.query(model.Page).get(self.decode_id(id))
                if operation == "delete":
                    item.deleted = True
            session.flush()

        # Build grid dictionary.
        grid = self._page_list(trans, *args, **kwargs)
        grid['shared_by_others'] = self._get_shared(trans)
        return grid

    @web.expose
    @web.json
    def list_published(self, trans, *args, **kwargs):
        grid = self._all_published_list(trans, *args, **kwargs)
        grid['shared_by_others'] = self._get_shared(trans)
        return grid

    def _get_shared(self, trans):
        """Identify shared pages"""
        shared_by_others = trans.sa_session \
            .query(model.PageUserShareAssociation) \
            .filter_by(user=trans.get_user()) \
            .join(model.Page.table) \
            .filter(model.Page.deleted == false()) \
            .order_by(desc(model.Page.update_time)) \
            .all()
        return [{'username' : p.page.user.username,
                 'slug'     : p.page.slug,
                 'title'    : p.page.title} for p in shared_by_others]

    @web.legacy_expose_api
    @web.require_login("create pages")
    def create(self, trans, payload=None, **kwd):
        """
        Create a new page.
        """
        if trans.request.method == 'GET':
            return {
                'title'  : '创建新页面',
                'inputs' : [{
                    'name'      : 'title',
                    'label'     : '名称'
                }, {
                    'name'      : 'slug',
                    'label'     : '标识符',
#                     'help'      : 'A unique identifier that will be used for public links to this page. This field can only contain lowercase letters, numbers, and dashes (-).'
                    'help'      : '将用于指向此页面的公共链接的唯一标识符。该字段只能包含小写字母、数字和破折号(-)。'
                }, {
                    'name'      : 'annotation',
                    'label'     : '注释',
#                     'help'      : 'A description of the page. The annotation is shown alongside published pages.'
                    'help'      : '页面的描述和注释将显示在已发布的页面旁边。'
                }]
            }
        else:
            try:
                page = self.page_manager.create(trans, payload)
            except exceptions.MessageException as e:
                return self.message_exception(trans, unicodify(e))
            return {'message': 'Page \'%s\' successfully created.' % page.title, 'status': 'success'}

    @web.legacy_expose_api
    @web.require_login("edit pages")
    def edit(self, trans, payload=None, **kwd):
        """
        Edit a page's attributes.
        """
        id = kwd.get('id')
        if not id:
#             return self.message_exception(trans, 'No page id received for editing.')
            return self.message_exception(trans, '没有收到用于编辑的页面id。')
        decoded_id = self.decode_id(id)
        user = trans.get_user()
        p = trans.sa_session.query(model.Page).get(decoded_id)
        if trans.request.method == 'GET':
            if p.slug is None:
                self.create_item_slug(trans.sa_session, p)
            return {
#                 'title'  : 'Edit page attributes',
                'title'  : '编辑页面属性',
                'inputs' : [{
                    'name'      : 'title',
                    'label'     : '名称',
                    'value'     : p.title
                }, {
                    'name'      : 'slug',
                    'label'     : '标识符',
                    'value'     : p.slug,
#                     'help'      : 'A unique identifier that will be used for public links to this page. This field can only contain lowercase letters, numbers, and dashes (-).'
                    'help'      : '将用于指向此页面的公共链接的唯一标识符。该字段只能包含小写字母、数字和破折号(-)。'
                }, {
                    'name'      : 'annotation',
                    'label'     : '注释',
                    'value'     : self.get_item_annotation_str(trans.sa_session, user, p),
#                     'help'      : 'A description of the page. The annotation is shown alongside published pages.'
                    'help'      : '页面的描述和注释将显示在已发布的页面旁边。'
                }]
            }
        else:
            p_title = payload.get('title')
            p_slug = payload.get('slug')
            p_annotation = payload.get('annotation')
            if not p_title:
#                 return self.message_exception(trans, 'Please provide a page name is required.')
                return self.message_exception(trans, '请提供页面名称，此项为必填项。')
            elif not p_slug:
#                 return self.message_exception(trans, 'Please provide a unique identifier.')
                return self.message_exception(trans, '请提供唯一的标识符。')
            elif not self._is_valid_slug(p_slug):
#                 return self.message_exception(trans, 'Page identifier can only contain lowercase letters, numbers, and dashes (-).')
                return self.message_exception(trans, '页面标识符只能包含小写字母、数字和破折号(-)。')
            elif p_slug != p.slug and trans.sa_session.query(model.Page).filter_by(user=p.user, slug=p_slug, deleted=False).first():
#                 return self.message_exception(trans, 'Page id must be unique.')
                return self.message_exception(trans, '页面id必须是唯一的。')
            else:
                p.title = p_title
                p.slug = p_slug
                if p_annotation:
                    p_annotation = sanitize_html(p_annotation)
                    self.add_item_annotation(trans.sa_session, user, p, p_annotation)
                trans.sa_session.add(p)
                trans.sa_session.flush()
#             return {'message': 'Attributes of \'%s\' successfully saved.' % p.title, 'status': 'success'}
            return {'message': '成功保存 \'%s\' 的属性。' % p.title, 'status': 'success'}

    @web.expose
    @web.require_login("edit pages")
    def edit_content(self, trans, id):
        """
        Render the main page editor interface.
        """
        id = self.decode_id(id)
        page = trans.sa_session.query(model.Page).get(id)
        assert page.user == trans.user
        return trans.fill_template("page/editor.mako", page=page)

    @web.expose
    @web.require_login("use Galaxy pages")
    def share(self, trans, id, email="", use_panels=False):
        """ Handle sharing with an individual user. """
        msg = mtype = None
        page = trans.sa_session.query(model.Page).get(self.decode_id(id))
        if email:
            other = trans.sa_session.query(model.User) \
                                    .filter(and_(model.User.table.c.email == email,
                                                 model.User.table.c.deleted == false())) \
                                    .first()
            if not other:
                mtype = "error"
#                 msg = ("User '%s' does not exist" % escape(email))
                msg = ("用户 '%s' 不存在" % escape(email))
            elif other == trans.get_user():
                mtype = "error"
#                 msg = ("You cannot share a page with yourself")
                msg = ("您不能与自己共享页面")
            elif trans.sa_session.query(model.PageUserShareAssociation) \
                    .filter_by(user=other, page=page).count() > 0:
                mtype = "error"
#                 msg = ("Page already shared with '%s'" % escape(email))
                msg = ("页面已分享给 '%s'" % escape(email))
            else:
                share = model.PageUserShareAssociation()
                share.page = page
                share.user = other
                session = trans.sa_session
                session.add(share)
                self.create_item_slug(session, page)
                session.flush()
                page_title = escape(page.title)
                other_email = escape(other.email)
#                 trans.set_message("Page '%s' shared with user '%s'" % (page_title, other_email))
                trans.set_message("页面 '%s' 已分享给用户 '%s'" % (page_title, other_email))
                return trans.response.send_redirect(url_for("/pages/sharing?id=%s" % id))
        return trans.fill_template("/ind_share_base.mako",
                                   message=msg,
                                   messagetype=mtype,
                                   item=page,
                                   email=email,
                                   use_panels=use_panels)

    @web.expose
    @web.require_login()
    def save(self, trans, id, content):
        id = self.decode_id(id)
        page = trans.sa_session.query(model.Page).get(id)
        assert page.user == trans.user
        self.page_manager.save_new_revision(trans, page, {"content": content})

    @web.expose
    @web.require_login()
    def display(self, trans, id):
        id = self.decode_id(id)
        page = trans.sa_session.query(model.Page).get(id)
        if not page:
            raise web.httpexceptions.HTTPNotFound()
        return self.display_by_username_and_slug(trans, page.user.username, page.slug)

    @web.expose
    def display_by_username_and_slug(self, trans, username, slug):
        """ Display page based on a username and slug. """

        # Get page.
        session = trans.sa_session
        user = session.query(model.User).filter_by(username=username).first()
        page = trans.sa_session.query(model.Page).filter_by(user=user, slug=slug, deleted=False).first()
        if page is None:
            raise web.httpexceptions.HTTPNotFound()
        # Security check raises error if user cannot access page.
        self.security_check(trans, page, False, True)

        # Process page content.
        processor = PageContentProcessor(trans, self._get_embed_html)
        processor.feed(page.latest_revision.content)
        # Output is string, so convert to unicode for display.
        page_content = unicodify(processor.output(), 'utf-8')

        # Get rating data.
        user_item_rating = 0
        if trans.get_user():
            user_item_rating = self.get_user_item_rating(trans.sa_session, trans.get_user(), page)
            if user_item_rating:
                user_item_rating = user_item_rating.rating
            else:
                user_item_rating = 0
        ave_item_rating, num_ratings = self.get_ave_item_rating_data(trans.sa_session, page)

        return trans.fill_template_mako("page/display.mako", item=page,
                                        item_data=page_content,
                                        user_item_rating=user_item_rating,
                                        ave_item_rating=ave_item_rating,
                                        num_ratings=num_ratings,
                                        content_only=True)

    @web.expose
    @web.require_login("use Galaxy pages")
    def set_accessible_async(self, trans, id=None, accessible=False):
        """ Set page's importable attribute and slug. """
        page = self.get_page(trans, id)

        # Only set if importable value would change; this prevents a change in the update_time unless attribute really changed.
        importable = accessible in ['True', 'true', 't', 'T']
        if page.importable != importable:
            if importable:
                self._make_item_accessible(trans.sa_session, page)
            else:
                page.importable = importable
            trans.sa_session.flush()
        return

    @web.expose
    @web.require_login("rate items")
    @web.json
    def rate_async(self, trans, id, rating):
        """ Rate a page asynchronously and return updated community data. """

        page = self.get_page(trans, id, check_ownership=False, check_accessible=True)
        if not page:
            return trans.show_error_message("The specified page does not exist.")

        # Rate page.
        self.rate_item(trans.sa_session, trans.get_user(), page, rating)

        return self.get_ave_item_rating_data(trans.sa_session, page)

    @web.expose
    def get_embed_html_async(self, trans, id):
        """ Returns HTML for embedding a workflow in a page. """

        # TODO: user should be able to embed any item he has access to. see display_by_username_and_slug for security code.
        page = self.get_page(trans, id)
        if page:
            return "Embedded Page '%s'" % page.title

    @web.expose
    @web.json
    @web.require_login("use Galaxy pages")
    def get_name_and_link_async(self, trans, id=None):
        """ Returns page's name and link. """
        page = self.get_page(trans, id)

        if self.create_item_slug(trans.sa_session, page):
            trans.sa_session.flush()
        return_dict = {"name": page.title, "link": url_for(controller='page',
                                                           action="display_by_username_and_slug",
                                                           username=page.user.username,
                                                           slug=page.slug)}
        return return_dict

    @web.expose
    @web.json
    @web.require_login("select a history from saved histories")
    def list_histories_for_selection(self, trans, **kwargs):
        """ Returns HTML that enables a user to select one or more histories. """
        return self._history_selection_grid(trans, **kwargs)

    @web.expose
    @web.json
    @web.require_login("select a workflow from saved workflows")
    def list_workflows_for_selection(self, trans, **kwargs):
        """ Returns HTML that enables a user to select one or more workflows. """
        return self._workflow_selection_grid(trans, **kwargs)

    @web.expose
    @web.json
    @web.require_login("select a visualization from saved visualizations")
    def list_visualizations_for_selection(self, trans, **kwargs):
        """ Returns HTML that enables a user to select one or more visualizations. """
        return self._visualization_selection_grid(trans, **kwargs)

    @web.expose
    @web.json
    @web.require_login("select a page from saved pages")
    def list_pages_for_selection(self, trans, **kwargs):
        """ Returns HTML that enables a user to select one or more pages. """
        return self._page_selection_grid(trans, **kwargs)

    @web.expose
    @web.json
    @web.require_login("select a dataset from saved datasets")
    def list_datasets_for_selection(self, trans, **kwargs):
        """ Returns HTML that enables a user to select one or more datasets. """
        return self._datasets_selection_grid(trans, **kwargs)

    @web.expose
    def get_editor_iframe(self, trans):
        """ Returns the document for the page editor's iframe. """
        return trans.fill_template("page/wymiframe.mako")

    def get_page(self, trans, id, check_ownership=True, check_accessible=False):
        """Get a page from the database by id."""
        # Load history from database
        id = self.decode_id(id)
        page = trans.sa_session.query(model.Page).get(id)
        if not page:
            error("Page not found")
        else:
            return self.security_check(trans, page, check_ownership, check_accessible)

    def get_item(self, trans, id):
        return self.get_page(trans, id)

    def _get_embedded_history_html(self, trans, decoded_id):
        """
        Returns html suitable for embedding in another page.
        """
        # histories embedded in pages are set to importable when embedded, check for access here
        history = self.history_manager.get_accessible(decoded_id, trans.user, current_history=trans.history)

        # create ownership flag for template, dictify models
        # note: adding original annotation since this is published - get_dict returns user-based annos
        user_is_owner = trans.user == history.user
        history.annotation = self.get_item_annotation_str(trans.sa_session, history.user, history)

        # include all datasets: hidden, deleted, and purged
        history_dictionary = self.history_serializer.serialize_to_view(
            history, view='detailed', user=trans.user, trans=trans
        )
        contents = self.history_serializer.serialize_contents(history, 'contents', trans=trans, user=trans.user)
        history_dictionary['annotation'] = history.annotation

        filled = trans.fill_template("history/embed.mako",
                                     item=history,
                                     user_is_owner=user_is_owner,
                                     history_dict=history_dictionary,
                                     content_dicts=contents)
        return filled

    def _get_embedded_visualization_html(self, trans, encoded_id):
        """
        Returns html suitable for embedding visualizations in another page.
        """
        visualization = self.get_visualization(trans, encoded_id, False, True)
        visualization.annotation = self.get_item_annotation_str(trans.sa_session, visualization.user, visualization)
        if not visualization:
            return None

        # Fork to template based on visualization.type (registry or builtin).
        if((trans.app.visualizations_registry and visualization.type in trans.app.visualizations_registry.plugins) and
                (visualization.type not in trans.app.visualizations_registry.BUILT_IN_VISUALIZATIONS)):
            # if a registry visualization, load a version into an iframe :(
            # TODO: simplest path from A to B but not optimal - will be difficult to do reg visualizations any other way
            # TODO: this will load the visualization twice (once above, once when the iframe src calls 'saved')
            encoded_visualization_id = trans.security.encode_id(visualization.id)
            return trans.fill_template('visualization/embed_in_frame.mako',
                                       item=visualization,
                                       encoded_visualization_id=encoded_visualization_id,
                                       content_only=True)

        return trans.fill_template("visualization/embed.mako", item=visualization, item_data=None)

    def _get_embed_html(self, trans, item_class, item_id):
        """ Returns HTML for embedding an item in a page. """
        item_class = self.get_class(item_class)
        encoded_id, decoded_id = get_page_identifiers(item_id, trans.app)
        if item_class == model.History:
            return self._get_embedded_history_html(trans, decoded_id)

        elif item_class == model.HistoryDatasetAssociation:
            dataset = self.hda_manager.get_accessible(decoded_id, trans.user)
            dataset = self.hda_manager.error_if_uploading(dataset)

            dataset.annotation = self.get_item_annotation_str(trans.sa_session, dataset.history.user, dataset)
            if dataset:
                data = self.hda_manager.text_data(dataset)
                return trans.fill_template("dataset/embed.mako", item=dataset, item_data=data)

        elif item_class == model.StoredWorkflow:
            workflow = self.get_stored_workflow(trans, encoded_id, False, True)
            workflow.annotation = self.get_item_annotation_str(trans.sa_session, workflow.user, workflow)
            if workflow:
                self.get_stored_workflow_steps(trans, workflow)
                return trans.fill_template("workflow/embed.mako", item=workflow, item_data=workflow.latest_workflow.steps)

        elif item_class == model.Visualization:
            return self._get_embedded_visualization_html(trans, encoded_id)

        elif item_class == model.Page:
            pass
