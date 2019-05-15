from cryptotrader.api.kraken import Kraken
from cryptotrader.api.exceptions import APIError

from fake_useragent import UserAgent
from proxy_server import get_proxy_ips

import requests
import threading
import csv
import os
import time
import random

PROXY_URLS = None
PROXY_POOL = 5

def get_random_proxy_url():
	global PROXY_URLS
	refresh_proxy_url_list()
	ind = random.randint(0, len(PROXY_URLS)-1)
	return PROXY_URLS[ind]


def parse_proxy_url(url):
	return '%s:%s' % (url[0], url[1])


def refresh_proxy_url_list():
	global PROXY_URLS
	global PROXY_POOL
	# If the list of Proxy URLs is too small, refresh it.
	if len(PROXY_URLS) < 0.5*PROXY_POOL:
		PROXY_URLS = get_proxy_ips(limit=PROXY_POOL)


def scrape_trade_histories(writer):
	proxy_id = get_random_proxy_url()
	proxy_url = parse_proxy_url(proxy_id)
	user_agent = UserAgent().random
	print(proxy_url)
	kraken = Kraken(proxy=proxy_url, user_agent=user_agent)

	try:
		histories = kraken.get_market_trade_history('bch-usd', depth=50)
		writer.writerow(histories)
		print("%s: Writing Order Book Row" % time.time())
		print("[~] Proxy URL: %s. User Agent: %s." % (proxy_url, user_agent))
	except:
		print("[~] Error when request. Timing out for 10 seconds.")
		time.sleep(10)
		PROXY_URLS.remove(proxy_id)

	t = threading.Timer(1, scrape_trade_histories, args=(writer))
	t.setDaemon(True)
	t.start()


def scrape_order_book(writer):
	proxy_id = get_random_proxy_url()
	proxy_url = parse_proxy_url(proxy_id)
	user_agent = UserAgent().random
	kraken = Kraken(proxy=proxy_url, user_agent=user_agent)
	print("[~] proxy url: " % proxy_url)
	try:
		order_book = kraken.get_market_orders('bch-usd', depth=50)
		writer.writerow(order_book)
		print("%s: Writing Order Book Row" % time.time())
		print("[~] Proxy URL: %s. User Agent: %s." % (proxy_url, user_agent))
	except:
		print("[~] Error when request. Timing out for 10 seconds.")
		time.sleep(10)
		PROXY_URLS.remove(proxy_id)

	t = threading.Timer(1, scrape_order_book, args=(writer))
	t.setDaemon(True)
	t.start()


def main():
	# if not os.path.exists('/home/alex/2019/cryptobot/cryptobot/data/trade_histories.csv'):
	# 	os.makedirs('/home/alex/2019/cryptobot/cryptobot/data/trade_histories.csv')

	# if not os.path.exists('/home/alex/2019/cryptobot/cryptobot/data/order_book.csv'):
	# 	os.makedirs('/home/alex/2019/cryptobot/cryptobot/data/order_book.csv')
	global PROXY_URLS
	global PROXY_POOL

	PROXY_URLS = get_proxy_ips(limit=PROXY_POOL)

	history_file = open('/home/alex/2019/cryptobot/cryptobot/data/trade_histories.csv', 'w')
	order_book_file = open('/home/alex/2019/cryptobot/cryptobot/data/order_book.csv', 'w')
	
	h_writer = csv.writer(history_file, delimiter=',')
	o_writer = csv.writer(order_book_file, delimiter=',')

	scrape_order_book(h_writer)
	scrape_trade_histories(o_writer)

	while True:
		time.sleep(1000)


if __name__ == "__main__":
	main()