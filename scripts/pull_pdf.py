import tabula
import requests
from bs4 import BeautifulSoup
import bs4
import pdfplumber
import time

#TODO: https://stackoverflow.com/questions/28667684/python-requests-getting-sslerror

def pull(stock_id, filename):
  r = requests.post('https://doc.twse.com.tw/server-java/t57sb01', data = {
      "colorchg": 1,
      "step": 9,
      "kind": 'A',
      "co_id": str(stock_id),
      "filename": filename,
  })
  
  if r.headers['Content-type'] == 'application/msword':
    print(f'downloaded {filename}')
    open(f'tmp/{filename}', 'wb').write(r.content)
    time.sleep(10)
    return
  elif r.headers['Content-type'] == 'application/x-zip-compressed':
    print(f'downloaded {filename}')
    open(f'tmp/{filename}', 'wb').write(r.content)
    time.sleep(10)
    return
  assert 'text/html' in r.headers['Content-type'], r.headers
  time.sleep(3)

  soup = BeautifulSoup(r.text, 'html.parser')
  
  links = [a for a in soup.find_all('a') if filename in a]
  if len(links) == 1:
    link = links[0].get('href')
    link = 'https://doc.twse.com.tw' + link
    print(f'downloading {link}')
    r = requests.get(link)
    open(f'tmp/{filename}', 'wb').write(r.content)
    time.sleep(10)
  else:
    print(filename, r.text)

def crawl(stock_id, year):
  url = f'https://doc.twse.com.tw/server-java/t57sb01?step=1&colorchg=1&co_id={stock_id}&year={year}&seamon=&mtype=A'
  print(url)
  r = requests.get(url)
  time.sleep(5)
  soup = BeautifulSoup(r.content, 'html.parser')
  if not soup.table:
    print('not found')
    exit()
  tab = [r for r in soup.table.contents if len(r) > 1][0]
  retval = []
  for row in tab:
    cols = [col.contents[0] for col in row if type(col) is bs4.element.Tag]
    if cols:
      retval.append(cols)
  h = retval[0]
  e = retval[1:]
  retval = [{h[i]: row[i] for i in range(len(h))} for row in e]
  for f in retval:
    target = None
    if f['資料細節說明'] == 'IFRSs個體財報':
      target = f['電子檔案']
    if f['資料細節說明'] == '母公司財報' and '第四季' in f['資料年度']:
      target = f['電子檔案']
    if target:
      filename = target.contents[0]
      pull(stock_id, filename)

listing = [2323, 2406, 2349, 8053]
for y in range(103, 105):
  for sid in listing:
    crawl(sid, y)
