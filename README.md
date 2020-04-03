## TODO
- isolate stocklab-core

## TODO: Main objective (to predict)
- (exist/never) k-(higher/lower) than current price within N-days
- use this cheating info to perform simulation

## Intermediate objective
- tech. analysis
- price / vol. correlation
- time-frame quality (noisy or indicative)

## Metaevaluate
- metadata: known data in the dependency evaluation phase (e.g. valid_date)
- can be obtained by 1. ordinary evaluate or 2. metaevaluate
- internal id of stocks are not static

## Design choices
- No transaction in the day -> an record w/ NULL prices will be added
- do not care about ETF and the like
- stocklab expressions cannot contain curly-braces
- d_last_date := (will be updated after market opened not after closed)
- a single underscore in the expression means dont-care, otherwise expressions cannot start/end with underscore
