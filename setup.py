from setuptools import setup, find_packages

version = '0.1'
from ckanext.catalog import __doc__ as long_description

setup(
	name='ckanext-catalog',
	version=version,
	description=long_description.split('\n')[0],
	long_description=long_description,
	classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
	keywords='',
	author='John Glover',
	author_email='j@johnglover.net',
	url='',
	license='mit',
    packages=find_packages(exclude=['tests']),
    namespace_packages=['ckanext', 'ckanext.catalog'],
    package_data = {'ckanext.catalog' : ['public/ckanext-catalog/*.js', 
                                         'public/ckanext-catalog/css/*.css',
                                         'public/ckanext-catalog/images/*.png',
                                         'templates/*.html']},
	include_package_data=True,
	zip_safe=False,
	install_requires=[
		# -*- Extra requirements: -*-
	],
	entry_points=\
	"""
    [ckan.plugins]
	catalog=ckanext.catalog.plugin:CatalogPlugin
	""",
)
