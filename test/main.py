import os
import stocklab
import stocklab_twse.bundle

config_file = __file__.replace('main.py', 'config.yml')
stocklab.configure(config_file)

print(stocklab.eval('DateTrades.date:20201208'))
