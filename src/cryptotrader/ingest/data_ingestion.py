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
PROXY_POOL = 50

def get_random_proxy_url():
	global PROXY_URLS
	ind = random.randint(0, len(PROXY_URLS)-1)
	return PROXY_URLS[ind]


def parse_proxy_url(url):
	return 'https://%s:%s' % (url[0], url[1])


def refresh_proxy_url_list():
	# TODO: incrementally add proxies to the list instead of one big add.
	global PROXY_URLS
	global PROXY_POOL
	# If the list of Proxy URLs is too small, refresh it.
	if len(PROXY_URLS) < 0.5*PROXY_POOL:
		print("[~] Refreshing Proxy List")
		PROXY_URLS.append(get_proxy_ips(limit=10))


def scrape_trade_histories(writer):
	try:
		refresh_proxy_url_list()
		proxy_id = get_random_proxy_url()
		proxy_url = parse_proxy_url(proxy_id)
		user_agent = UserAgent().random
		print(proxy_url)
	except Exception as e:
		print("[~]Exception %s" % e)

	kraken = Kraken(proxy=proxy_url, user_agent=user_agent)
	try:
		histories = kraken.get_market_orders('bch-usd', depth=50)
		print("[~] Successfully retrieved Trade Histories")
		writer.writerow([time.time(), 'bch-usd', 'trade_histories', histories])
		print("%s: Writing Trade History Row" % time.time())
		print("[~] Proxy URL: %s. User Agent: %s." % (proxy_url, user_agent))
	except Exception as e:
		print("[~] Error when request: %s" % e)
		try:
			print("Removing Proxy ID")
			PROXY_URLS.remove(proxy_id)
		except:
			pass

	t = threading.Timer(1, scrape_trade_histories, args=(writer,))
	t.setDaemon(True)
	t.start()


def scrape_order_book(writer):
	try:
		refresh_proxy_url_list()
		proxy_id = get_random_proxy_url()
		proxy_url = parse_proxy_url(proxy_id)
		user_agent = UserAgent().random
		print(proxy_url)
	except Exception as e:
		print("[~]Exception %s" % e)
	kraken = Kraken(proxy=proxy_url, user_agent=user_agent)
	try:
		order_book = kraken.get_market_orders('bch-usd', depth=50)
		print("[~] Successfully retrieved Order Book")
		writer.writerow([time.time(), 'bch-usd', 'order_book', order_book])
		print("%s: Writing Order Book Row" % time.time())
		print("[~] Proxy URL: %s. User Agent: %s." % (proxy_url, user_agent))
	except Exception as e:
		print("[~] Error when request: %s" % e)
		try:
			print("Removing Proxy ID")
			PROXY_URLS.remove(proxy_id)
		except:
			pass

	t = threading.Timer(1, scrape_order_book, args=(writer,))
	t.setDaemon(True)
	t.start()

o_file = None
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

	scrape_order_book(o_writer)
	scrape_trade_histories(h_writer)

	while True:
		time.sleep(1000)




if __name__ == "__main__":
	main()