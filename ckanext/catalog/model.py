"""
CKAN Catalog Extension Data Model
"""
import sqlalchemy as sa
from ckan import model
from ckan.model import meta, User, Package, Session
from ckan.model.types import make_uuid
from datetime import datetime
