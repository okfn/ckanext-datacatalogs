"""
CKAN Catalog Extension
"""
from logging import getLogger
log = getLogger(__name__)

from pylons.i18n import _
from pylons.decorators import jsonify
from pylons import request, tmpl_context as c
from ckan.lib.base import BaseController, response, render, abort
from ckanext.catalog import model

class CatalogController(BaseController):
    """
    The ckanext-catalog Controller.
    """
    def catalog_list(self):
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

    def catalog_new(self):
        """
        Display the form for adding a new catalog.
        """
        return "new"
