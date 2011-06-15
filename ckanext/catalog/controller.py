"""
CKAN Catalog Extension
"""
from logging import getLogger
log = getLogger(__name__)

from pylons.i18n import _
from pylons.decorators import jsonify
from pylons import request, tmpl_context as c
from ckan.lib.base import BaseController, response, render, abort
from ckan.controllers.package import PackageController
from ckan.lib.navl.validators import (
    ignore_missing, not_empty, ignore, keep_extras
)
import ckan.logic.validators as val
from ckanext.catalog import model

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
            'tag_string': [ignore_missing, val.tag_string_convert],
            '__extras': [ignore],
        }

    def _db_to_form_schema(data):
        return {
            'language': [convert_from_extras, ignore_missing],
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

    def list(self):
        """
        Display a page containing a list of all todo items, sorted by category.
        """
        # categories = model.Session.query(func.count(model.Todo.id).label('todo_count'), 
        #                                  model.Todo.todo_category_id)\
        #     .filter(model.Todo.resolved == None)\
        #     .group_by(model.Todo.todo_category_id)
        # c.categories = []
        # c.pkg_names = {}
        # for t in categories:
        #     tc = model.TodoCategory.get(t.todo_category_id)
        #     tc.todo_count = t.todo_count
        #     # get todo items for each category
        #     tc.todo = model.Session.query(model.Todo).filter(model.Todo.resolved == None)\
        #         .filter(model.Todo.todo_category_id == t.todo_category_id)\
        #         .order_by(model.Todo.created.desc())
        #     for todo in tc.todo:
        #         # get the package name for each package if one exists
        #         if todo.package_id:
        #             c.pkg_names[todo.package_id] = model.Package.get(todo.package_id).name
        #     c.categories.append(tc)
        # # sort into alphabetical order
        # c.categories.sort(key = lambda x: x.name)
        c.catalogs = None
        return render("catalog_list.html")
