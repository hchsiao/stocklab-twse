from datetime import datetime, timedelta
import stocklab
from stocklab.datetime import datetime_to_timestamp, now, update_required

def set_last_update_datetime(mod_name):
  tstmp = datetime_to_timestamp(now())
  stocklab.set_state(f'{mod_name}__t_last_update', str(tstmp))

def last_update_datetime(mod_name):
  t_last_update = stocklab.get_state(f'{mod_name}__t_last_update')
  if t_last_update:
    return datetime.utcfromtimestamp(int(t_last_update))
  else:
    return None

def is_outdated(mod_name):
  kwargs = {}
  if mod_name:
    spec = stocklab.get_module(mod_name).spec
    if 'update_offset' in spec:
      kwargs['offset'] = spec['update_offset']
    if 'update_period' in spec:
      kwargs['period'] = spec['update_period']

  last_update = last_update_datetime(mod_name)
  if last_update:
    return update_required(last_update, **kwargs)
  else:
    return True
