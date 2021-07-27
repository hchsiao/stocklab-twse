# stocklab-twse
Toolkit for studying TWSE stocks

## TODO
- Make the periodic crawler apart from stocklab (as one of utilities?)
  - Note: primitive & metamodules have a update method
    - not fresh if `!in_time_window(last_update_datetime, update_offset, update_period)`
    - primitive: update today's date for stocks in 'stock_of_interest'
    - metamodule: only run crawler_entry once (all modules will update at stocklab init)
  - Node: `peek()` cause the same crawler trigger as evaluate, but runs faster
- avoid
  - module `last_trade_date`
  - `*_list`

### Mid-term
- `import assets` should yield 'module not found'.
- Fix README
- Write docstring

## Features
- [Crawlers](crawlers/) are modularized so website-specific logic (e.g. speed limits, retry conditions) won't get messy
- [Modules](modules/), which represents an expression mapping, are modularized so un-related analysis tools can be easily decoupled
- See the [ipython notebook](stocklab_demo.ipynb) or [colab notebook](https://colab.research.google.com/drive/1oeQcOgrTxnD3qSZDQU0Cf4gESqpV58cS?usp=sharing) to get an overview of what stocklab can do for you

## Design choices
- No transaction in the day -> an record w/ NULL prices will be added
- do not care about ETF and the like
- d_last_date := (will be updated after market opened not after closed)

## Notes to myself
- TODO
  - make use of stock info
  - sign searcher (pre-built cache vs. ad-hoc search)
  - properly implement stock_types (w/ relational-map table)
  - improve caching
- Golden: a sign that peeking the future
  - e.g., exist price (higher/lower) than current price for certain amount within N-days
- Designing (verifying) a good sign
  - implement the idea
  - search for occurences
  - see if the sign coincide with some golden
  - tweak and iterate
- Be aware of variance between time-periods (noisy window vs. indicative window)
  - use financial healthiness to select window & stock

## Fast evaluation
### Motivation
Evaluate for each stock_id: naive DB access scattered in each loop is slow
### Solution
1. First solve dependencies of all primitive data in DB (e.g. transactions, open & close price)
2. Fetch them in once (if RAM size permits) as some data structure (numpy array?)
3. Compute 
