import stocklab
from stocklab.datetime import Date
import logging

_table_name = 'stocklab__states'

# do not explicitly set primary key otherwise 'update_or_insert' won't work
_schema = {
    'key': {'type': 'string'},
    'val': {'type': 'string'},
    }

def get(key):
  with stocklab.get_db('cache') as db:
    db.declare_table(_table_name, _schema)
    rows = db(db[_table_name]['key'] == key).select()
    return rows[0]['val'] if rows else None

def set(key, val):
  assert type(val) is str, f'expected type is str, got {type(val)}'
  with stocklab.get_db('cache') as db:
    db.declare_table(_table_name, _schema)
    table = db[_table_name]
    table.update_or_insert(table.key==key, key=key, val=val)
