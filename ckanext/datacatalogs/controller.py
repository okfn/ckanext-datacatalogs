"""
CKAN DataCatalogs Extension
"""
from logging import getLogger
log = getLogger(__name__)

from pylons.i18n import _
from pylons import tmpl_context as c, config
import genshi
from ckan.lib.base import render, etag_cache, h, redirect, request, abort
from ckan.lib.search import query_for, SearchError
from ckan.lib.helpers import Page
from ckan.controllers import home
from ckan.controllers import package
from ckan.controllers import group
from ckan.lib.navl.validators import (
    ignore_missing, empty, not_empty, ignore, keep_extras
)
import ckan.logic.validators as val
from ckan.logic import get_action
from ckan.logic.action import get
from ckan.logic import NotFound, NotAuthorized
from ckan import model
import ckan

from sqlalchemy.sql import select
from ckan.lib.dictization import table_dictize
from ckan.lib.dictization.model_dictize import resource_list_dictize

def convert_to_extras(key, data, errors, context):
    extras = data.get(('extras',), [])
    if not extras:
        data[('extras',)] = extras
    extras.append({'key': key[-1], 'value': data[key]})

def convert_from_extras(key, data, errors, context):
    for data_key, data_value in data.iteritems():
        if (data_key[0] == 'extras' 
            and data_key[-1] == 'key'
            and data_value == key[-1]):
            data[key] = data[('extras', data_key[1], 'value')]

def _package_list_with_resources(context, package_revision_list):
    package_list = []
    for package in package_revision_list:
        result_dict = table_dictize(package, context)
        res_rev = model.resource_revision_table
        resource_group = model.resource_group_table
        query = select([res_rev], from_obj = res_rev.join(resource_group,
                   resource_group.c.id == res_rev.c.resource_group_id))
        query = query.where(resource_group.c.package_id == package.id)
        result = query.where(res_rev.c.current == True).execute()
        result_dict["resources"] = resource_list_dictize(result, context)
        license_id = result_dict['license_id']
        if license_id:
            try:
                isopen = model.Package.get_license_register()[license_id].isopen()
                result_dict['isopen'] = isopen
            except KeyError:
                # TODO: create a log message this error?
                result_dict['isopen'] = False
        else:
            result_dict['isopen'] = False
        package_list.append(result_dict)
    return package_list

class DataCatalogsController(package.PackageController):
    """
    The ckanext-datacatalogs Controller.
    """
    package_form = 'package/catalog_form.html'

    def _form_to_db_schema(self):
        return {
            'name': [not_empty, unicode, val.name_validator],
            'title': [not_empty, unicode],
            'url': [not_empty, unicode],
            'notes': [ignore_missing, unicode],
            'author': [ignore_missing, unicode],
            'license_id': [ignore_missing, unicode],
            'language': [ignore_missing, unicode, convert_to_extras],
            'state': [val.ignore_not_admin, ignore_missing],
            'spatial_text': [ignore_missing, unicode, convert_to_extras],
            'spatial': [ignore_missing, unicode, convert_to_extras],
            'tag_string': [ignore_missing, val.tag_string_convert],
            '__extras': [ignore],
            'groups': {
                'id': [ignore_missing, unicode],
                '__extras': [empty],
                'name': [ignore, unicode],
            }
        }

    def _db_to_form_schema(self):
        return {
            'language': [convert_from_extras, ignore_missing],
            'spatial_text': [convert_from_extras, ignore_missing],
            'spatial': [convert_from_extras, ignore_missing],
            'extras': {
                'key': [],
                'value': [],
                '__extras': [keep_extras]
            },
            'tags': {
                '__extras': [keep_extras]
            },
            '__extras': [keep_extras],
            'groups': {
                'id': [],
                '__extras': [ignore_missing],
                'name': [],
            }
        }

    def _check_data_dict(self, data_dict):
        return
    
    def _form_save_redirect(self, pkgname, action):
        '''This redirects the user to the CKAN package/read page,
        unless there is request parameter giving an alternate location,
        perhaps an external website.
        @param pkgname - Name of the package just edited
        @param action - What the action of the edit was
        '''
        assert action in ('new', 'edit')
        if action == 'new':
            msg = _('<span class="new-dataset">Your catalog has been created.</span>')
            h.flash_success(msg, allow_html=True)
        url = request.params.get('return_to') or \
              config.get('package_%s_return_url' % action)
        if url:
            url = url.replace('<NAME>', pkgname)
        else:
            url = h.url_for(controller='package', action='read', id=pkgname)
        redirect(url)        


class DataCatalogsHomeController(home.HomeController):
    @home.proxy_cache(expires=home.cache_expires)
    def index(self):
        cache_key = self._home_cache_key()
        etag_cache(cache_key)

        try:
            query = query_for(model.Package)
            query.run({'q': '*:*'})
            c.package_count = query.count
            c.latest_packages = get.current_package_list_with_resources(
                {'model': model, 'user': c.user},
                {'limit': 5}
            )  
        except SearchError, se:
            c.package_count = 0
            c.latest_packages = []

        return render('home/index.html', cache_key=cache_key,
                      cache_expire=home.cache_expires)

class DataCatalogsGroupController(group.GroupController):
    def read(self, id):
        context = {'model': model, 'session': model.Session,
                   'user': c.user or c.author,
                   'schema': self._form_to_db_schema()}
        data_dict = {'id': id}
        try:
            c.group_dict = get_action('group_show')(context, data_dict)
            c.group = context['group']
        except NotFound:
            abort(404, _('Group not found'))
        except NotAuthorized:
            abort(401, _('Unauthorized to read group %s') % id)
        try:
            description_formatted = ckan.misc.MarkdownFormat().to_html(c.group.get('description',''))
            c.description_formatted = genshi.HTML(description_formatted)
        except Exception, e:
            error_msg = "<span class='inline-warning'>%s</span>" % _("Cannot render description")
            c.description_formatted = genshi.HTML(error_msg)
        
        try:
            desc_formatted = ckan.misc.MarkdownFormat().to_html(c.group.description)
            desc_formatted = genshi.HTML(desc_formatted)
        except genshi.ParseError, e:
            desc_formatted = 'Error: Could not parse group description'
        c.group_description_formatted = desc_formatted
        c.group_admins = self.authorizer.get_admins(c.group)

        # copy of group_package show from the logic layer
        #
        # TODO: remove when this fix makes it into a 1.5 stable release
        query = model.Session.query(model.PackageRevision)\
            .filter(model.PackageRevision.state=='active')\
            .filter(model.PackageRevision.current==True)\
            .join(model.PackageGroup, model.PackageGroup.package_id==model.PackageRevision.id)\
            .join(model.Group, model.Group.id==model.PackageGroup.group_id)\
            .filter_by(id=context['group'].id)
        query = query.order_by(model.package_revision_table.c.revision_timestamp.desc())
        pack_rev = query.all()
        results = _package_list_with_resources(context, pack_rev)

        c.page = Page(
            collection=results,
            page=request.params.get('page', 1),
            items_per_page=50
        )

        return render('group/read.html')

