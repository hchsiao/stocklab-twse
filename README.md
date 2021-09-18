# stocklab-twse
Toolkit for studying TWSE stocks

## Dependencies
```
conda install -c conda-forge ta-lib
```
See [TA-Lib](https://github.com/mrjbq7/ta-lib).
TODO: try [pyti](https://github.com/kylejusticemagnuson/pyti).

## TODO
- Write docstring
- Port old modules/crawlers
  - Refactor: `last_trade_date` is a state instead of a module
  - Refactor: `*_list` is states instead of modules
  - No transaction in the day -> an record w/ NULL prices will be added
  - d_last_date := (will be updated after market opened not after closed)
  - fix bug: init before mid-night (00:00), bug appears after mid-night (such as update conditions checking)
- Golden sign
  - Day gap to the next n% gain

## Features
- See the [ipython notebook](stocklab_demo.ipynb) or [colab notebook](https://colab.research.google.com/drive/1oeQcOgrTxnD3qSZDQU0Cf4gESqpV58cS?usp=sharing) to get an overview of what stocklab can do for you
- TODO: update notebooks
