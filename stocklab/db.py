import pydal
from contextlib import ContextDecorator

import stocklab

def _get_keys(schema):
  return [field_name
      for field_name, field_config in schema.items()
      if 'key' in field_config and field_config['key']
      ]

class get_db(pydal.DAL, ContextDecorator):
  def __init__(self, config_name, *args, **kwargs):
    self.__args = args
    self.__kwargs = kwargs
    self.config = stocklab.config[config_name]
    self.logger = stocklab.create_logger('stocklab_db')

  def __enter__(self):
    assert self.config['type'] in ['sqlite', 'mssql']
    if self.config['type'] == 'sqlite':
      import os
      db_path = os.path.join(stocklab.data_path, self.config['filename'])
      uri = f'sqlite://{db_path}'
      self.__kwargs['folder'] = stocklab.data_path
    elif self.config['type'] == 'mssql':
      url = self.config['url']
      user = self.config['user']
      password = self.config['password']
      driver = self.config['driver']
      uri = f'mssql4://{user}:{password}@{url}/stocklab-db?driver={driver}'
    super().__init__(uri=uri, *self.__args, **self.__kwargs)
    return self

  def __exit__(self, err_type, err_value, traceback):
    if isinstance(err_type, Exception):
      self.logger.error(err_value)
    self.close()
    return False # do not eliminate error
  
  def declare_table(self, name, schema):
    def _field(name, config):
      assert name != 'id', 'pyDAL reserved this name'
      _cfg = config.copy()
      try: # pop-out params not used by pyDAL
        _cfg.pop('key')
        _cfg.pop('pre_proc')
      except KeyError:
        pass
      return pydal.Field(name, **_cfg)
    fields = [_field(field_name, schema[field_name])
        for field_name in schema.keys()]
    self.define_table(name, *fields)

  def update(self, mod, res):
    assert type(res) is list
    assert all([type(rec) is dict for rec in res])
    schema = mod.spec['schema']
    ignore_existed = mod.spec['ignore_existed'] if \
        'ignore_existed' in mod.spec else False
    update_existed = mod.spec['update_existed'] if \
        'update_existed' in mod.spec else False
    assert not (ignore_existed and update_existed)

    def _proc(key, val):
      cfg = schema[key]
      field_type = cfg['type'] if 'type' in cfg else 'string'
      type_map = {
          'string': str,
          'text': str,
          'integer': int,
          }
      processed = cfg['pre_proc'](val) if 'pre_proc' in cfg else val
      if field_type in type_map.keys() and processed is not None:
        assert type(processed) is type_map[field_type], 'type error in DB insertion.' +\
            f' Field {key} requires {field_type}, got {type(processed)}'
      return processed

    def _key_q(schema):
      key_fields = _get_keys(schema)
      queries = [table[k] == v for k, v in rec.items() if k in key_fields]
      assert len(key_fields) > 0
      def _and(qs):
        if len(qs) == 1:
          return qs[0]
        else:
          return qs[0] & _and(qs[1:])
      return _and(queries)

    table = self[mod.name]
    for rec in res:
      rec = {k:_proc(k, v) for k, v in rec.items()}
      if ignore_existed:
        if not self[mod.name](_key_q(schema)):
          self[mod.name].insert(**rec)
      elif update_existed:
        self[mod.name].update_or_insert(_key_q(schema), **rec)
      else:
        self[mod.name].insert(**rec)
    self.commit()
