from cryptotrader.api.kraken import Kraken
from cryptotrader.api.exceptions import APIError
from cryptotrader.ingest.proxy_server import ProxyPool
from cryptotrader.utils.logger import Logger

from fake_useragent import UserAgent

import requests
import threading
import csv
import os
import time
import random
import logging
import asyncio
import argparse
import signal

global PROXY_POOL
global SCRAPE_FREQ


@Logger.logged
def scrape_trade_history(writer, target_pair, limit):
	global PROXY_POOL
	global SCRAPE_FREQ
	start = time.time()

	proxy_id = PROXY_POOL.get_random_proxy_id()
	proxy_url = PROXY_POOL.parse_proxy_id(proxy_id)

	user_agent = UserAgent().random
	logging.debug("Proxy URL: %s. User Agent: %s" % (proxy_url, user_agent))

	kraken = Kraken(proxy=proxy_url, user_agent=user_agent)

	# Initialize payload to garbage. While it is not of type list, keep trying. 
	payload = ""
	while type(payload) != list:
		try:
			logging.debug("Getting Market Trade History for pair: %s." % target_pair)
			payload = kraken.get_market_trade_history(target_pair, limit=50)
		except Exception as e:
			# Remove bad proxy from proxy list, grab a new proxy, and then try the call again.
			logging.error(e)
			PROXY_POOL.remove_bad_proxy(proxy_id)


			proxy_id = PROXY_POOL.get_random_proxy_id()
			proxy_url = PROXY_POOL.parse_proxy_id(proxy_id)
			logging.info("Fetching another Proxy URL: %s" % proxy_url)
			kraken = Kraken(proxy=proxy_url, user_agent=user_agent)

	logging.info("Writing trade history payload to file for target_pair: %s." % target_pair)
	writer.writerow([time.time(), target_pair, limit, 'trade_history', payload])
	end = time.time()
	elapsed_time = end-start
	logging.info("Time Elapsed: %0.4fs for %s history scraping event loop." % (elapsed_time, target_pair))
	
	# TODO: Implement better timer for more uniform time steps. 
	t = threading.Timer(SCRAPE_FREQ, scrape_trade_history, args=(writer,target_pair,limit))
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


# TODO: Need to change this potentially if we aren't going to be calling this file directly.
def _parse_args():
	parser = argparse.ArgumentParser(description="data_ingestion.py")
	parser.add_argument("--scrape_freq", default=1, help="Determines the frequency between ticks for each target pair.")
	parser.add_argument("--trade_history_depth", default=50, help="How many trade histories deep do we want to grab every scrape.")
	parser.add_argument("--order_book_depth", default=50, help="How many order levels do we want for each scrape.")
	parser.add_argument("--proxy_pool_size", default=100, help="Determines the size of the proxy pool to draw from is.")
	# parser.add_argument("--target_pairs" default="all", help='')
	args = parser.parse_args()
	return args


def main():
	# if not os.path.exists('/home/alex/2019/cryptobot/cryptobot/data/trade_histories.csv'):
	# 	os.makedirs('/home/alex/2019/cryptobot/cryptobot/data/trade_histories.csv')

	# if not os.path.exists('/home/alex/2019/cryptobot/cryptobot/data/order_book.csv'):
	# 	os.makedirs('/home/alex/2019/cryptobot/cryptobot/data/order_book.csv')
	global PROXY_POOL
	global SCRAPE_FREQ

	logging_level=logging.INFO
	logging_format='[~] %(asctime)s:%(levelname)s: %(message)s'
	logging_filename = './logs/ingest_logs.txt'

	Logger(level=logging_level,format=logging_format,filename=logging_filename)
	logging.basicConfig(level=logging_level,format=logging_format,filename=logging_filename)
	# loop = asyncio.get_event_loop()
	# TODO: Add support for multiple pairs. 

	args = _parse_args()
	logging.info("Args: %s" % args)
	PROXY_POOL = ProxyPool(pool_size=15)
	SCRAPE_FREQ=args.scrape_freq


	pairs = ['btc-usd', 'bch-usd', 'dash-usd', 'ltc-usd', 'eth-usd', 'xmr-usd', 'zec-usd', 'xrp-usd', 'ada-usd', 'eos-usd']
	file_map = {}
	# TODO: Figure out best way to handle file directory
	history_file = open('/home/alex/2019/cryptobot/cryptobot/data/trade_histories.csv', 'w')
	order_book_file = open('/home/alex/2019/cryptobot/cryptobot/data/order_book.csv', 'w')
	
	h_writer = csv.writer(history_file, delimiter=',')
	o_writer = csv.writer(order_book_file, delimiter=',')


	# scrape_order_book(o_writer)
	scrape_trade_history(h_writer, 'bch-usd', args.trade_history_depth)

	while True:
		try:
			signal.alarm(300)
			PROXY_POOL.refresh_proxy_url_list()
			time.sleep(120)
		except Exception as e:
			logging.error(e, exc_info=True)
			logging.error("Error when Refreshing Proxy URL List. Retrying...")
		else:
			logging.info("Refresh() finished in time. Resetting alarm...")
			signal.alarm(0)




if __name__ == "__main__":
	main()

		# try:
	# 	refresh_proxy_url_list()
	# 	proxy_id = get_random_proxy_url()
	# 	proxy_url = parse_proxy_url(proxy_id)
	# 	user_agent = UserAgent().random
	# 	print(proxy_url)
	# except Exception as e:
	# 	print("[~]Exception %s" % e)

	# kraken = Kraken(proxy=proxy_url, user_agent=user_agent)
	# try:
	# 	histories = kraken.get_market_orders('bch-usd', depth=50)
	# 	print("[~] Successfully retrieved Trade Histories")
	# 	writer.writerow([time.time(), 'bch-usd', 'trade_histories', histories])
	# 	print("%s: Writing Trade History Row" % time.time())
	# 	print("[~] Proxy URL: %s. User Agent: %s." % (proxy_url, user_agent))
	# except Exception as e:
	# 	print("[~] Error when request: %s" % e)
	# 	try:
	# 		print("Removing Proxy ID")
	# 		PROXY_URLS.remove(proxy_id)
	# 	except:
	# 		pass

	# t = threading.Timer(1, scrape_trade_histories, args=(writer,))
	# t.setDaemon(True)
	# t.start()

# ERROR STUFF

# # If the error is from read/connection timeout, it's ok. If it's a reset Error or 
# # connection closed/rejection, then remove it. 
# if check_bad_conn_error(e):
# 	logging.info("Removing Bad proxy")

# else:
# 	logging.info("Proxy Read Timeout -> Resuming...")
# @Logger.logged
# def check_bad_conn_error(error):
# 	e_str = str(error)
# 	if e_str.contains("Cannot connect"):
# 		return True
# 	elif e_str.contains("connect timeout"):
# 		return True
# 	elif e_str.contains("SSLError"):
# 		return True

# 	return True