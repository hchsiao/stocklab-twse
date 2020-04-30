# stocklab-twse
Toolkit for studying TWSE stocks

## Notes to myself
- TODO
  - failed to raise log level
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

## Design choices
- No transaction in the day -> an record w/ NULL prices will be added
- do not care about ETF and the like
- d_last_date := (will be updated after market opened not after closed)
