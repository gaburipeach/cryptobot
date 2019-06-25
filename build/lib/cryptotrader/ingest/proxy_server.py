from proxybroker import Broker

import asyncio
import aiohttp
import random
import logging
import time
import traceback

# TODO: Look into expanding proxy types beyond just HTTPS and HTTP (SOCKS?)
# TODO: Do proxy refresh asynchronously


class ProxyPool(object):
    """
    This class creates a pool of proxies for use in distributed scraping. 

    Automatically handles pool resizing and addition/deletions. 
    """
    def __init__(self, pool_size=1):
        self.pool_size = pool_size
        # self.loop = event_loop
        self.proxy_set = set(self.get_proxy_ips(limit=self.pool_size))
        

    def get_proxy_ips(self, limit=1):
        # https://proxybroker.readthedocs.io/en/latest/examples.html#

        # NEED TO COMMENT OUT THE REMOVAL OF IP_CHECKERS IN LINE 90 OF 
        # resolver.py within the ProxyBroker Code! Otherwise, it will 
        # fail after doing the refresh.
        host, port = '127.0.0.1', 8888  # by default
        types = [('HTTP', 'High'), 'HTTPS', 'CONNECT:80']
        codes = [200, 301, 302]

        proxies = asyncio.Queue()
        broker = Broker(proxies, max_tries=2)
        new_list = []

        try:
            logging.info("Gathering proxies using ProxyBroker API")
            tasks = asyncio.gather(
                broker.find(types=['HTTP', 'HTTPS'], limit=limit),
                self.show(proxies, new_list))
            loop = asyncio.get_event_loop()
            logging.debug("Got Event Loop.")
            loop.run_until_complete(tasks)
            logging.info("Ran until complete.")
            broker.stop()
            logging.info("Broker Stopped Successfully.")
        except Exception as e:
            logging.error("Error encountered when collecting Proxies in get_proxy_ips().")
            logging.error(e, exc_info=True)

        return new_list


    async def show(self, proxies,ip_list):
        while True:
            proxy = await proxies.get()
            if proxy is None: break
            print('Found proxy: %s' % proxy)
            ip_list.append((proxy.host,proxy.port,proxy.schemes))
            # tasks.result()[1].host.port


    def get_random_proxy_id(self):
        return random.sample(self.proxy_set, 1)[0]


    def parse_proxy_id(self, url):
        # TODO: Need to change this to handle SOCKS protocol proxies
        if not url:
            return None

        scheme = url[2][0].lower()
        return "%s://%s:%s" % (scheme, url[0], url[1])


    def refresh_proxy_url_list(self):
        # If the list of Proxy URLs is too small, refresh it.
        if len(self.proxy_set) < 0.5*self.pool_size:
            logging.info("Refreshing Proxy URL List")
            logging.info("Proxy List length too small. Current Size: %d." % len(self.proxy_set))
            add_size = int(0.8*self.pool_size+1)
            try:
                logging.info("Adding %d new proxies." % add_size)
                # TODO: Figure out if this can be optimized (We want this to wait to minimize other thread's blocking)
                new_proxies = self.get_proxy_ips(limit=add_size)
                self.proxy_set.update(new_proxies)
                logging.info("New Proxy List Length: %d" % len(self.proxy_set))
            except Exception as e:
                logging.error("Error occured when trying to refresh proxy list.")
                logging.error(e, exc_info=True)


    def remove_bad_proxy(self, proxy_url):
        logging.info("Current proxy pool size: %d" % len(self.proxy_set))
        logging.info("Attempting to remove proxy from pool.")
        try:
            self.proxy_set.remove(proxy_url)
            logging.info("Proxy removed from pool successfully.")
            while len(self.proxy_set) < 1:
                logging.info("Attempting to add new Proxy to Pool...")
                # TODO: Find a better way to add an emergency proxy to the list. 
                # TODO: Currently, using the proxybroker library with threads is imcompatible.
                # TODO: The issue with using None as a proxy is that it might interfere with rate 
                #       limiting in the future with calls that require API keys (verifying book, executing orders) 
                # Elects to add an empty proxy server to the list when we run out of proxies.
                # self.proxy_set.add(None)
                logging.info("New Proxy Pool Size: %d" % len(self.proxy_set))
                logging.info("Added 1 new Proxy to Pool.")
                # TODO: Change
                break
        except Exception as e:
            # pass
            logging.error("Error occured when trying to remove proxy URL.")
            logging.error(e, exc_info=True)

        # TODO: Change this. Break out right now if we are under 1.
        if len(self.proxy_set) < 1:
            logging.error("Empty proxy list. Exiting...")
            raise Exception


    async def get_pages(self, urls, proxy_url):
        tasks = [self.fetch(url, proxy_url) for url in urls]
        for task in asyncio.as_completed(tasks):
            url, content = await task
            print('Done! url: %s; content: %.100s' % (url, content))


    async def fetch(self, url, proxy_url):
        resp = None
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, proxy=proxy_url) as response:
                    resp = await response.read()
        except (aiohttp.errors.ClientOSError, aiohttp.errors.ClientResponseError,
                aiohttp.errors.ServerDisconnectedError) as e:
            print('Error. url: %s; error: %r' % (url, e))
        finally:
            return (url, resp)




# def get_proxy_ips(limit=10):
#     host, port = '127.0.0.1', 8888  # by default
#     types = [('HTTP', 'High'), 'HTTPS', 'CONNECT:80']
#     codes = [200, 301, 302]

#     broker = Broker(max_tries=1)

#     proxies = asyncio.Queue()
#     broker = Broker(proxies)
#     new_list = []
#     tasks = asyncio.gather(
#         # broker.find(countries=['US'], types=['HTTPS'], limit=limit),
#         # show(proxies,new_list))
#         broker.find(types=['HTTP', 'HTTPS'], limit=limit),
#         show(proxies,new_list))

#     # Broker.serve() also supports all arguments that are accepted
#     # # Broker.find() method: data, countries, post, strict, dnsbl.
#     # broker.serve(host=host, port=port, types=types, limit=100, max_tries=3,
#     #              prefer_connect=True, min_req_proxy=5, max_error_rate=0.5,
#     #              max_resp_time=8, http_allowed_codes=codes, backlog=100)
#     #
#     #
#     # print(broker.find())
#     #
#     # # urls = ['http://httpbin.org/get', 'https://httpbin.org/get',
#     # #         'http://httpbin.org/redirect/1', 'http://httpbin.org/status/404']
#     # #
#     # # proxy_url = 'http://%s:%d' % (host, port)
#     # # loop.run_until_complete(get_pages(urls, proxy_url))
#     #
#     loop = asyncio.get_event_loop()
#     loop.run_until_complete(tasks)
#     broker.stop()
#     return new_list







# async def show(proxies,ip_list):
#     while True:
#         proxy = await proxies.get()
#         if proxy is None: break
#         print('Found proxy: %s' % proxy)
#         ip_list.append((proxy.host,proxy.port,proxy.schemes))
#         # tasks.result()[1].host.port



# def start_proxy_server():
#     host, port = '127.0.0.1', 8888  # by default
#     types = [('HTTP', 'High'), 'HTTPS', 'CONNECT:80']
#     codes = [200, 301, 302]

#     broker = Broker(max_tries=1)

#     # Broker.serve() also supports all arguments that are accepted
#     # # Broker.find() method: data, countries, post, strict, dnsbl.
#     broker.serve(host=host, port=port, types=types, limit=100, max_tries=1,
#                  prefer_connect=True, min_req_proxy=5, max_error_rate=0.5,
#                  max_resp_time=2, http_allowed_codes=codes, backlog=100)

#     #
#     # print(broker.find())
#     #
#     # # urls = ['http://httpbin.org/get', 'https://httpbin.org/get',
#     # #         'http://httpbin.org/redirect/1', 'http://httpbin.org/status/404']
#     # #
#     # # proxy_url = 'http://%s:%d' % (host, port)
#     # # loop.run_until_complete(get_pages(urls, proxy_url))
#     #

# if __name__ == '__main__':
#     start_proxy_server()
