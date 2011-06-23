from ckanclient.loaders.base import SimpleGoogleSpreadsheetLoader 

class DataCatalogLoader(SimpleGoogleSpreadsheetLoader):
    """
    Load a google spreadsheet containing catalog data and add it to
    a CKAN instance.
    """
    def __init__(self, import_tag=None):
        SimpleGoogleSpreadsheetLoader.__init__(self)
        self.import_tag = import_tag

    def entity_to_package(self, entity):
        required_fields = ['Name', 'Title', 'Description', 'Homepage']
        for field in required_fields:
            if not entity[field+'*']:
                print 'Skipping', entity
                return None

        name = entity.pop('Name*')
        title = entity.pop('Title*')
        url = entity.pop('Homepage*')
        notes = entity.pop('Description*', '')
        author = entity.pop('Publisher', '')
        license = entity.pop('Metadata License', '') or None
        tags = [x.lower() for x in entity.pop('Keywords', '').split()]
        if self.import_tag:
            tags.append(self.import_tag)
        extras = {
            'spatial_text': entity.pop('Spatial Coverage Text', ''),
            'spatial': entity.pop('Spatial Coverage', ''),
            'language': entity.pop('Language', '')
        }
        package = self.create_package(
            name,
            title=title,
            url=url,
            author=author,
            license=license,
            notes=notes,
            tags=tags,
            extras=extras
        )
        return package

if __name__ == '__main__':
    # example usage: 
    #
    # $ python importcatalogs.py --google-email=<email> --google-password=<password> 
    #   --google-spreadsheet-key=<key> --ckan-api-key=<key> --ckan-api-location=<location>
    #   --no-create-confirmation --no-update-confirmation
    loader = DataCatalogLoader('ctic')
    loader.run()
