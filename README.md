## TODO
- implement time_to_crawl(datetime, db)
- grep -r 'TODO' .
- use pyDAL (refactor: grep -r 'get_db' .)
- maintain 'day_off' tab (stop trade for only few days)
- stocklab.evaluate cannot be invoked from a crawler
- transactions do not depend on twse, but invoked twse
- distrubute as bundles (stocklab_core, twse_bundle, ...), de-couple

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
- a single underscore in the expression means dont-care
