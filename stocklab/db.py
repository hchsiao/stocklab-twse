import sqlite3
from contextlib import ContextDecorator

import stocklab
class get_db(ContextDecorator):
  def __init__(self, logger):
    self.logger = stocklab.create_logger('stocklab_db')

  def __enter__(self):
    self.conn = sqlite3.connect(stocklab.CACHE_FILE)
    self.c = self.conn.cursor()
    return self

  def __exit__(self, err_type, err_value, traceback):
    if err_type is sqlite3.Error:
      self.logger.error(err_value)
      if self.conn:
        self.conn.close()
        # self.c.close() not required
      return True
    return False
  
  def commit(self, *args):
    return self.conn.commit(*args)
  
  def execute(self, *args):
    return self.c.execute(*args)

  def has_table(self, name):
    exist = [r for r in self.execute(f"SELECT name FROM sqlite_master\
        WHERE type='table' AND name='{name}';")]
    return bool(exist)

  def create_if_not_exist(self, mod):
    schema = type(mod).spec['schema']
    schema_sql = ', '.join([col[0] for col in schema])
    key_fields = []
    for col in schema:
      if 'key' in col:
        key_fields.append(col[0].split(' ')[0])
    if key_fields:
      key_fields = ', '.join(key_fields)
      create_sql = f"CREATE TABLE {mod.name} (\
          {schema_sql},\
          PRIMARY KEY ({key_fields})\
      );"
    else:
      create_sql = f"CREATE TABLE {mod.name} (\
          {schema_sql}\
      );"
    if not self.has_table(mod.name):
      self.logger.debug("creating DB with sql: " + create_sql)
      self.execute(create_sql)

  def update(self, mod, res):
    schema = type(mod).spec['schema']
    ignore_nonunique = type(mod).spec['ignore_nonunique'] if \
        'ignore_nonunique' in type(mod).spec else False
    assert type(res) is list
    cols = ', '.join([col[0].split(' ')[0] for col in schema])
    fmts = ', '.join([col[1] for col in schema])
    sql = f"INSERT INTO {mod.name}({cols})\
        VALUES({fmts})"
    for rec in res:
      try:
        self.execute(sql, tuple(rec))
      except sqlite3.IntegrityError as e:
        if ignore_nonunique:
          continue
        else:
          raise e
    self.commit()
