import stocklab

# At most possess one share (generalize: run policies in parallel)
def f(avg_price, date, stock_id):
  if avg_price is None:
    return 0
  else:
    return 999

# Another model: the objective is to minimize avg_price (not limit to owning 1 share)

def simulate(start_date, duration, stock_id):
  result = []
  avg_p = [None]
  dates = stocklab.metaevaluate(f'valid_dates.{start_date}.{duration}.lead')
  for d in range(duration):
    today = dates[d]
    min_price = stocklab.evaluate(f'twse.{stock_id}.{today}.min')
    max_price = stocklab.evaluate(f'twse.{stock_id}.{today}.max')
    target_price = f(avg_p[d], today, stock_id)
    buy = avg_p[d] is None
    sell = avg_p[d] is not None
    if buy and target_price >= min_price:
      result.append(-target_price)
      avg_p.append(target_price)
    elif sell and target_price <= max_price:
      result.append(target_price)
      avg_p.append(None)
    else:
      result.append(0)
      avg_p.append(avg_p[d])
  return result
