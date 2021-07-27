""" Refactor this entire file. """
from stocklab.db import get_db
_table_name = 'stocklab__states'

# do not explicitly set primary key otherwise 'update_or_insert' won't work
_schema = {
    'key': {'type': 'string'},
    'val': {'type': 'string'},
    }

def get(key):
  with get_db('state') as db:
    db.declare_table(_table_name, _schema)
    rows = db(db[_table_name]['key'] == key).select()
    return rows[0]['val'] if rows else None

def set(key, val):
  with get_db('state') as db:
    db.declare_table(_table_name, _schema)
    table = db[_table_name]
    table.update_or_insert(table.key==key, key=key, val=str(val))
