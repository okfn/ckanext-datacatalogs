CKAN Catalog Extension
======================

**Current Status:** Beta

Installation and Activation
---------------------------

To install the plugin, enter your virtualenv and install the source:

    $ pip install hg+http://bitbucket.org/okfn/ckanext-catalog

This will also register a plugin entry point, so you now should be 
able to add the following to your CKAN .ini file:

    ckan.plugins = catalog
 
After you clear your cache and reload the site the plugin should be available. 

Tests
-----
From the ckanext-catalog directory, run:

    $ nosetests --ckan
