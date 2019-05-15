import pytest
from cryptotrader.api.kraken import Kraken
from cryptotrader.api.exceptions import APIError
from decimal import Decimal
import time


private = pytest.mark.skipif(
    not pytest.config.getoption("--apikey"),
    reason="needs --apikey option to run."
)

kraken = Kraken(pytest.config.getoption("--apikey"), 
                pytest.config.getoption("--secret"))

def test_outputs():
	print("=============================================")
	print("Kraken Get Markets")
	print("=============================================")
	print(kraken.get_markets())

	print("=============================================")
	print("Kraken Get order data")
	print("=============================================")
	print(kraken.get_market_trade_history('bch-usd'))


	assert False
