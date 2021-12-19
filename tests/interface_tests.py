import unittest
import json
from utilities.okex_client import OkexClient

client = OkexClient(
    '3d2a7e66-45dd-446d-89ab-1f3ec614733a',
    '312D970B5F3B1F8E30550123BD2C5E0B',
    'nageRpyUpli1'
)


class MyTestCase(unittest.TestCase):
    def test_account_balance(self):
        resp = client.account_balance('BTC')
        print(resp)
        self.assertEqual(True, True)

    def test_market_tickers(self):
        resp = client.market_tickers()
        print(json.dumps(resp, indent=2))
        self.assertEqual(True, True)

    def test_config_models(self):
        from configs import settings
        print(settings)


if __name__ == '__main__':
    unittest.main()
