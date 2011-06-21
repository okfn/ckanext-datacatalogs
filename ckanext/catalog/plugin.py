"""
Catalog is a CKAN extension - http://ckan.org/wiki/Extensions.
Enable by adding to your ckan.plugins line in the CKAN config::

    ckan.plugins = catalog
"""
import os
from logging import getLogger
log = getLogger(__name__)

from pylons import request, tmpl_context as c
from ckan.lib.base import h
from ckan.plugins import SingletonPlugin, implements
from ckan.plugins.interfaces import IConfigurable, IRoutes, IConfigurer

class CatalogPlugin(SingletonPlugin):
    """
    Plugin
    """
    implements(IConfigurable)
    implements(IConfigurer, inherit=True)
    implements(IRoutes, inherit=True)

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
        pass

    def before_map(self, map):
        """
        Setup routing.
        """
        map.connect('catalog_list', '/catalogs',
                    controller='ckanext.catalog.controller:CatalogController',
                    action='list')
        map.connect('catalog_new', '/catalog/new',
                    controller='ckanext.catalog.controller:CatalogController',
                    action='new')
        map.connect('catalog_edit', '/catalog/edit/{id}', 
                    controller='ckanext.catalog.controller:CatalogController', 
                    action='edit')
        map.connect('catalog_read', '/catalog/{id}', 
                    controller='ckanext.catalog.controller:CatalogController', 
                    action='read')
        map.connect('catalog_history', '/catalog/history/{id}', 
                    controller='ckanext.catalog.controller:CatalogController', 
                    action='history')
        map.connect('/catalog/{action}/{id}',
                    controller='ckanext.catalog.controller:CatalogController', 
                    requirements=dict(action='|'.join([
                        'edit',
                        'authz',
                        'history',
                        'read_ajax',
                        'history_ajax',
                    ]))
        )
        map.connect('catalog_search', '/catalog',  
                    controller='ckanext.catalog.controller:CatalogController', 
                    action='search')
        map.connect('catalog_index', '/catalog',  
                    controller='ckanext.catalog.controller:CatalogController', 
                    action='index')
        map.connect('/catalog/{action}',
                    controller='ckanext.catalog.controller:CatalogController', 
                    requirements=dict(action='|'.join([
                        'list',
                        'new',
                        'autocomplete',
                        'search'
                    ]))
        )
        map.connect('/catalog/{action}/{id}/{revision}', 
                    controller='ckanext.catalog.controller:CatalogController', 
                    action='read_ajax')
        return map
