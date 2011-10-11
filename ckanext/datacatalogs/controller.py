"""
CKAN DataCatalogs Extension
"""
from logging import getLogger
log = getLogger(__name__)

from pylons.i18n import _
from pylons import request, tmpl_context as c
from ckan.lib.base import render, abort, h, g, etag_cache
from ckan.lib.search import query_for, SearchError
from ckan.controllers import home
from ckan.controllers.package import PackageController, search_url
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

class DataCatalogsController(PackageController):
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

    def search(self):        
        if not self.authorizer.am_authorized(c, model.Action.SITE_READ, model.System):
            abort(401, _('Not authorized to see this page'))
        q = c.q = request.params.get('q') # unicode format (decoded from utf8)

        # hack q to get url search working:
        # - remove 'http://'
        q = q.replace('http://', '') if q else None

        c.open_only = request.params.get('open_only')
        c.downloadable_only = request.params.get('downloadable_only')
        c.query_error = False
        try:
            page = int(request.params.get('page', 1))
        except ValueError, e:
            abort(400, ('"page" parameter must be an integer'))
        limit = 20
        query = query_for(model.Package)

        # most search operations should reset the page counter:
        params_nopage = [(k, v) for k,v in request.params.items() if k != 'page']
        
        def drill_down_url(**by):
            params = list(params_nopage)
            params.extend(by.items())
            return search_url(set(params))
        
        c.drill_down_url = drill_down_url 
        
        def remove_field(key, value):
            params = list(params_nopage)
            params.remove((key, value))
            return search_url(params)

        c.remove_field = remove_field
        
        def pager_url(q=None, page=None):
            params = list(params_nopage)
            params.append(('page', page))
            return search_url(params)

        try:
            c.fields = []
            for (param, value) in request.params.items():
                if not param in ['q', 'open_only', 'downloadable_only', 'page'] \
                        and len(value) and not param.startswith('_'):
                    c.fields.append((param, value))

            query.run(query=q,
                      fields=c.fields,
                      facet_by=g.facets,
                      limit=limit,
                      offset=(page-1)*limit,
                      return_objects=True,
                      filter_by_openness=c.open_only,
                      filter_by_downloadable=c.downloadable_only,
                      username=c.user)
                       
            c.page = h.Page(
                collection=query.results,
                page=page,
                url=pager_url,
                item_count=query.count,
                items_per_page=limit
            )
            c.facets = query.facets
            c.page.items = query.results
        except SearchError, se:
            c.query_error = True
            c.facets = {}
            c.page = h.Page(collection=[])
        
        return render('package/search.html')


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
