import json
from stocklab import DataIdentifier as DI
from stocklab_twse.utils import state, datetime
from datetime import datetime as pydt

def update_today():
    def set_last_update_datetime(name):
        tstmp = datetime.datetime_to_timestamp(datetime.now())
        state.set(f'{name}__t_last_update', str(tstmp))
      
    def get_last_update_datetime(name):
        t_last_update = state.get(f'{name}__t_last_update')
        if t_last_update:
            return pydt.utcfromtimestamp(int(t_last_update))
        else:
            return None
      
    def is_outdated(name, offset=0, period=(1, 0, 0)):
        last_update = get_last_update_datetime(name)
        if last_update:
            return not datetime.in_time_window(last_update, offset, period)
        else:
            return True

    if is_outdated('stock_list', offset=(13, 40), period=(1,0,0)):
        print(f'Updating stock_list...')
        stock_list = ['2330', '6533'] # TODO: fetch the list from crawler
        state.set('stock_list', json.dumps(stock_list))
        set_last_update_datetime('stock_list')

    def db_is_fresh(name, db, stock_list):
        stock_count = len(stock_list)
        table = db[name]
        query = table.date == datetime.Date.today().timestamp()
        todays_count = len(db(query).select(table.stock_id, distinct=True))

        assert not todays_count > stock_count
        if todays_count == stock_count:
            set_last_update_datetime(name)
            return True
        else:
            return False

    stock_list = json.loads(state.get('stock_list'))
    primitive = DI('DailyData')
    if is_outdated(primitive.name, offset=(13, 40), period=(1,0,0)):
        from stocklab.db import get_db
        from stocklab_twse.error import InvalidDateRequested
        with get_db('database') as db:
            db.declare_table(primitive.name, primitive.schema)
            if not db_is_fresh(primitive.name, db, stock_list):
                print(f'Updating {primitive.name}...')
                today = datetime.Date.today()
                try:
                    for s in stock_list:
                        primitive(stock=s, date=today)
                except InvalidDateRequested:
                    print(f'Today ({today}) is not trade date')
                else:
                    set_last_update_datetime(primitive.name)
