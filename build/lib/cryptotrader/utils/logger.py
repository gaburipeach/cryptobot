import logging
import sys

"""Contains a function decorator for easy logging. Takes an argument 
that specifies the target file directory path. """

class Logger(object):
	def __init__(self, level, format, filename):
		logging.basicConfig(level=level, format=format, filename=filename)
		logging.info("Logging Initialized with Level %s" % level)


	@staticmethod
	def logged(func):
		def wrapper(*args, **kwargs):
			try:
				logging.debug("Started method '{0}' with arguments: {1} and keyword arguments: {2}.".format(func.__name__, args, kwargs))
				return func(*args, **kwargs)
			except Exception as e:
				logging.exception(e)
		return wrapper