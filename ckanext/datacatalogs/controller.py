"""
CKAN DataCatalogs Extension
"""
from logging import getLogger
log = getLogger(__name__)

from pylons.i18n import _
from pylons import tmpl_context as c, config
from ckan.lib.base import render, etag_cache, h, redirect, request
from ckan.lib.search import query_for, SearchError
from ckan.controllers import home
from ckan.controllers import package
from ckan.lib.navl.validators import (
    ignore_missing, not_empty, ignore, keep_extras
)
import ckan.logic.validators as val
from ckan.logic.action import get
from ckan import model

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

        return render('home/index.html')
        return render('home/index.html', cache_key=cache_key,
                      cache_expire=home.cache_expires)

