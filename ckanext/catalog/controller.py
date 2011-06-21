"""
CKAN Catalog Extension
"""
from logging import getLogger
log = getLogger(__name__)
import datetime
import re

from pylons.i18n import _
from pylons.decorators import jsonify
from pylons import request, tmpl_context as c
from pylons import config, cache
from ckan.lib.base import BaseController, response, render, abort, h
from ckan.lib.base import etag_cache, response, redirect, gettext
from ckan.lib.package_saver import PackageSaver, ValidationException
from ckan.lib.cache import proxy_cache
from ckan.controllers.package import PackageController, autoneg_cfg
from ckan.lib.navl.validators import (
    ignore_missing, not_empty, ignore, keep_extras
)
import ckan.logic.action.get as get
import ckan.logic.validators as val
from ckan.logic import NotFound, NotAuthorized, ValidationError
from sqlalchemy.orm import eagerload_all
from autoneg.accept import negotiate
from ckan import model

CATALOG_TAG = u'data-catalog'
LIST_LIMIT = 25 # TODO: limit list results to this name items per page

def add_catalog_tag(key, data, errors, context):
    """
    Adds a tag with the value of the CATALOG_TAG variable to the tags list if it
    doesn't already exist
    """
    if not CATALOG_TAG in data[key]:
        data[key] = CATALOG_TAG + u' ' + data[key]

def remove_catalog_tag(key, data, errors, context):
    """
    Sets the tag with the value in the CATALOG_TAG variable to the empty string
    """
    for data_key, data_value in data.iteritems():
        if (data_key[0] == 'tags' and data_key[-1] == 'name'
            and data_value == CATALOG_TAG):
            data[data_key] = u''

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

class CatalogController(PackageController):
    """
    The ckanext-catalog Controller.
    """
    package_form = 'catalog_form.html'

    def _form_to_db_schema(self):
        return {
            'name': [not_empty, unicode, val.name_validator],
            'title': [not_empty, unicode],
            'url': [not_empty, unicode],
            'notes': [ignore_missing, unicode],
            'language': [ignore_missing, unicode, convert_to_extras],
            'spatial': [ignore_missing, unicode, convert_to_extras],
            'tag_string': [add_catalog_tag, ignore_missing, val.tag_string_convert],
            '__extras': [ignore],
        }

    def _db_to_form_schema(self):
        return {
            'language': [convert_from_extras, ignore_missing],
            'spatial': [convert_from_extras, ignore_missing],
            'extras': {
                'key': [],
                'value': [],
                '__extras': [keep_extras]
            },
            'tags': {
                'name': [remove_catalog_tag],
                '__extras': [keep_extras]
            },
            '__extras': [keep_extras],
        }

    def _check_data_dict(self, data_dict):
        return

    @proxy_cache()
    def read(self, id):
        context = {'model': model, 'session': model.Session,
                   'user': c.user or c.author, 'extras_as_string': True,
                   'schema': self._form_to_db_schema(),
                   'id': id}
        split = id.split('@')
        if len(split) == 2:
            context['id'], revision = split
            try:
                date = datetime.datetime(*map(int, re.split('[^\d]', revision)))
                context['revision_date'] = date
            except ValueError:
                context['revision_id'] = revision
        #check if package exists
        try:
            c.pkg_dict = get.package_show(context)
            c.pkg = context['package']
        except NotFound:
            abort(404, _('Package not found'))
        except NotAuthorized:
            abort(401, _('Unauthorized to read package %s') % id)
        
        # cache_key = self._pkg_cache_key(c.pkg)        
        # etag_cache(cache_key)
        
        #set a cookie so we know whether to display the welcome message
        c.hide_welcome_message = bool(request.cookies.get('hide_welcome_message', False))
        response.set_cookie('hide_welcome_message', '1', max_age=3600) #(make cross-site?)

        # used by disqus plugin
        c.current_package_id = c.pkg.id
        
        if config.get('rdf_packages'):
            accept_header = request.headers.get('Accept', '*/*')
            for content_type, exts in negotiate(autoneg_cfg, accept_header):
                if "html" not in exts: 
                    rdf_url = '%s%s.%s' % (config['rdf_packages'], c.pkg.id, exts[0])
                    redirect(rdf_url, code=303)
                break

        PackageSaver().render_package(c.pkg_dict, context)
        return render('catalog_read.html')

    def list(self):
        """
        Display a page containing a list of all data catalogs
        """
        tag = model.Session.query(model.Tag)\
            .filter(model.Tag.name == CATALOG_TAG)\
            .options(eagerload_all('package_tags.package'))\
            .options(eagerload_all('package_tags.package.package_tags.tag'))\
            .first()
        if tag is None:
            abort(404)
        # TODO: check state of package for deleted/removed/inactive packages
        cat_cmp = lambda pkg1, pkg2: cmp(pkg1.name, pkg2.name)
        c.catalogs = sorted(tag.packages, cmp = cat_cmp)
        return render("catalog_list.html")
