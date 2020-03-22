import requests
import json
from bs4 import BeautifulSoup
import bs4

date = '20200306'
stock_id = '6666'

url = 'https://www.tdcc.com.tw/smWeb/QryStockAjax.do'

data = {'REQ_OPR': "qrySelScaDates"}
r = requests.post(url, data=data)
dates = json.loads(r.text)

data = {
    'scaDates': date,
    'scaDate': date,
    'SqlMethod': "StockNo",
    'StockNo': stock_id,
    'radioStockNo': stock_id,
    'StockName': "",
    'REQ_OPR': "SELECT",
    'clkStockNo': stock_id,
    'clkStockName': "",
    }
r = requests.post(url, data=data)

def parse(body):
  soup = BeautifulSoup(body, 'html.parser')
  tab = soup.find_all(class_='mt')[1].tbody.contents
  retval = []
  for row in tab:
    if isinstance(row, bs4.element.Tag):
      r_ = [e.contents[0] for e in row if isinstance(e, bs4.element.Tag)]
      if len(r_) == 5:
        _no, _range, _n_person, _n_share, _perc = r_
        retval.append((_range, _n_person, _n_share))
  if len(retval) > 1:
    return retval[1:-1]
  else:
    return []

print(parse(r.content))
