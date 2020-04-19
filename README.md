# stocklab-twse
Toolkit for studying TWSE stocks

## Notes to myself
- TODO
  - properly implement stock_types (w/ relational-map table)
  - random sampling
  - sign searcher
  - support float type in expression
- class stocklab.Sign(stocklab.Sequence): a module that returns [0,1]
  - tech. analysis
  - price / vol. correlation
- Golden: a sign that peeking the future
  - exist price (higher/lower) than current price for certain amount within N-days
- Designing (verifying) a good sign
  - implement the idea
  - search for occurences
  - see if the sign coincide with some golden
  - tweak and iterate
- Be aware of variance between time-periods (noisy window vs. indicative window)
  - use financial healthiness to select window & stock

## Design choices
- No transaction in the day -> an record w/ NULL prices will be added
- do not care about ETF and the like
- d_last_date := (will be updated after market opened not after closed)
