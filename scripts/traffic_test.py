import requests
import json
import time

# Conclusion: max speed = 0.4t/s, timeout = 25/0.4 = 62.5s

#25 23.920793771743774 1.0451158200916824 {"ip":"34.73.113.180"}
#25 16.530459880828857 1.5123596185605013 {"ip":"34.83.55.199"}
#25 27.927971363067627 0.8951598981177837
#26 55.827882051467896 0.46571711203427923

#36 185.02512073516846 0.19456817461844972
#28 73.89545559883118 0.378913693313001
#80 294.69613766670227 0.27146606207129537
#33 104.57965278625488 0.31554895355645374
#29 79.92620182037354 0.3628347067608031

try:
  start_time = time.time()
  for i in range(1000000):
    date = '20200219'
    # limited
    url = f'https://www.twse.com.tw/exchangeReport/STOCK_DAY?'\
            + 'response=json&date={date}&stockNo=2330'
    r = requests.get(url) # may throw error
    page = r.text
    json.loads(page) # may throw error

    elapsed_time = time.time() - start_time
    speed = float(i+1) / elapsed_time
    while speed > 0.4:
      time.sleep(0.01)
      elapsed_time = time.time() - start_time
      speed = float(i+1) / elapsed_time
    if 0 == i%1:
      print(i+1, speed)
except requests.exceptions.ConnectionError as e:
  if 'Connection aborted' in str(e):
    print('Connection error, waiting for retry...')
  else:
    print(f'unexpected error {e}')
except json.decoder.JSONDecodeError as e:
  if 'Expecting value' in str(e):
    print('Too many requests? waiting for retry...')
  else:
    print(f'unexpected error {e}')
finally:
  elapsed_time = time.time() - start_time
  print(i, elapsed_time, i / elapsed_time)
