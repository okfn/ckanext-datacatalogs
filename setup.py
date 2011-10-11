from setuptools import setup, find_packages

version = '0.1'
from ckanext.datacatalogs import __doc__ as long_description

setup(
	name='ckanext-datacatalogs',
	version=version,
	description=long_description.split('\n')[0],
	long_description=long_description,
	classifiers=[],
	keywords='',
	author='John Glover',
	author_email='john.glover@okfn.org',
	url='',
	license='mit',
    packages=find_packages(exclude=['tests']),
    namespace_packages=['ckanext', 'ckanext.datacatalogs'],
    package_data = {'ckanext.datacatalogs' : ['public/ckanext-datacatalogs/*.js', 
                                              'public/ckanext-datacatalogs/css/*.css',
                                              'public/ckanext-datacatalogs/images/*.png',
                                              'templates/*.html',
                                              'templates/package*.html']},
	include_package_data=True,
	zip_safe=False,
	install_requires=[],
	entry_points=\
	"""
    [ckan.plugins]
	datacatalogs=ckanext.datacatalogs.plugin:DataCatalogsPlugin
	"""
)

