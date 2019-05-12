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
	print("Kraken Get OHLCV data")
	print("=============================================")
	print(kraken.get_market_ohlcv_data('bch-usd', 1, 21600))


	assert False
