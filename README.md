# stocklab-twse
- TODO
  - properly implement stock_types (w/ relational-map table)

## TODO: Main objective (to predict)
- (exist/never) k-(higher/lower) than current price within N-days
- use this cheating info to perform simulation

## Intermediate objective
- tech. analysis
- price / vol. correlation
- time-frame quality (noisy or indicative)

## Design choices
- No transaction in the day -> an record w/ NULL prices will be added
- do not care about ETF and the like
- d_last_date := (will be updated after market opened not after closed)
