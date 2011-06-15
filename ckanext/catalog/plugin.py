"""
Catalog is a CKAN extension - http://ckan.org/wiki/Extensions.
Enable by adding to your ckan.plugins line in the CKAN config::

    ckan.plugins = catalog
"""
import os
from logging import getLogger
log = getLogger(__name__)

from genshi.input import HTML
from genshi.filters import Transformer
from pylons import request, tmpl_context as c
from webob import Request
from ckan.lib.base import h
from ckan.plugins import SingletonPlugin, implements
from ckan.plugins.interfaces import (IConfigurable, IRoutes, 
                                     IGenshiStreamFilter, IConfigurer)

from ckanext.catalog import model
from ckanext.catalog import controller
from ckanext.catalog import html

class CatalogPlugin(SingletonPlugin):
    """
    Plugin
    """
    implements(IConfigurable)
    implements(IConfigurer, inherit=True)
    implements(IRoutes, inherit=True)
    implements(IGenshiStreamFilter)

    def update_config(self, config):
        """
        Called during CKAN setup.

        Add the public folder to CKAN's list of public folders,
        and add the templates folder to CKAN's list of template
        folders.
        """
        # add public folder to the CKAN's list of public folders
        here = os.path.dirname(__file__)
        public_dir = os.path.join(here, 'public')
        if config.get('extra_public_paths'):
            config['extra_public_paths'] += ',' + public_dir
        else:
            config['extra_public_paths'] = public_dir
        # add template folder to the CKAN's list of template folders
        template_dir = os.path.join(here, 'templates')
        if config.get('extra_template_paths'):
            config['extra_template_paths'] += ',' + template_dir
        else:
            config['extra_template_paths'] = template_dir

    def configure(self, config):
        """
        Called at the end of CKAN setup.

        Create catalog and catalog_tag tables in the database.
        """
        model.catalog_table.create(checkfirst=True)
        model.catalog_tag_table.create(checkfirst=True)

    def before_map(self, map):
        """
        Setup routing.
        """
        return map

    def filter(self, stream):
        """
        Required to implement IGenshiStreamFilter.
        """
        routes = request.environ.get('pylons.routes_dict')
        return stream
