# TODO: use notebook to substitute this file
import os
import stocklab
import stocklab_twse.data_bundle
import stocklab_twse.analysis_bundle

config_file = __file__.replace('main.py', 'config.yml')
stocklab.configure(config_file)

print(stocklab.eval('MovingAverage.date:20201208.stock:6533.window:5'))

from stocklab.core.bundle import get_crawler
crawler = get_crawler('TWSECrawler')
#print(crawler.stock_list())
#print(crawler.last_trade_date())
