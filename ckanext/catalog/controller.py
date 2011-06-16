"""
CKAN Catalog Extension
"""
from logging import getLogger
log = getLogger(__name__)

from pylons.i18n import _
from pylons.decorators import jsonify
from pylons import request, tmpl_context as c
from ckan.lib.base import BaseController, response, render, abort, h
from ckan.controllers.package import PackageController
from ckan.lib.navl.validators import (
    ignore_missing, not_empty, ignore, keep_extras
)
import ckan.logic.validators as val
from ckan.lib.search import query_for
from sqlalchemy.orm import eagerload_all
from ckanext.catalog import model

CATALOG_TAG = u'data-catalog'
LIST_LIMIT = 25

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

    def list(self):
        """
        Display a page containing a list of all data catalogs
        """
        query = model.Session.query(model.Tag)\
            .filter(model.Tag.name == CATALOG_TAG)\
            .options(eagerload_all('package_tags.package'))\
            .options(eagerload_all('package_tags.package.package_tags.tag'))
        tag = query.first()
        if tag is None:
            abort(404)
        c.catalogs = tag.packages_ordered
        return render("catalog_list.html")
