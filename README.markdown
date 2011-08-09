CKAN - datacatalogs.org theme
=============================

This is the custom CKAN theme used on http://datacatalogs.org.


Installation and Activation
---------------------------

To install the plugin, enter your virtualenv and install the source:

    $ pip install hg+http://bitbucket.org/okfn/ckanext-catalog

This will also register a plugin entry point, so you now should be 
able to add the following to your CKAN .ini file:

    ckan.plugins = catalog
 
After you reload the site the plugin should be available. 


Configuration
-------------

You should also add the following to the app:main section of your config file:

    ckan.site_title = datacatalogs.org
    ckan.site_logo = /ckanext-catalog/images/datacatalogs.png
    package_edit_return_url = /catalog/<NAME>
    package_new_return_url = /catalog/<NAME>

To prevent non-system admins from being able to create packages, run:

    paster roles -c datacatalogs.ini deny anon_editor create-package
    paster roles -c datacatalogs.ini deny editor create-package

Tests
-----
From the ckanext-catalog directory, run:

    $ nosetests --ckan
