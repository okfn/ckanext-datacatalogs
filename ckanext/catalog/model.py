"""
CKAN Catalog Extension Data Model
"""
from datetime import datetime
import sqlalchemy as sa
from ckan import model
from ckan.model import meta, User, Package, Session, Tag
from ckan.model.meta import types, Table, ForeignKey, DateTime
from ckan.model.types import make_uuid

# not needed for now, use the package model and use the 'extras' field
# to store any additional fields
