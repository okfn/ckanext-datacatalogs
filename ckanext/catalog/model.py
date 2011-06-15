"""
CKAN Catalog Extension Data Model
"""
import sqlalchemy as sa
from ckan import model
from ckan.model import meta, User, Package, Session, Tag
from ckan.model.meta import types, Table, ForeignKey, DateTime
from ckan.model.types import make_uuid
from datetime import datetime

CATALOG_NAME_MAX_LENGTH = 100

catalog_table = Table('catalog', meta.metadata,
    meta.Column('id', types.UnicodeText, primary_key=True, default = make_uuid),
    meta.Column('name', types.Unicode(CATALOG_NAME_MAX_LENGTH),
                nullable=False, unique=True),
    meta.Column('homepage', types.UnicodeText, nullable = False, unique = True),
    meta.Column('title', types.UnicodeText, nullable = False),
    meta.Column('publisher', types.UnicodeText, nullable = False),
    meta.Column('description', types.UnicodeText),
    meta.Column('spatial', types.UnicodeText),
    meta.Column('created', DateTime, default = datetime.now, nullable = False))

catalog_tag_table = Table('catalog_tag', meta.metadata,
    meta.Column('id', types.UnicodeText, primary_key=True, default=make_uuid),
    meta.Column('catalog_id', types.UnicodeText, 
                ForeignKey('catalog.id', onupdate='CASCADE', ondelete='CASCADE')),
    meta.Column('tag_id', types.UnicodeText, 
                ForeignKey('tag.id', onupdate='CASCADE', ondelete='CASCADE')))

class Catalog(object):
    """A Catalog Object"""
    def __init__(self):
        pass
    def __repr__(self):
        return "<Catalog('%s')>" % (self.id)

    @classmethod
    def get(cls, reference):
        """Returns a Catalog object referenced by its id."""
        return Session.query(cls).filter(cls.id == reference).first()

class CatalogTag(object):
    def __init__(self, catalog = None, tag = None, state = None, **kwargs):
        self.catalog = catalog
        self.tag = tag
        self.state = state
        for k,v in kwargs.items():
            setattr(self, k, v)

    def __repr__(self):
        return '<CatalogTag package=%s tag=%s>' % (self.catalog.name, self.tag.name)

    @classmethod
    def by_name(self, catalog_name, tag_name, autoflush=True):
        q = Session.query(self).autoflush(autoflush).\
            join('package').filter(Catalog.name==catalog_name).\
            join('tag').filter(Tag.name==tag_name)
        assert q.count() <= 1, q.all()
        return q.first()

meta.mapper(Catalog, catalog_table)
meta.mapper(CatalogTag, catalog_tag_table)
