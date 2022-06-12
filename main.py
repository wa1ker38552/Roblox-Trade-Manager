from colors import *
import requests
import os


cookie = os.environ['COOKIE']

def index_segment(text, start, i):
  x = start = text.index(start)+len(start)
  while text[x] != i: x += 1
  return text[start:x]

def refresh_xcsrf():
  global cookie
  with requests.Session() as session:
    session.cookies['.ROBLOSECURITY'] = cookie
    response = session.post('https://auth.roblox.com/v1/login')
    if "X-CSRF-TOKEN" in response.headers:
      return response.headers["X-CSRF-TOKEN"]

def get_trades_list(limit=10):
  global cookie, xcsrf
  request = requests.get(f'https://trades.roblox.com/v1/trades/Inbound?sortOrder=Asc&limit={limit}', 
                         cookies={".ROBLOSECURITY": cookie}, headers={'x-csrf-token': xcsrf})
  return request.json()['data']

def get_trade(id, trades_page):
  global cookie, xcsrf
  trade = {'offer': {}, 'request': {}}
  request = requests.get(f'https://trades.roblox.com/v1/trades/{id}',
                         cookies={".ROBLOSECURITY": cookie}, headers={'x-csrf-token': xcsrf})
  items = ['offer', 'request']
  for i in range(2):
    for index, item in enumerate(request.json()['offers'][i]['userAssets']):
      hat = get_item_value(item['assetId'], trades_page)
      trade[items[i]][str(index)] = {
        'item': item['name'],
        'rap': item['recentAveragePrice'],
        'serial': item['serialNumber'],
        'id': item['assetId'],
        'value': int(hat[0]),
        'projected': True if hat[1] == 1 else False
      }
  return trade

def get_item_value(id, page):
  try:
    item = page['items'][str(id)]
  except KeyError:
    print(page)
  if item[3] < 0:
    return [item[2], item[7]]
  else:
    return [item[3], item[7]]


if __name__ == '__main__':
  os.system('clear')
  xcsrf = refresh_xcsrf()
  trades = get_trades_list()
  trades_page = requests.get('https://rolimons.com/itemapi/itemdetails').json()
  
  for trade in trades:
    t = get_trade(trade['id'], trades_page)
    offering_value, offering_rap = 0, 0
    request_value, request_rap = 0, 0
    offering_projected = ''
    request_projected = ''
    for item in t['offer']:
      offering_rap += t['offer'][item]['rap']
      offering_value += t['offer'][item]['value']
      if t['offer'][item]['projected'] is True:
        offering_projected = '🔺'
    for item in t['request']:
      request_rap += t['request'][item]['rap']
      request_value += t['request'][item]['value']
      if t['request'][item]['projected'] is True:
        request_projected = '🔺'
    value_win = green if offering_value < request_value else red
    rap_win = green if offering_rap < request_rap else red
    rap_win_amount = request_rap - offering_rap
    value_win_amount = request_value - offering_value
    print(f'Offering: {rap_win}{offering_rap}{white} RAP and {value_win}{offering_value}{white} value {bright_yellow}{offering_projected}{white}')
    print(f'Requesting: {rap_win}{request_rap}{white} RAP and {value_win}{request_value}{white} value {bright_yellow}{request_projected}{white}')
    print(f'Rap win: {rap_win}{rap_win_amount}{white}')
    print(f'Value win: {value_win}{value_win_amount}{white}\n')
