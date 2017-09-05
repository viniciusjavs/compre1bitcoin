from time import time
from requests import get
from fractions import Fraction
from decimal import Decimal
from babel import numbers

def timestamp():
    '''
    returns epoch time in milliseconds
    '''
    return str(int(time()*1000))

def getMeta():
    '''
    request information about order book
    returns dict with keys: order_book_prefix, current_round, order_book_pages
    '''
    api_url_meta = ('https://s3.amazonaws.com/data-production-walltime-info/production/dynamic/meta.json?now='
                    + timestamp())
    meta = get(api_url_meta)
    if meta.status_code != 200:
        raise RuntimeError('Bad request')
    return meta.json()

def toFraction(pair):
    '''
    receives a pair of numbers (numerator/denominator)
    returns its Fraction equivalent
    '''
    pair = pair.split('/')
    if len(pair) == 1:
        return Fraction(Decimal(pair[0]))
    else:
        num=Decimal(pair[0])
        den=Decimal(pair[1])
        return Fraction (num/den);

def fetchOrderBookPage(meta, page):
    '''
    fetch order book page
    return list with order book xbt-brl (selling)
    '''
    order_book_prefix = str(meta['order_book_prefix'])
    current_round = str(meta['current_round'])
    order_book_pages = meta['order_book_pages']
    assert page <= order_book_pages
    api_url= ('https://s3.amazonaws.com/data-production-walltime-info/production/dynamic/'
              + order_book_prefix
              + '_r' + current_round
              + '_p' + str(page)
              + '.json?now=' + timestamp())
    order_book = get(api_url)
    if order_book.status_code != 200:
        raise RuntimeError('Bad request')   
    order_book = order_book.json()
    return order_book['xbt-brl']

def sweepPage(order_book_selling, total):
    '''
    trying reach a given BTC value, per page
    return Boolean
    '''
    for order in order_book_selling:
        xbt = toFraction(order[0]) # amount of BTC for sale
        brl = toFraction(order[1]) # amount of BRL needed
        if (xbt < total['btc']):
            total['btc'] -= xbt
            total['brl'] += brl
        else:
            total['brl'] += (total['btc'] * brl) / xbt
            return True
    return False

def buyFullBTC():
    '''
    trying reach a given BTC value, sweep order book
    return BTC value in BRL or 'Order currently unavailable'
    '''
    try:
        meta = getMeta()
        total = {'btc': 1, 'brl': 0}
        order_book_pages = meta['order_book_pages']
        for page in range(0,order_book_pages):
            order_book_selling = fetchOrderBookPage(meta, page)
            if sweepPage(order_book_selling, total):
                return numbers.format_currency(float(total['brl']), 'BRL', locale='pt_BR')
        return 'Order currently unavailable'
    except Exception as e:
        return 'Error: ' + str(e)
