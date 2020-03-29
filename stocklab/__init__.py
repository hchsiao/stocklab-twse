MODULE_DIR = "./modules/"
CRAWlER_DIR = "./crawlers/"
DATA_DIR = "./app_data/"

import importlib.util
import os
root_path = importlib.util.find_spec(__name__).origin
root_path = os.path.abspath(root_path + "/../../")
modules_path = os.path.join(root_path, MODULE_DIR)
crawlers_path = os.path.join(root_path, CRAWlER_DIR)
data_path = os.path.join(root_path, DATA_DIR)

force_offline = False
timezone_offset = 8 # TWSE: GMT+8

import logging
log_level = logging.INFO
init_flag = False
_logger = None

_loggers = {}
def create_logger(name):
  global log_level, _loggers
  if name in _loggers:
    return _loggers[name]
  else:
    logger = logging.getLogger(name)
    log_handler = logging.StreamHandler()
    log_format = logging.Formatter(
        f"[%(levelname)s] {name}: %(message)s"
        )
    log_handler.setFormatter(log_format)
    logger.addHandler(log_handler)
    logger.setLevel(log_level)
    _loggers[name] = logger
    return logger

from stocklab.args import Args
from stocklab.base_crawler import Crawler
from stocklab.base_module import Module, MetaModule
from stocklab.db import get_db
from stocklab.error import *
from .states import set as set_state
from .states import get as get_state
__all__ = [
    'Args', 'Crawler', 'Module', 'MetaModule',
    'get_db', 'get_state', 'set_state',
    ]

# scopes of singletons
_modules = {}
_metamodules = {}
_crawlers = {}

def declare(_class):
  def _declare_in(scope):
    assert _class.__name__ not in scope
    scope[_class.__name__] = _class()

  global _modules, _crawlers
  if issubclass(_class, Module):
    _declare_in(_modules)
  elif issubclass(_class, Crawler):
    _declare_in(_crawlers)
  else:
    assert False, f'Class {_class.__name__} is not stocklab.Module nor stocklab.Crawler'

def change_log_level(level):
  global log_level
  log_level = level

  _tmp = {}
  _tmp.update(_metamodules)
  _tmp.update(_modules)
  _tmp.update(_crawlers)
  for m in _tmp.values():
    m.logger.setLevel(level)

  if not init_flag:
    _init()

def _create_singleton(prefix, name):
  path = os.path.join(prefix, name + '.py')
  spec = importlib.util.spec_from_file_location(name, location=path)
  assert spec, f"stocklab module {name} not found."
  target_module = importlib.util.module_from_spec(spec)
  spec.loader.exec_module(target_module)
  singleton = getattr(target_module, name)()

  if isinstance(singleton, MetaModule):
    scope = _metamodules
  elif isinstance(singleton, Module):
    scope = _modules
  elif isinstance(singleton, Crawler):
    scope = _crawlers
  else:
    assert False, 'Should not reach here'
  scope[name] = singleton

def get_module(module_name):
  if not init_flag:
    _init()
  global _metamodules, _modules, modules_path
  if module_name in _metamodules:
    return _metamodules[module_name]
  elif module_name not in _modules:
    _create_singleton(modules_path, module_name)
  return _modules[module_name]

def get_crawler(crawler_name):
  if not init_flag:
    _init()
  global _crawlers, crawlers_path
  if crawler_name not in _crawlers:
    _create_singleton(crawlers_path, crawler_name)
  return _crawlers[crawler_name]

def _eval(path):
  if not init_flag:
    _init()
  assert '{' not in path
  assert '}' not in path
  mod = get_module(path.split('.')[0])
  return mod.evaluate(path)

def evaluate(path):
  if not init_flag:
    _init()
  global _logger
  _logger.info(f'evaluating: {path}')
  mod_name = path.split('.')[0]
  assert mod_name not in _metamodules
  return _eval(path)

import stocklab.utils
def _update(mod):
  if not stocklab.utils.is_outdated(mod.name):
    return
  with get_db() as db:
    last_args = None
    db.declare_table(mod.name, mod.spec['schema'])
    while True:
      update_required, crawl_args = mod.check_update(db, last_args)
      last_args = crawl_args
      if update_required:
        if stocklab.force_offline:
          raise NoLongerAvailable('Please unset' +\
              'force_offline option to enable crawlers')
        mod.logger.info('meta miss')
        res = mod.parser(**crawl_args)
        db.update(mod, res)
        stocklab.utils.set_last_update_datetime(mod.name)
      else:
        break

def metaevaluate(path):
  if not init_flag:
    _init()
  global _logger
  _logger.debug(f'evaluating: {path}')
  mod_name = path.split('.')[0]
  assert mod_name in _metamodules
  _update(get_module(mod_name))
  return _eval(path)

def _init():
  global init_flag
  init_flag = True

  global _logger
  _logger = create_logger('stocklab_core')

  for mc in os.listdir(modules_path):
    if mc[-3:] == '.py':
      m_name = mc[:-3]
      _create_singleton(modules_path, m_name)

  for m in _metamodules.keys():
    mod = _metamodules[m]
    _update(mod)
